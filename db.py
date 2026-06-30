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
PERSONAS   = ["Moni", "Guille"]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

CATEGORIAS_PENDIENTES = ["Supermercado", "Limpieza", "Farmacia", "Ropa", "Hogar", "Trámite", "Otro"]
PRIORIDADES = ["Alta", "Normal", "Baja"]


@st.cache_resource
def _db():
    url = st.secrets["supabase"]["db_url"]
    return {"url": url, "conn": psycopg2.connect(url)}


def get_conn():
    db = _db()
    if db["conn"].closed:
        db["conn"] = psycopg2.connect(db["url"])
    try:
        cur = db["conn"].cursor()
        cur.execute("SELECT 1")
        cur.close()
    except Exception:
        try:
            db["conn"].close()
        except Exception:
            pass
        db["conn"] = psycopg2.connect(db["url"])
    return db["conn"]


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

    c.execute("ALTER TABLE gastos_fijos ADD COLUMN IF NOT EXISTS pagado_por TEXT DEFAULT 'Moni'")

    # Gastos fijos por defecto si la tabla está vacía
    c.execute("SELECT COUNT(*) FROM gastos_fijos")
    if c.fetchone()[0] == 0:
        fijos_default = [
            ("UTE", 0), ("Alquiler", 0), ("IVA Alquiler", 0),
            ("Prima por alquiler", 0), ("Cuota social ANDA", 0),
            ("Impuestos", 0), ("Gastos comunes", 0),
            ("Ahorro BHU", 0), ("Antel", 0),
        ]
        c.executemany("INSERT INTO gastos_fijos (nombre, valor) VALUES (%s, %s)", fijos_default)

    conn.commit()

# --- Gastos variables ---

def agregar_gasto(fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO gastos_variables (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto),
    )
    conn.commit()

def get_gastos_mes(anio, mes):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT id, fecha, categoria, descripcion, pagado_por, tipo, monto, comentarios FROM gastos_variables WHERE fecha LIKE %s ORDER BY fecha DESC",
        (f"{prefijo}%",),
    )
    rows = c.fetchall()
    return rows


def agregar_gasto_en_cuotas(fecha_base, categoria, descripcion, pagado_por, tipo, tarjeta, monto_total, num_cuotas):
    import calendar
    from datetime import datetime
    valor_cuota = round(monto_total / num_cuotas, 0)
    if isinstance(fecha_base, str):
        fecha_base = datetime.strptime(fecha_base, "%Y-%m-%d").date()
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
            "INSERT INTO gastos_variables (fecha, categoria, descripcion, pagado_por, comentarios, tipo, monto) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (str(fecha_cuota), categoria, desc, pagado_por, comentario, tipo, valor_cuota),
        )
    conn.commit()

def eliminar_gasto(gasto_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM gastos_variables WHERE id = %s", (gasto_id,))
    conn.commit()

def get_totales_mes(anio, mes):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT pagado_por, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s GROUP BY pagado_por",
        (f"{prefijo}%",),
    )
    rows = c.fetchall()
    return dict(rows)


def get_por_categoria_mes(anio, mes):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT categoria, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s GROUP BY categoria ORDER BY SUM(monto) DESC",
        (f"{prefijo}%",),
    )
    rows = c.fetchall()
    return rows


def get_por_tipo_mes(anio, mes):
    conn = get_conn()
    prefijo = f"{anio}-{mes:02d}"
    c = conn.cursor()
    c.execute(
        "SELECT tipo, SUM(monto) FROM gastos_variables WHERE fecha LIKE %s GROUP BY tipo",
        (f"{prefijo}%",),
    )
    rows = c.fetchall()
    return rows


# --- Gastos fijos ---

def get_gastos_fijos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, nombre, valor, activo, pagado_por FROM gastos_fijos WHERE activo=1 ORDER BY id")
    rows = c.fetchall()
    return rows


def actualizar_gasto_fijo(gasto_id, valor):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET valor=%s WHERE id=%s", (valor, gasto_id))
    conn.commit()

def actualizar_pagador_fijo(gasto_id, pagado_por):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET pagado_por=%s WHERE id=%s", (pagado_por, gasto_id))
    conn.commit()

def agregar_gasto_fijo(nombre, valor):
    conn = get_conn()
    conn.cursor().execute("INSERT INTO gastos_fijos (nombre, valor) VALUES (%s, %s)", (nombre, valor))
    conn.commit()

