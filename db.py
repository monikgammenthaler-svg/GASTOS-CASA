import psycopg2
import psycopg2.extras
import streamlit as st
from datetime import date

CATEGORIAS = [
    "Super - TICKETS",
    "Super",
    "Feria",
    "Compras generales",
    "Almuerzos / Salidas",
    "Transporte",
    "Panadería",
    "Farmacia",
    "Ropa / Calzado",
    "Servicios",
    "Otros",
]

TARJETAS = [
    "OCA VISA (compartida)",
    "OCA MONI",
    "OCA GUILLE",
    "BROU MONI",
    "BROU GUILLE",
    "ITAU MONI",
    "ITAU GUILLE",
]

TIPOS_PAGO = ["Débito", "Crédito", "Efectivo"]
PERSONAS   = ["Persona 1", "Persona 2"]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

CATEGORIAS_PENDIENTES = ["Supermercado", "Limpieza", "Farmacia", "Ropa", "Hogar", "Trámite", "Otro"]
PRIORIDADES = ["Alta", "Normal", "Baja"]
CATEGORIAS_PERSONAL = [
    "Ropa / Calzado", "Capricho", "Salud / Belleza", "Entretenimiento",
    "Suscripciones", "Comidas", "Transporte", "Ahorro personal", "Otros",
]


@st.cache_resource
def _db():
    url = st.secrets["supabase"]["db_url"]
    return {"url": url, "conn": psycopg2.connect(url)}


def get_conn():
    d = _db()
    if d["conn"].closed:
        d["conn"] = psycopg2.connect(d["url"])
    return d["conn"]


