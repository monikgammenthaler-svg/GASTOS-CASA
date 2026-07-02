import bcrypt
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

TARJETAS_SEED_CASA1 = [
    ("OCA VISA (compartida)", "Compartida"),
    ("OCA MONI", "Moni"),
    ("OCA GUILLE", "Guille"),
    ("BROU MONI", "Moni"),
    ("BROU GUILLE", "Guille"),
    ("ITAU MONI", "Moni"),
    ("ITAU GUILLE", "Guille"),
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


def _connect(url):
    conn = psycopg2.connect(url)
    conn.autocommit = True
    return conn


@st.cache_resource
def _db():
    url = st.secrets["supabase"]["db_url"]
    return {"url": url, "conn": _connect(url)}


def get_conn():
    d = _db()
    if d["conn"].closed:
        d["conn"] = _connect(d["url"])
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS casas (
            id SERIAL PRIMARY KEY,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            persona_1 TEXT NOT NULL,
            persona_2 TEXT NOT NULL,
            creado_en TIMESTAMP DEFAULT now()
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tarjetas (
            id SERIAL PRIMARY KEY,
            casa_id INTEGER NOT NULL DEFAULT 1,
            nombre TEXT NOT NULL,
            dueno TEXT NOT NULL,
            activa INTEGER DEFAULT 1,
            UNIQUE(casa_id, nombre, dueno)
        )
    """)
    c.execute("ALTER TABLE tarjetas DROP CONSTRAINT IF EXISTS tarjetas_casa_id_nombre_key")
    c.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'tarjetas_casa_id_nombre_dueno_key'
            ) THEN
                ALTER TABLE tarjetas ADD CONSTRAINT tarjetas_casa_id_nombre_dueno_key UNIQUE (casa_id, nombre, dueno);
            END IF;
        END $$;
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS personas_casa (
            id SERIAL PRIMARY KEY,
            casa_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            orden INTEGER NOT NULL,
            UNIQUE(casa_id, nombre)
        )
    """)
    c.execute("ALTER TABLE casas ALTER COLUMN persona_1 DROP NOT NULL")
    c.execute("ALTER TABLE casas ALTER COLUMN persona_2 DROP NOT NULL")
    c.execute("""
        INSERT INTO personas_casa (casa_id, nombre, orden)
        SELECT id, persona_1, 1 FROM casas
        WHERE persona_1 IS NOT NULL
          AND id NOT IN (SELECT casa_id FROM personas_casa)
    """)
    c.execute("""
        INSERT INTO personas_casa (casa_id, nombre, orden)
        SELECT id, persona_2, 2 FROM casas
        WHERE persona_2 IS NOT NULL
          AND id NOT IN (SELECT casa_id FROM personas_casa WHERE orden=2)
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

    c.execute("SELECT COUNT(*) FROM casas")
    if c.fetchone()[0] == 0:
        for cfg in st.secrets.get("casas", {}).values():
            pw_hash = bcrypt.hashpw(cfg["password"].encode(), bcrypt.gensalt()).decode()
            personas = list(cfg["personas"])
            c.execute(
                "INSERT INTO casas (id, usuario, password_hash, nombre, persona_1, persona_2) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                (int(cfg["id"]), cfg["usuario"], pw_hash, cfg["nombre"], personas[0], personas[1]),
            )
        c.execute("SELECT setval('casas_id_seq', COALESCE((SELECT MAX(id) FROM casas), 1))")

    c.execute("SELECT COUNT(*) FROM tarjetas WHERE casa_id=1")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO tarjetas (nombre, dueno, casa_id) VALUES (%s, %s, 1)",
            TARJETAS_SEED_CASA1,
        )

    conn.commit()


# ── Casas / cuentas ──────────────────────────────────────────────────

def crear_casa(usuario, password_hash, nombre, personas):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO casas (usuario, password_hash, nombre) VALUES (%s,%s,%s) RETURNING id",
        (usuario, password_hash, nombre),
    )
    casa_id = c.fetchone()[0]
    c.executemany(
        "INSERT INTO personas_casa (casa_id, nombre, orden) VALUES (%s,%s,%s)",
        [(casa_id, p, i + 1) for i, p in enumerate(personas)],
    )
    conn.commit()
    return casa_id

def obtener_casa_por_usuario(usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, usuario, password_hash, nombre FROM casas WHERE usuario=%s",
        (usuario,),
    )
    return c.fetchone()

def usuario_existe(usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM casas WHERE usuario=%s", (usuario,))
    return c.fetchone() is not None

def actualizar_password_casa(usuario, password_hash):
    conn = get_conn()
    conn.cursor().execute("UPDATE casas SET password_hash=%s WHERE usuario=%s", (password_hash, usuario))
    conn.commit()

def obtener_casa_por_id(casa_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, usuario, password_hash, nombre FROM casas WHERE id=%s",
        (casa_id,),
    )
    return c.fetchone()

def obtener_personas_casa(casa_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nombre FROM personas_casa WHERE casa_id=%s ORDER BY orden", (casa_id,))
    return [row[0] for row in c.fetchall()]


# ── Tarjetas ─────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_tarjetas(casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, nombre, dueno, activa FROM tarjetas WHERE activa=1 AND casa_id=%s ORDER BY id",
        (casa_id,),
    )
    return c.fetchall()

def agregar_tarjeta(nombre, dueno, casa_id=1):
    conn = get_conn()
    conn.cursor().execute(
        "INSERT INTO tarjetas (nombre, dueno, casa_id) VALUES (%s,%s,%s)", (nombre, dueno, casa_id)
    )
    conn.commit()
    _invalidar()

def actualizar_dueno_tarjeta(tarjeta_id, dueno):
    conn = get_conn()
    conn.cursor().execute("UPDATE tarjetas SET dueno=%s WHERE id=%s", (dueno, tarjeta_id))
    conn.commit()
    _invalidar()

def actualizar_nombre_tarjeta(tarjeta_id, nombre):
    conn = get_conn()
    conn.cursor().execute("UPDATE tarjetas SET nombre=%s WHERE id=%s", (nombre, tarjeta_id))
    conn.commit()
    _invalidar()

def desactivar_tarjeta(tarjeta_id):
    conn = get_conn()
    conn.cursor().execute("UPDATE tarjetas SET activa=0 WHERE id=%s", (tarjeta_id,))
    conn.commit()
    _invalidar()


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
def get_total_cuotas_activas_mes(anio, mes, casa_id=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT pagado_por, tarjeta, detalle, valor_cuota, cuotas, mes_primera_cuota FROM compras_tarjeta WHERE casa_id=%s",
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