def get_fijos_excluidos_mes(anio, mes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT gasto_id FROM gastos_fijos_excluidos WHERE mes=%s", (f"{anio}-{mes:02d}",))
    return {row[0] for row in c.fetchall()}

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

def desactivar_gasto_fijo(gasto_id):
    conn = get_conn()
    conn.cursor().execute("UPDATE gastos_fijos SET activo=0 WHERE id=%s", (gasto_id,))
    conn.commit()

# --- Compras con tarjeta ---

def agregar_compra_tarjeta(detalle, valor, cuotas, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por):
    valor_cuota = round(valor / cuotas, 2)
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO compras_tarjeta (detalle, valor, cuotas, valor_cuota, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (detalle, valor, cuotas, valor_cuota, moneda, comentarios, fecha_compra, mes_primera_cuota, tarjeta, pagado_por),
    )
    conn.commit()

def get_compras_tarjeta():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, detalle, valor, cuotas, valor_cuota, moneda, mes_primera_cuota, tarjeta, pagado_por, comentarios, fecha_compra FROM compras_tarjeta ORDER BY id DESC")
    rows = c.fetchall()
    return rows


def eliminar_compra_tarjeta(compra_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM compras_tarjeta WHERE id=%s", (compra_id,))
    conn.commit()

def _parse_mes_cuota(mes_primera, anio_fallback=None):
    """Parsea mes_primera_cuota en formato 'Julio 2026' o texto libre como
    'Primer cuota se paga en julio'. Si no encuentra año, usa anio_fallback."""
    if not mes_primera:
        return None, None
    partes = mes_primera.strip().split()
    # Formato estándar: "Julio 2026"
    if len(partes) == 2 and partes[0] in MESES:
        try:
            return MESES.index(partes[0]) + 1, int(partes[1])
        except ValueError:
            pass
    # Fallback: buscar nombre de mes y año de 4 dígitos en cualquier posición
    mes_num = None
    anio = None
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


def get_total_oca_compartida_mes(anio, mes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT detalle, valor_cuota, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE tarjeta = 'OCA VISA (compartida)'")
    compras = c.fetchall()
    total = 0.0
    detalle_items = []
    for detalle, valor_cuota, n_cuotas, mes_primera in compras:
        mes_inicio, anio_inicio = _parse_mes_cuota(mes_primera, anio_fallback=anio)
        if mes_inicio is None or anio_inicio is None:
            continue
        inicio = anio_inicio * 12 + mes_inicio
        fin = inicio + n_cuotas - 1
        actual = anio * 12 + mes
        if inicio <= actual <= fin:
            cuota_num = actual - inicio + 1
            total += valor_cuota
            detalle_items.append((detalle, valor_cuota, cuota_num, n_cuotas))
    return total, detalle_items


def get_total_cuotas_activas_mes(anio, mes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT pagado_por, tarjeta, detalle, valor_cuota, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE tarjeta != 'OCA VISA (compartida)'")
    compras = c.fetchall()
    totales = {}
    detalle_items = []
    for pagado_por, tarjeta, detalle, valor_cuota, n_cuotas, mes_primera in compras:
        mes_inicio, anio_inicio = _parse_mes_cuota(mes_primera, anio_fallback=anio)
        if mes_inicio is None or anio_inicio is None:
            continue
        inicio = anio_inicio * 12 + mes_inicio
        fin = inicio + n_cuotas - 1
        actual = anio * 12 + mes
        if inicio <= actual <= fin:
            cuota_num = actual - inicio + 1
            totales[pagado_por] = totales.get(pagado_por, 0) + valor_cuota
            detalle_items.append((pagado_por, tarjeta, detalle, valor_cuota, cuota_num, n_cuotas))
    return totales, detalle_items


# --- Pendientes ---

def agregar_pendiente(descripcion, categoria, prioridad, asignado_a):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO pendientes (descripcion, categoria, prioridad, asignado_a, fecha_creacion) VALUES (%s,%s,%s,%s,%s)",
        (descripcion, categoria, prioridad, asignado_a, str(date.today())),
    )
    conn.commit()

def get_pendientes(solo_activos=True):
    conn = get_conn()
    c = conn.cursor()
    filtro = "WHERE completado=0" if solo_activos else ""
    c.execute(
        f"SELECT id, descripcion, categoria, prioridad, asignado_a, completado, fecha_creacion FROM pendientes {filtro} ORDER BY CASE prioridad WHEN 'Alta' THEN 1 WHEN 'Normal' THEN 2 ELSE 3 END, id"
    )
    rows = c.fetchall()
    return rows


def marcar_pendiente(pendiente_id, completado):
    conn = get_conn()
    conn.cursor().execute("UPDATE pendientes SET completado=%s WHERE id=%s", (1 if completado else 0, pendiente_id))
    conn.commit()

def eliminar_pendiente(pendiente_id):
    conn = get_conn()
    conn.cursor().execute("DELETE FROM pendientes WHERE id=%s", (pendiente_id,))
    conn.commit()

def actualizar_pendiente(pendiente_id, descripcion):
    conn = get_conn()
    conn.cursor().execute("UPDATE pendientes SET descripcion=%s WHERE id=%s", (descripcion, pendiente_id))
    conn.commit()

def get_cuotas_del_mes(anio, mes_num):
    nombre_mes = MESES[mes_num - 1]
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, detalle, valor_cuota, moneda, tarjeta, pagado_por, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE mes_primera_cuota=%s",
        (f"{nombre_mes} {anio}",),
    )
    rows = c.fetchall()
    return rows