def _invalidar():
    """Limpia todo el caché de datos después de cualquier escritura."""
    st.cache_data.clear()


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos_variables (
            id SERIAL PRIMARY KEY,
            fecha TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            pagado_por TEXT NOT NULL,
            comentarios TEXT,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos_fijos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            valor REAL NOT NULL,
            activo INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS compras_tarjeta (
            id SERIAL PRIMARY KEY,
            detalle TEXT NOT NULL,
            valor REAL NOT NULL,
            cuotas INTEGER NOT NULL DEFAULT 1,
            valor_cuota REAL NOT NULL,
            moneda TEXT DEFAULT '$',
            comentarios TEXT,
            fecha_compra TEXT,
            mes_primera_cuota TEXT,
            tarjeta TEXT,
            pagado_por TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pendientes (
            id SERIAL PRIMARY KEY,
            descripcion TEXT NOT NULL,
            categoria TEXT DEFAULT 'General',
            prioridad TEXT DEFAULT 'Normal',
            asignado_a TEXT DEFAULT 'Ambos',
            completado INTEGER DEFAULT 0,
            fecha_creacion TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos_fijos_excluidos (
            id SERIAL PRIMARY KEY,
            mes TEXT NOT NULL,
            gasto_id INTEGER NOT NULL,
            UNIQUE(mes, gasto_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos_personales (
            id SERIAL PRIMARY KEY,
            fecha TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            persona TEXT NOT NULL,
            monto REAL NOT NULL,
            comentarios TEXT
        )
    """)

    c.execute("ALTER TABLE gastos_fijos ADD COLUMN IF NOT EXISTS pagado_por TEXT DEFAULT 'Moni'")
    c.execute("ALTER TABLE gastos_variables ADD COLUMN IF NOT EXISTS casa_id INTEGER DEFAULT 1")
    c.execute("ALTER TABLE gastos_fijos ADD COLUMN IF NOT EXISTS casa_id INTEGER DEFAULT 1")
    c.execute("ALTER TABLE compras_tarjeta ADD COLUMN IF NOT EXISTS casa_id INTEGER DEFAULT 1")
    c.execute("ALTER TABLE pendientes ADD COLUMN IF NOT EXISTS casa_id INTEGER DEFAULT 1")
    c.execute("ALTER TABLE gastos_personales ADD COLUMN IF NOT EXISTS casa_id INTEGER DEFAULT 1")

    c.execute("SELECT COUNT(*) FROM gastos_fijos WHERE casa_id=1")
    if c.fetchone()[0] == 0:
        fijos_default = [
            ("UTE", 0), ("Alquiler", 0), ("IVA Alquiler", 0),
            ("Prima por alquiler", 0), ("Cuota social ANDA", 0),
            ("Impuestos", 0), ("Gastos comunes", 0),
            ("Ahorro BHU", 0), ("Antel", 0),
        ]
        c.executemany("INSERT INTO gastos_fijos (nombre, valor, casa_id) VALUES (%s, %s, 1)", fijos_default)

    conn.commit()


# ── Gastos variables ─────────────────────────────────────────────────

def agregar_gasto(fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto, casa_id=1):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO gastos_variables (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto, casa_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto, casa_id),
    )
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_gastos_mes(anio, mes, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT id, fecha, categoria, descripcion, pagado_por, tipo, monto, comentarios FROM gastos_variables WHERE fecha LIKE %s AND casa_id=%s ORDER BY fecha DESC",
        (f"{prefijo}%", casa_id),
    )
    return c.fetchall()

def agregar_gasto_en_cuotas(fecha_base, categoria, descripcion, pagado_por, tipo, tarjeta, monto_total, num_cuotas, casa_id=1):
    import calendar
    from datetime import datetime as dt
    valor_cuota = round(monto_total / num_cuotas, 0)
    if isinstance(fecha_base, str):
        fecha_base = dt.strptime(fecha_base, "%Y-%m-%d").date()
    conn = get_conn()
    c = conn.cursor()
    for i in range(num_cuotas):
        mes = (fecha_base.month - 1 + i) % 12 + 1
        anio = fecha_base.year + (fecha_base.month - 1 + i) // 12
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        dia = min(fecha_base.day, ultimo_dia)
        fecha_cuota = date(anio, mes, dia)
        desc = f"{descripcion} (cuota {i+1}/{num_cuotas})"
        comentario = f"Tarjeta: {tarjeta}" if tarjeta else ""
        c.execute(
            "INSERT INTO gastos_variables (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto, casa_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (str(fecha_cuota), categoria, desc, pagado_por, comentario, tipo, valor_cuota, casa_id),
        )
    conn.commit()
    _invalidar()

def eliminar_gasto(gasto_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM gastos_variables WHERE id = %s", (gasto_id,))
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_totales_mes(anio, mes, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT pagado_por, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s AND casa_id=%s GROUP BY pagado_por",
        (f"{prefijo}%", casa_id),
    )
    return dict(c.fetchall())

@st.cache_data(ttl=60)
def get_por_categoria_mes(anio, mes, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT categoria, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s AND casa_id=%s GROUP BY categoria ORDER BY SUM(monto) DESC",
        (f"{prefijo}%", casa_id),
    )
    return c.fetchall()

@st.cache_data(ttl=60)
def get_por_tipo_mes(anio, mes, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT tipo, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s AND casa_id=%s GROUP BY tipo",
        (f"{prefijo}%", casa_id),
    )
    return c.fetchall()


# ── Gastos fijos ─────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_gastos_fijos(casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, nombre, valor, activo, pagado_por FROM gastos_fijos WHERE activo=1 AND casa_id=%s ORDER BY id", (casa_id,))
    return c.fetchall()

def actualizar_gasto_fijo(gasto_id, valor):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET valor=%s WHERE id=%s", (valor, gasto_id))
    conn.commit()
    _invalidar()

def actualizar_pagador_fijo(gasto_id, pagado_por):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET pagado_por=%s WHERE id=%s", (pagado_por, gasto_id))
    conn.commit()
    _invalidar()

def agregar_gasto_fijo(nombre, valor, casa_id=1):
    conn = get_conn()
    conn.cursor().execute("INSERT INTO gastos_fijos (nombre, valor, casa_id) VALUES (%s, %s, %s)", (nombre, valor, casa_id))
    conn.commit()
    _invalidar()

def desactivar_gasto_fijo(gasto_id):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET activo=0 WHERE id=%s", (gasto_id,))
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_fijos_excluidos_mes(anio, mes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT gasto_id FROM gastos_fijos_excluidos WHERE mes=%s", (f"{anio}-{mes:02d}",))
    return frozenset(row[0] for row in c.fetchall())

def toggle_fijo_excluido(anio, mes, gasto_id):
    mes_str = f"{anio}-{mes:02d}"
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM gastos_fijos_excluidos WHERE mes=%s AND gasto_id=%s", (mes_str, gasto_id))
    if c.fetchone():
        c.execute("DELETE FROM gastos_fijos_excluidos WHERE mes=%s AND gasto_id=%s", (mes_str, gasto_id))
    else:
        c.execute("INSERT INTO gastos_fijos_excluidos (mes, gasto_id) VALUES (%s,%s)", (mes_str, gasto_id))
    conn.commit()
    _invalidar()


# ── Compras con tarjeta ───────────────────────────────────────────────

def agregar_compra_tarjeta(detalle, valor, cuotas, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por, casa_id=1):
    valor_cuota = round(valor / cuotas, 2)
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO compras_tarjeta (detalle, valor, cuotas, valor_cuota, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por, casa_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (detalle, valor, cuotas, valor_cuota, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por, casa_id),
    )
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_compras_tarjeta(casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, detalle, valor, cuotas, valor_cuota, moneda, mes_primera_cuota, tarjeta, pagado_por, comentarios, fecha_compra FROM compras_tarjeta WHERE casa_id=%s ORDER BY id DESC",
        (casa_id,),
    )
    return c.fetchall()

def eliminar_compra_tarjeta(compra_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM compras_tarjeta WHERE id=%s", (compra_id,))
    conn.commit()
    _invalidar()

def _parse_mes_cuota(mes_primera, anio_fallback=None):
    if not mes_primera:
        return None, None
    partes = mes_primera.strip().split()
    if len(partes) == 2 and partes[0] in MESES:
        try:
            return MESES.index(partes[0]) + 1, int(partes[1])
        except ValueError:
            pass
    mes_num = anio = None
    for p in partes:
        if p.capitalize() in MESES and mes_num is None:
            mes_num = MESES.index(p.capitalize()) + 1
        try:
            y = int(p)
            if 2020 <= y <= 2035:
                anio = y
        except ValueError:
            pass
    if mes_num is not None:
        return mes_num, anio if anio is not None else anio_fallback
    return None, None

@st.cache_data(ttl=60)
def get_total_oca_compartida_mes(anio, mes, casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT detalle, valor_cuota, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE tarjeta = 'OCA VISA (compartida)' AND casa_id=%s",
        (casa_id,),
    )
    compras = c.fetchall()
    total = 0.0
    detalle_items = []
    for detalle, valor_cuota, n_cuotas, mes_primera in compras:
        mes_inicio, anio_inicio = _parse_mes_cuota(mes_primera, anio_fallback=anio)
        if mes_inicio is None or anio_inicio is None:
            continue
        inicio  = anio_inicio * 12 + mes_inicio
        fin     = inicio + n_cuotas - 1
        actual  = anio * 12 + mes
        if inicio <= actual <= fin:
            total += valor_cuota
            detalle_items.append((detalle, valor_cuota, actual - inicio + 1, n_cuotas))
    return total, detalle_items

@st.cache_data(ttl=60)
def get_total_cuotas_activas_mes(anio, mes, casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT pagado_por, tarjeta, detalle, valor_cuota, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE tarjeta != 'OCA VISA (compartida)' AND casa_id=%s",
        (casa_id,),
    )
    compras = c.fetchall()
    totales = {}
    detalle_items = []
    for pagado_por, tarjeta, detalle, valor_cuota, n_cuotas, mes_primera in compras:
        mes_inicio, anio_inicio = _parse_mes_cuota(mes_primera, anio_fallback=anio)
        if mes_inicio is None or anio_inicio is None:
            continue
        inicio  = anio_inicio * 12 + mes_inicio
        fin     = inicio + n_cuotas - 1
        actual  = anio * 12 + mes
        if inicio <= actual <= fin:
            cuota_num = actual - inicio + 1
            totales[pagado_por] = totales.get(pagado_por, 0) + valor_cuota
            detalle_items.append((pagado_por, tarjeta, detalle, valor_cuota, cuota_num, n_cuotas))
    return totales, detalle_items


# ── Pendientes ────────────────────────────────────────────────────────

def agregar_pendiente(descripcion, categoria, prioridad, asignado_a, casa_id=1):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO pendientes (descripcion, categoria, prioridad, asignado_a, fecha_creacion, casa_id) VALUES (%s,%s,%s,%s,%s,%s)",
        (descripcion, categoria, prioridad, asignado_a, str(date.today()), casa_id),
    )
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_pendientes(solo_activos=True, casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    filtro = "AND completado=0" if solo_activos else ""
    c.execute(
        f"SELECT id, descripcion, categoria, prioridad, asignado_a, completado, fecha_creacion FROM pendientes WHERE casa_id=%s {filtro} ORDER BY CASE prioridad WHEN 'Alta' THEN 1 WHEN 'Normal' THEN 2 ELSE 3 END, id",
        (casa_id,),
    )
    return c.fetchall()

def marcar_pendiente(pendiente_id, completado):
    conn = get_conn()
    conn.cursor().execute("UPDATE pendientes SET completado=%s WHERE id=%s", (1 if completado else 0, pendiente_id))
    conn.commit()
    _invalidar()

def eliminar_pendiente(pendiente_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM pendientes WHERE id=%s", (pendiente_id,))
    conn.commit()
    _invalidar()

def actualizar_pendiente(pendiente_id, descripcion):
    conn = get_conn()
    conn.cursor().execute("UPDATE pendientes SET descripcion=%s WHERE id=%s", (descripcion, pendiente_id))
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_cuotas_del_mes(anio, mes_num, casa_id=1):
    nombre_mes = MESES[mes_num - 1]
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, detalle, valor_cuota, moneda, tarjeta, pagado_por, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE mes_primera_cuota=%s AND casa_id=%s",
        (f"{nombre_mes} {anio}", casa_id),
    )
    return c.fetchall()


# ── Gastos personales ─────────────────────────────────────────────────

def agregar_gasto_personal(fecha, categoria, descripcion, persona, monto, comentarios, casa_id=1):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO gastos_personales (fecha, categoria, descripcion, persona, monto, comentarios, casa_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (fecha, categoria, descripcion, persona, monto, comentarios, casa_id),
    )
    conn.commit()
    _invalidar()

@st.cache_data(ttl=60)
def get_gastos_personales_mes(anio, mes, persona, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT id, fecha, categoria, descripcion, monto, comentarios FROM gastos_personales WHERE fecha LIKE %s AND persona=%s AND casa_id=%s ORDER BY fecha DESC",
        (f"{prefijo}%", persona, casa_id),
    )
    return c.fetchall()

@st.cache_data(ttl=60)
def get_total_personal_mes(anio, mes, persona, casa_id=1):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT COALESCE(SUM(monto),0) FROM gastos_personales WHERE fecha LIKE %s AND persona=%s AND casa_id=%s",
        (f"{prefijo}%", persona, casa_id),
    )
    return c.fetchone()[0]

def eliminar_gasto_personal(gasto_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM gastos_personales WHERE id=%s", (gasto_id,))
    conn.commit()
    _invalidar()
