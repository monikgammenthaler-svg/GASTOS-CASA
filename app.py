import streamlit as st
from datetime import datetime
import db
import estilos
from views import resumen, cargar_gasto, ver_gastos, cuotas, gastos_fijos, pendientes, personal

# ── Inicialización DB (una sola vez por servidor) ──────────────────────
@st.cache_resource
def _init_once():
    db.init_db()
_init_once()

st.set_page_config(page_title="DOMUS", page_icon="🏠", layout="centered",
                   initial_sidebar_state="expanded")

st.markdown('<link href="https://fonts.googleapis.com/css2?family=Cormorant:wght@600'
            '&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet">',
            unsafe_allow_html=True)
st.markdown(estilos.css_global(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════
def _pantalla_login():
    casas = st.secrets.get("casas", {})
    E = estilos

    st.markdown(f"""
<div style="max-width:420px;margin:60px auto 0;">
  <div style="background:linear-gradient(140deg,{E.NAVY},{E.NAVY2} 70%,{E.BLUE});
       border-radius:22px;padding:36px 34px 30px;
       box-shadow:0 10px 40px rgba(15,27,53,.28);text-align:center;margin-bottom:28px;">
    <div style="font-size:42px;margin-bottom:8px;">🏠</div>
    <div style="color:#fff;font-family:{E.DISPLAY};font-size:52px;font-weight:600;
         line-height:1;letter-spacing:2px;">DOMUS</div>
    <div style="color:{E.GOLD_L};font-size:13px;font-weight:500;margin-top:6px;
         letter-spacing:.5px;">Gastos de nuestro hogar</div>
  </div>
</div>""", unsafe_allow_html=True)

    with st.form("form_login"):
        usuario = st.text_input("Usuario", placeholder="Tu usuario…")
        clave   = st.text_input("Contraseña", type="password", placeholder="Tu contraseña…")
        ok      = st.form_submit_button("Entrar →", use_container_width=True, type="primary")

    if ok:
        for cfg in casas.values():
            if cfg.get("usuario") == usuario and cfg["password"] == clave:
                st.session_state["casa_id"]     = int(cfg["id"])
                st.session_state["personas"]    = list(cfg["personas"])
                st.session_state["casa_nombre"] = cfg["nombre"]
                st.rerun()
        st.error("Usuario o contraseña incorrectos.")

    st.stop()


if not st.session_state.get("casa_id"):
    _pantalla_login()

# ── Variables de sesión ────────────────────────────────────────────────
casa_id     = st.session_state["casa_id"]
personas    = st.session_state["personas"]
persona_1   = personas[0]
persona_2   = personas[1]
casa_nombre = st.session_state["casa_nombre"]


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:11px;padding:8px 6px 0;">
  <span style="font-size:26px;">🏠</span>
  <span style="font-family:{estilos.DISPLAY};font-size:27px;font-weight:600;letter-spacing:2px;">DOMUS</span>
</div>
<div style="color:rgba(255,255,255,.45);font-size:11px;padding:4px 6px 0;">{casa_nombre}</div>
<div style="height:1px;background:rgba(255,255,255,.1);margin:14px 6px;"></div>
""", unsafe_allow_html=True)

    pagina = st.radio(
        "Menú",
        ["📊 Resumen del mes", "➕ Cargar gasto", "📋 Ver gastos",
         "💳 Cuotas tarjeta", "🔒 Gastos fijos", "📝 Pendientes", "💰 Personal"],
        label_visibility="collapsed",
    )

    st.markdown('<div style="height:1px;background:rgba(255,255,255,.1);margin:18px 6px;"></div>',
                unsafe_allow_html=True)
    st.markdown(f'<div style="color:{estilos.GOLD_L};font-size:10px;font-weight:800;'
                f'letter-spacing:1.5px;">AÑO</div>', unsafe_allow_html=True)
    anos     = list(range(2024, 2029))
    anio_sel = st.selectbox("Año", anos,
                             index=anos.index(datetime.today().year) if datetime.today().year in anos else 0,
                             label_visibility="collapsed")

    st.markdown(f'<div style="color:{estilos.GOLD_L};font-size:10px;font-weight:800;'
                f'letter-spacing:1.5px;margin-top:8px;">MES</div>', unsafe_allow_html=True)
    mes_nombre = st.selectbox("Mes", db.MESES, index=datetime.today().month - 1,
                               label_visibility="collapsed")
    mes_sel = db.MESES.index(mes_nombre) + 1

    st.markdown('<div style="height:1px;background:rgba(255,255,255,.1);margin:18px 6px 10px;"></div>',
                unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        for k in ["casa_id", "personas", "casa_nombre"]:
            st.session_state.pop(k, None)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════════
ctx = {
    "casa_id":    casa_id,
    "personas":   personas,
    "persona_1":  persona_1,
    "persona_2":  persona_2,
    "anio_sel":   anio_sel,
    "mes_sel":    mes_sel,
    "mes_nombre": mes_nombre,
    "casa_nombre": casa_nombre,
}

if   pagina == "📊 Resumen del mes": resumen.render(ctx)
elif pagina == "➕ Cargar gasto":    cargar_gasto.render(ctx)
elif pagina == "📋 Ver gastos":      ver_gastos.render(ctx)
elif pagina == "💳 Cuotas tarjeta":  cuotas.render(ctx)
elif pagina == "🔒 Gastos fijos":    gastos_fijos.render(ctx)
elif pagina == "📝 Pendientes":      pendientes.render(ctx)
elif pagina == "💰 Personal":        personal.render(ctx)
