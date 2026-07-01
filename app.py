import streamlit as st
import pandas as pd
from datetime import date, datetime
import db

@st.cache_resource
def _init_once():
    db.init_db()
_init_once()

st.set_page_config(
    page_title="DOMUS",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Paleta ────────────────────────────────────────────────────────────
NAVY   = "#0f1b35"
NAVY2  = "#1a3360"
BLUE   = "#2d6bc4"
GOLD   = "#c9a84c"
GOLD_L = "#f5d060"
GOLD_P = "#fdf6e3"
WHITE  = "#ffffff"
GRAY   = "#6b7280"
SERIF   = "Newsreader, serif"
DISPLAY = "Cormorant, serif"
GOLD_T  = "#a87f2c"

st.markdown('<link href="https://fonts.googleapis.com/css2?family=Cormorant:wght@600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet">', unsafe_allow_html=True)

st.markdown(f"""
<style>
    .stApp {{ background-color: #efeae6; }}
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg,{NAVY},#13213f) !important;
    }}
    section[data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        display:flex; align-items:center; gap:14px;
        padding:13px 14px; border-radius:12px; margin:3px 0;
        cursor:pointer; transition:background .15s;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background:rgba(255,255,255,.07); }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{ display:none; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
        background:rgba(45,107,196,.26);
        box-shadow:inset 3px 0 0 {GOLD_L};
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] p {{ font-size:17px; font-weight:600; }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background:rgba(255,255,255,.06) !important;
        border:1px solid rgba(255,255,255,.14) !important; border-radius:10px !important;
    }}
    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input {{
        border-radius:10px !important; border:1px solid rgba(15,27,53,.14) !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        border-radius:10px !important; background:#f4f6fb !important;
        border:1px solid rgba(15,27,53,.1) !important;
    }}
    div[data-testid="stNumberInput"] input {{
        border-radius:9px !important; border:1px solid rgba(15,27,53,.14) !important;
        font-family:{SERIF} !important; font-size:16px !important;
        text-align:right !important; color:{NAVY} !important; background:#fff !important;
    }}
    .stButton > button[kind="primary"] {{
        background:linear-gradient(135deg,{NAVY},{BLUE}) !important;
        color:#fff !important; font-weight:700 !important;
        border:none !important; border-radius:12px !important;
    }}
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {{
        background:linear-gradient(135deg,{NAVY},{BLUE}) !important;
        color:#fff !important; border:none !important; border-radius:12px !important;
        font-weight:700 !important;
    }}
    div[data-testid="column"] button[kind="secondary"] {{
        border:1.5px solid rgba(45,107,196,.4) !important;
        color:{BLUE} !important; border-radius:9px !important; font-weight:700 !important;
        padding:4px 6px !important; min-height:36px !important;
    }}
    @media(max-width:640px) {{
        div[data-testid="column"] button[kind="secondary"] {{
            font-size:15px !important; padding:2px 0 !important;
        }}
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color:{NAVY} !important; }}
    div[data-baseweb="tab-highlight"] {{ background:{GOLD} !important; }}
    h1 {{ color:{NAVY} !important; }}
    h2, h3 {{ color:{NAVY2} !important; }}
    hr {{ border-color:#e2e8f0 !important; }}
    .tag-p1 {{ background:{BLUE}; color:{WHITE}; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    .tag-p2 {{ background:{GOLD}; color:{NAVY}; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    .g-card {{ background:{WHITE}; border-radius:14px; padding:20px 24px; box-shadow:0 2px 12px rgba(15,27,53,0.08); margin-bottom:16px; }}
    div[data-testid="stSidebarNav"] {{ display:none; }}
    div[data-testid="stToggle"] div[aria-checked="true"],
    div[data-testid="stToggle"] input:checked ~ div {{
        background-color:{GOLD} !important; border-color:{GOLD} !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:white !important; border:1px solid rgba(15,27,53,.08) !important;
        border-top:none !important; border-radius:0 0 20px 20px !important;
        box-shadow:0 6px 24px rgba(15,27,53,.1) !important;
        margin-top:-4px !important; padding:0 6px 8px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background:rgba(255,255,255,.10) !important;
        border:1px solid rgba(255,255,255,.22) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span,
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {{
        color:{WHITE} !important; fill:{WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,255,255,.07) !important;
        color: rgba(255,255,255,.6) !important;
        border: 1px solid rgba(255,255,255,.12) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,.13) !important;
        color: {WHITE} !important;
        border-color: rgba(255,255,255,.22) !important;
    }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════
def _pantalla_login():
    casas = st.secrets.get("casas", {})

    st.markdown(f"""
    <div style="max-width:460px;margin:60px auto 0;">
      <div style="background:linear-gradient(140deg,{NAVY},{NAVY2} 70%,{BLUE});
           border-radius:22px;padding:36px 34px 30px;
           box-shadow:0 10px 40px rgba(15,27,53,.28);text-align:center;margin-bottom:28px;">
        <div style="font-size:42px;margin-bottom:8px;">🏠</div>
        <div style="color:#fff;font-family:{DISPLAY};font-size:52px;font-weight:600;line-height:1;letter-spacing:2px;">DOMUS</div>
        <div style="color:{GOLD_L};font-size:13px;font-weight:500;margin-top:6px;letter-spacing:.5px;">Gastos de nuestro hogar</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    casa_key = st.session_state.get("login_casa_key")

    if casa_key is None:
        # ── Paso 1: elegir hogar ─────────────────────────────────────
        st.markdown(
            f'<div style="text-align:center;color:{NAVY};font-size:14px;font-weight:600;'
            f'letter-spacing:.5px;margin-bottom:14px;">¿A qué hogar querés entrar?</div>',
            unsafe_allow_html=True)

        iconos = ["🏡", "🏠", "🏘️", "🏗️"]
        cols = st.columns(len(casas))
        for i, (key, cfg) in enumerate(casas.items()):
            icono = iconos[i % len(iconos)]
            personas_txt = " & ".join(cfg["personas"])
            with cols[i]:
                st.markdown(f"""
                <div style="background:#fff;border-radius:16px;padding:20px 12px 14px;
                     box-shadow:0 2px 14px rgba(15,27,53,.1);text-align:center;
                     border:2px solid rgba(15,27,53,.06);margin-bottom:8px;">
                  <div style="font-size:30px;margin-bottom:8px;">{icono}</div>
                  <div style="color:{NAVY};font-family:{DISPLAY};font-size:20px;font-weight:600;line-height:1.1;">{personas_txt}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Entrar", key=f"sel_{key}", use_container_width=True, type="primary"):
                    st.session_state["login_casa_key"] = key
                    st.rerun()
    else:
        # ── Paso 2: ingresar contraseña ──────────────────────────────
        cfg = casas[casa_key]
        personas_txt = " & ".join(cfg["personas"])
        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:18px 22px 14px;
             box-shadow:0 2px 14px rgba(15,27,53,.1);border-left:4px solid {GOLD};
             margin-bottom:20px;">
          <div style="color:{GRAY};font-size:11px;font-weight:700;letter-spacing:1.5px;">HOGAR SELECCIONADO</div>
          <div style="color:{NAVY};font-family:{DISPLAY};font-size:24px;font-weight:600;margin-top:2px;">{personas_txt}</div>
        </div>""", unsafe_allow_html=True)

        with st.form("form_login"):
            clave = st.text_input("Contraseña", type="password", placeholder="Tu contraseña…")
            ok = st.form_submit_button("Entrar →", use_container_width=True, type="primary")

        if ok:
            if cfg["password"] == clave:
                st.session_state["casa_id"]     = int(cfg["id"])
                st.session_state["personas"]    = list(cfg["personas"])
                st.session_state["casa_nombre"] = cfg["nombre"]
                st.session_state.pop("login_casa_key", None)
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Intentá de nuevo.")

        if st.button("← Cambiar hogar", use_container_width=False):
            st.session_state.pop("login_casa_key", None)
            st.rerun()

    st.stop()


if not st.session_state.get("casa_id"):
    _pantalla_login()

# Variables de sesión disponibles tras login
casa_id     = st.session_state["casa_id"]
personas    = st.session_state["personas"]
persona_1   = personas[0]
persona_2   = personas[1]
casa_nombre = st.session_state["casa_nombre"]


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:11px;padding:8px 6px 0;">
  <span style="font-size:26px;">🏠</span>
  <span style="font-family:{DISPLAY};font-size:27px;font-weight:600;letter-spacing:2px;">DOMUS</span>
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
    st.markdown('<div style="height:1px;background:rgba(255,255,255,.1);margin:18px 6px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:1.5px;">AÑO</div>', unsafe_allow_html=True)
    anos = list(range(2024, 2029))
    anio_sel = st.selectbox("Año", anos, index=anos.index(datetime.today().year) if datetime.today().year in anos else 0, label_visibility="collapsed")
    st.markdown(f'<div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:1.5px;margin-top:8px;">MES</div>', unsafe_allow_html=True)
    mes_nombre = st.selectbox("Mes", db.MESES, index=datetime.today().month - 1, label_visibility="collapsed")
    mes_sel = db.MESES.index(mes_nombre) + 1

    st.markdown('<div style="height:1px;background:rgba(255,255,255,.1);margin:18px 6px 10px;"></div>', unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        for k in ["casa_id", "personas", "casa_nombre"]:
            st.session_state.pop(k, None)
        st.rerun()


# ── Helper HTML ───────────────────────────────────────────────────────
def banner(texto, tipo="info"):
    colores = {
        "info":    (BLUE,  "#e8f0fe"),
        "gold":    (GOLD,  GOLD_P),
        "success": ("#15803d", "#dcfce7"),
        "warning": ("#b45309", "#fef3c7"),
    }
    border, bg = colores.get(tipo, (BLUE, "#e8f0fe"))
    return f"<div style='background:{bg};border-left:4px solid {border};padding:11px 16px;border-radius:8px;margin-bottom:14px;font-size:14px;color:{NAVY};'>{texto}</div>"


def render_resumen(st, mes_nombre, anio_sel,
                   total_mes, variables, fijos,
                   p1_pago, p2_pago, corresponde_cu,
                   deudor, acreedor, balance,
                   persona_1, persona_2,
                   total_ant=None, balance_ant=None, deudor_ant=None, acreedor_ant=None):
    p1_pct = round(p1_pago / (p1_pago + p2_pago) * 100) if (p1_pago + p2_pago) else 50
    st.markdown(f"""
<div style="padding:34px 30px 8px;">
  <div style="color:#b7973f;font-family:{DISPLAY};font-size:19px;font-weight:600;
       font-style:italic;letter-spacing:3px;text-transform:uppercase;">Resumen del mes</div>
  <div style="color:{NAVY};font-family:{DISPLAY};font-size:72px;font-weight:600;
       line-height:.98;margin-top:4px;letter-spacing:-.5px;">{mes_nombre} {anio_sel}</div>
</div>""", unsafe_allow_html=True)
    st.markdown(f"""
<div style="padding:0 30px;display:flex;flex-direction:column;gap:8px;">
  <div style="display:flex;align-items:center;gap:10px;background:#faf8f4;border-left:3px solid {GOLD};
       border-radius:8px;padding:9px 13px;">
    <span style="width:6px;height:6px;border-radius:50%;background:{GOLD};flex:none;"></span>
    <span style="font-size:12.5px;color:#6b5d38;">Los gastos de <b style="color:{NAVY};">{mes_nombre}</b>
    se pagan con el sueldo de <b style="color:{NAVY};">principios del mes siguiente</b>.</span>
  </div>
</div>""", unsafe_allow_html=True)
    if balance_ant is not None and total_ant:
        st.markdown(f"""
<div style="padding:8px 30px 0;">
  <div style="display:flex;align-items:center;gap:10px;background:#eef7f1;border-left:3px solid #1f9d57;
       border-radius:8px;padding:9px 13px;">
    <span style="width:6px;height:6px;border-radius:50%;background:#1f9d57;flex:none;"></span>
    <span style="font-size:12.5px;color:#2f6b48;">A pagar <b>este mes</b>: Total
    <b>$ {total_ant:,.0f}</b> · {deudor_ant} le paga a {acreedor_ant} <b>$ {balance_ant:,.0f}</b></span>
  </div>
</div>""", unsafe_allow_html=True)
    if balance < 1:
        hero_inner = f"""
      <div style="color:#86efac;font-size:11px;font-weight:800;letter-spacing:2px;">ESTÁN AL DÍA</div>
      <div style="color:#fff;font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.02;margin-top:6px;">$ 0</div>
      <div style="color:rgba(255,255,255,.55);font-size:12px;margin-top:2px;">Los dos gastaron lo mismo</div>"""
    else:
        hero_inner = f"""
      <div style="color:{GOLD_L};font-size:11px;font-weight:800;letter-spacing:2px;">{deudor} LE DEBE A {acreedor}</div>
      <div style="color:#fff;font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.02;margin-top:6px;">$ {balance:,.0f}</div>
      <div style="color:rgba(255,255,255,.55);font-size:12px;margin-top:2px;">para quedar iguales</div>"""
    st.markdown(f"""
<div style="margin:18px 24px 8px;background:linear-gradient(140deg,{NAVY},{NAVY2} 70%,{BLUE});
     border-radius:18px;padding:26px 28px;box-shadow:0 6px 24px rgba(15,27,53,.22);">
  <div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:3px;">LIQUIDACIÓN DEL MES</div>
  <div style="text-align:center;padding:14px 0 18px;">{hero_inner}</div>
  <div style="display:flex;height:10px;border-radius:6px;overflow:hidden;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);">
    <div style="background:linear-gradient(90deg,{BLUE},#3f86e0);width:{p1_pct}%;"></div>
    <div style="background:linear-gradient(90deg,{GOLD},{GOLD_L});flex:1;"></div>
  </div>
  <div style="display:flex;align-items:stretch;gap:14px;margin-top:16px;">
    <div style="flex:1;background:rgba(45,107,196,.28);border-radius:13px;padding:14px 16px;text-align:center;">
      <div style="color:#93c5fd;font-size:11px;font-weight:700;letter-spacing:1px;">{persona_1.upper()} PAGÓ</div>
      <div style="color:#fff;font-family:{SERIF};font-size:26px;font-weight:600;margin-top:4px;">$ {p1_pago:,.0f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:10.5px;margin-top:3px;">le corresponde $ {corresponde_cu:,.0f}</div>
    </div>
    <div style="display:flex;align-items:center;color:{GOLD_L};font-size:20px;opacity:.7;">⇄</div>
    <div style="flex:1;background:rgba(201,168,76,.22);border-radius:13px;padding:14px 16px;text-align:center;">
      <div style="color:{GOLD_L};font-size:11px;font-weight:700;letter-spacing:1px;">{persona_2.upper()} PAGÓ</div>
      <div style="color:#fff;font-family:{SERIF};font-size:26px;font-weight:600;margin-top:4px;">$ {p2_pago:,.0f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:10.5px;margin-top:3px;">le corresponde $ {corresponde_cu:,.0f}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
    def _stat(label, valor, acento):
        return (f'<div style="background:#faf8f4;border:1px solid rgba(15,27,53,.07);'
                f'border-top:3px solid {acento};border-radius:13px;padding:16px 12px;text-align:center;">'
                f'<div style="color:#9aa0ab;font-size:10px;font-weight:800;letter-spacing:1.2px;">{label}</div>'
                f'<div style="color:{NAVY};font-family:{SERIF};font-size:28px;font-weight:600;margin-top:4px;">$ {valor:,.0f}</div></div>')
    st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;padding:16px 24px 28px;">
  {_stat("TOTAL DEL MES", total_mes, GOLD)}
  {_stat("VARIABLES", variables, BLUE)}
  {_stat("FIJOS", fijos, NAVY2)}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# 1. RESUMEN DEL MES
# ══════════════════════════════════════════════════════════════════════
if pagina == "📊 Resumen del mes":
    nombre_mes = db.MESES[mes_sel - 1]

    mes_ant_num    = mes_sel - 1 if mes_sel > 1 else 12
    anio_ant       = anio_sel if mes_sel > 1 else anio_sel - 1

    gastos_fijos      = db.get_gastos_fijos(casa_id)
    excluidos_res     = db.get_fijos_excluidos_mes(anio_sel, mes_sel)
    p1_fijos          = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == persona_1)
    p2_fijos          = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == persona_2)
    total_fijos_base  = p1_fijos + p2_fijos
    oca_total, oca_items = db.get_total_oca_compartida_mes(anio_sel, mes_sel, casa_id)
    total_fijos       = total_fijos_base + oca_total
    total_por_persona = db.get_totales_mes(anio_sel, mes_sel, casa_id)
    cuotas_persona, cuotas_items = db.get_total_cuotas_activas_mes(anio_sel, mes_sel, casa_id)
    p1_vars           = total_por_persona.get(persona_1, 0)
    p1_cuotas         = cuotas_persona.get(persona_1, 0)
    p2_vars           = total_por_persona.get(persona_2, 0)
    p2_cuotas         = cuotas_persona.get(persona_2, 0)
    p2_pago           = p2_vars + p2_cuotas + p2_fijos + oca_total
    total_variable    = sum(total_por_persona.values()) + sum(cuotas_persona.values())
    total_general     = total_fijos + total_variable
    p1_pago           = p1_vars + p1_cuotas + p1_fijos
    mitad             = total_general / 2
    balance           = p1_pago - mitad

    tot_ant_persona   = db.get_totales_mes(anio_ant, mes_ant_num, casa_id)
    cuotas_ant, _     = db.get_total_cuotas_activas_mes(anio_ant, mes_ant_num, casa_id)
    total_variable_ant = sum(tot_ant_persona.values()) + sum(cuotas_ant.values())
    total_ant         = total_fijos + total_variable_ant
    p1_ant            = tot_ant_persona.get(persona_1, 0) + cuotas_ant.get(persona_1, 0) + total_fijos_base
    balance_ant       = p1_ant - total_ant / 2

    if abs(balance) < 1:
        deudor, acreedor, balance_show = "—", "—", 0
    elif balance > 0:
        deudor, acreedor, balance_show = persona_2.upper(), persona_1.upper(), balance
    else:
        deudor, acreedor, balance_show = persona_1.upper(), persona_2.upper(), abs(balance)

    kw_ant = {}
    if total_ant > 0:
        if abs(balance_ant) < 1:
            kw_ant = dict(total_ant=total_ant, balance_ant=0, deudor_ant="—", acreedor_ant="—")
        elif balance_ant > 0:
            kw_ant = dict(total_ant=total_ant, balance_ant=balance_ant, deudor_ant=persona_2, acreedor_ant=persona_1)
        else:
            kw_ant = dict(total_ant=total_ant, balance_ant=abs(balance_ant), deudor_ant=persona_1, acreedor_ant=persona_2)

    render_resumen(st, nombre_mes, anio_sel,
                   total_general, total_variable, total_fijos,
                   p1_pago, p2_pago, mitad,
                   deudor, acreedor, balance_show,
                   persona_1, persona_2, **kw_ant)

    st.markdown("---")

    # ── POR CATEGORÍA ────────────────────────────────────────────────
    por_cat = db.get_por_categoria_mes(anio_sel, mes_sel, casa_id)
    if por_cat:
        st.markdown("<h3>Por categoría</h3>", unsafe_allow_html=True)
        df_cat = pd.DataFrame(por_cat, columns=["Categoría", "Monto"])
        df_cat["Monto"] = df_cat["Monto"].round(0).astype(int)
        st.bar_chart(df_cat.set_index("Categoría"), height=220, color=BLUE)
        for cat, monto in por_cat:
            pct = (monto / total_variable * 100) if total_variable > 0 else 0
            pct_bar = int(pct)
            st.markdown(f"""
            <div style="display:flex;align-items:center;margin-bottom:6px;gap:10px;">
                <div style="width:130px;font-size:13px;color:{NAVY};font-weight:500;">{cat}</div>
                <div style="flex:1;background:#e2e8f0;border-radius:4px;height:8px;">
                    <div style="width:{pct_bar}%;background:linear-gradient(90deg,{BLUE},{GOLD});height:8px;border-radius:4px;"></div>
                </div>
                <div style="width:80px;text-align:right;font-size:13px;font-weight:700;color:{NAVY};">$ {monto:,.0f}</div>
                <div style="width:38px;font-size:11px;color:{GRAY};">{pct:.0f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── POR TIPO DE PAGO ─────────────────────────────────────────────
    por_tipo = db.get_por_tipo_mes(anio_sel, mes_sel, casa_id)
    if por_tipo:
        st.markdown("<h3>Por tipo de pago</h3>", unsafe_allow_html=True)
        cols = st.columns(len(por_tipo))
        iconos = {"Débito": "💳", "Crédito": "🏦", "Efectivo": "💵"}
        for i, (tipo, monto) in enumerate(por_tipo):
            cols[i].markdown(f"""
            <div class="g-card" style="text-align:center;border-top:3px solid {NAVY2};">
                <div style="font-size:22px;">{iconos.get(tipo,'💰')}</div>
                <div style="color:{GRAY};font-size:12px;margin-top:4px;">{tipo}</div>
                <div style="color:{NAVY};font-size:22px;font-weight:800;">$ {monto:,.0f}</div>
            </div>""", unsafe_allow_html=True)

    # ── GASTOS FIJOS ─────────────────────────────────────────────────
    st.markdown("---")

    def tarjeta_compromisos(filas, total_f, p1_f, p2_f):
        cu_total = total_f / 2
        n_filas = len(filas)
        th = (
            f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 54px 88px 70px;gap:8px;'
            f'align-items:center;padding:12px 10px 9px;border-bottom:1px solid rgba(15,27,53,.1);">'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">GASTO</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">PAGA</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">TOTAL</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">C/U</span>'
            f'</div>'
        )
        def _fila(nombre, valor, pagado_por, pagado=False):
            if pagado_por == persona_1:
                badge = (f'<span style="background:#e8f0fe;color:{BLUE};font-size:9.5px;font-weight:800;'
                         f'letter-spacing:.5px;padding:3px 9px;border-radius:20px;">{persona_1.upper()}</span>')
            else:
                badge = (f'<span style="background:rgba(201,168,76,.2);color:#8a6d22;font-size:9.5px;'
                         f'font-weight:800;letter-spacing:.5px;padding:3px 9px;border-radius:20px;">{persona_2.upper()}</span>')
            if pagado:
                check = (f'<span style="width:21px;height:21px;border-radius:50%;flex:none;'
                         f'background:linear-gradient(135deg,{GOLD},{GOLD_L});color:{NAVY};display:flex;'
                         f'align-items:center;justify-content:center;font-size:12px;font-weight:900;">✓</span>')
                deco, op = "line-through", ".42"
            else:
                check = ('<span style="width:21px;height:21px;border-radius:50%;flex:none;'
                         'border:2px solid rgba(15,27,53,.16);"></span>')
                deco, op = "none", "1"
            return (
                f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 54px 88px 70px;gap:8px;'
                f'align-items:center;padding:11px 10px;border-radius:10px;opacity:{op};">'
                f'<div style="display:flex;align-items:center;gap:11px;min-width:0;">{check}'
                f'<span style="color:{NAVY};font-size:13px;font-weight:500;word-break:break-word;'
                f'overflow-wrap:anywhere;text-decoration:{deco};">{nombre}</span></div>'
                f'<div>{badge}</div>'
                f'<span style="text-align:right;color:{NAVY};font-family:{SERIF};font-size:16px;font-weight:500;'
                f'font-variant-numeric:tabular-nums;text-decoration:{deco};">$ {valor:,.0f}</span>'
                f'<span style="text-align:right;color:#b7973f;font-size:12.5px;font-weight:700;'
                f'font-variant-numeric:tabular-nums;">$ {valor/2:,.0f}</span>'
                f'</div>'
            )
        filas_html = "".join(
            _fila(f[0], f[1], f[2], f[3] if len(f) > 3 else False) for f in filas
        )
        header = (
            f'<div style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 58%,{BLUE} 100%);padding:24px 28px 22px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<div>'
            f'<div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:3px;">COMPROMISOS DEL MES</div>'
            f'<div style="color:#fff;font-family:{SERIF};font-size:40px;font-weight:500;margin-top:6px;'
            f'letter-spacing:-1px;line-height:1;font-variant-numeric:tabular-nums;">$ {total_f:,.0f}</div>'
            f'<div style="color:rgba(255,255,255,.5);font-size:11px;font-weight:600;letter-spacing:.5px;margin-top:4px;">'
            f'{n_filas} conceptos · compartido 50 / 50</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="display:inline-block;background:rgba(201,168,76,.22);border:1px solid rgba(245,208,96,.35);'
            f'border-radius:20px;padding:5px 12px;color:{GOLD_L};font-size:11px;font-weight:700;">corresponde c/u</div>'
            f'<div style="color:{GOLD_L};font-family:{SERIF};font-size:26px;font-weight:500;margin-top:8px;'
            f'font-variant-numeric:tabular-nums;">$ {cu_total:,.0f}</div>'
            f'</div></div>'
            f'<div style="display:flex;gap:9px;margin-top:18px;">'
            f'<div style="flex:1;background:rgba(45,107,196,.32);border-radius:11px;padding:9px 13px;">'
            f'<div style="color:rgba(255,255,255,.65);font-size:10px;font-weight:700;letter-spacing:.5px;">PAGA {persona_1.upper()}</div>'
            f'<div style="color:#fff;font-family:{SERIF};font-size:19px;font-weight:500;font-variant-numeric:tabular-nums;">$ {p1_f:,.0f}</div>'
            f'</div>'
            f'<div style="flex:1;background:rgba(201,168,76,.28);border-radius:11px;padding:9px 13px;">'
            f'<div style="color:rgba(255,255,255,.65);font-size:10px;font-weight:700;letter-spacing:.5px;">PAGA {persona_2.upper()}</div>'
            f'<div style="color:{GOLD_L};font-family:{SERIF};font-size:19px;font-weight:500;font-variant-numeric:tabular-nums;">$ {p2_f:,.0f}</div>'
            f'</div></div>'
            f'</div>'
        )
        return (
            f'<div style="border-radius:20px;overflow:hidden;box-shadow:0 6px 30px rgba(15,27,53,.13);margin-bottom:8px;">'
            f'{header}'
            f'<div style="background:#fff;padding:4px 18px 16px;">{th}{filas_html}</div>'
            f'</div>'
        )

    fijos_excluidos = [(nombre_ex,) for gid, nombre_ex, _, _, _ in gastos_fijos if gid in excluidos_res]
    filas_card = [(nombre_f, v, pg) for gid, nombre_f, v, _, pg in gastos_fijos if gid not in excluidos_res]
    st.markdown(
        tarjeta_compromisos(filas_card, total_fijos_base, p1_fijos, p2_fijos),
        unsafe_allow_html=True,
    )

    if fijos_excluidos:
        excl_html = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:8px 12px;margin-bottom:3px;'
            f'background:#f8fafc;border-radius:8px;opacity:0.5;">'
            f'<span style="color:{GRAY};font-size:12px;text-decoration:line-through;">{nombre_ex}</span>'
            f'<span style="color:{GRAY};font-size:11px;">no aplica este mes</span></div>'
            for (nombre_ex,) in fijos_excluidos
        )
        st.markdown(
            f'<div style="background:#f8fafc;border-radius:12px;padding:12px 16px;margin-bottom:8px;">'
            f'<div style="color:{GRAY};font-size:10px;font-weight:700;letter-spacing:1px;margin-bottom:8px;">NO APLICA ESTE MES</div>'
            f'{excl_html}</div>',
            unsafe_allow_html=True,
        )

    if cuotas_items or oca_items:
        cuotas_html_parts = []
        for d, vc, cn, tc in oca_items:
            cuotas_html_parts.append(
                f'<div style="display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;'
                f'padding:10px 12px;margin-bottom:4px;background:rgba(201,168,76,.1);'
                f'border-radius:10px;border-left:3px solid {GOLD};">'
                f'<div><div style="color:{NAVY};font-size:13px;font-weight:600;">OCA VISA: {d}</div>'
                f'<div style="color:{GRAY};font-size:11px;">OCA VISA (compartida) · cuota {cn}/{tc} · paga {persona_2}</div></div>'
                f'<span style="color:{NAVY};font-size:15px;font-weight:700;">$ {vc:,.0f}</span>'
                f'</div>'
            )
        for p, t, d, vc, cn, tc in cuotas_items:
            bg  = "#eef3fc" if p == persona_1 else "rgba(201,168,76,.1)"
            col = BLUE      if p == persona_1 else GOLD
            cuotas_html_parts.append(
                f'<div style="display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;'
                f'padding:10px 12px;margin-bottom:4px;background:{bg};'
                f'border-radius:10px;border-left:3px solid {col};">'
                f'<div><div style="color:{NAVY};font-size:13px;font-weight:600;">{d}</div>'
                f'<div style="color:{GRAY};font-size:11px;">{t} · cuota {cn}/{tc} · paga {p}</div></div>'
                f'<span style="color:{NAVY};font-size:15px;font-weight:700;">$ {vc:,.0f}</span>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:#f8fafc;border-radius:12px;padding:12px 16px;margin-bottom:8px;">'
            f'<div style="color:{GRAY};font-size:10px;font-weight:700;letter-spacing:1px;margin-bottom:8px;">CUOTAS DE TARJETA</div>'
            f'{"".join(cuotas_html_parts)}</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════
# 2. CARGAR GASTO
# ══════════════════════════════════════════════════════════════════════
elif pagina == "➕ Cargar gasto":
    st.markdown(f'<div style="color:{NAVY};font-family:{DISPLAY};font-size:46px;font-weight:600;'
                f'line-height:1;margin-bottom:10px;">Cargar gasto</div>', unsafe_allow_html=True)

    tiene_cuotas = st.checkbox("¿Pago en cuotas?")

    with st.form("form_gasto", clear_on_submit=True):
        col_f, col_p = st.columns([2, 1])
        fecha      = col_f.date_input("Fecha", value=date.today())
        pagado_por = col_p.selectbox("¿Quién pagó?", personas)

        col_cat, col_tipo = st.columns(2)
        categoria = col_cat.selectbox("Categoría", db.CATEGORIAS)
        tipo      = col_tipo.selectbox("Tipo de pago", db.TIPOS_PAGO)

        descripcion = st.text_input("Descripción", placeholder="ej: Super Paulino, taxi, farmacia...")
        monto       = st.number_input("Monto total ($)", min_value=0.0, step=10.0, format="%.0f")

        num_cuotas    = 1
        tarjeta_cuota = None
        if tiene_cuotas:
            st.markdown("---")
            col_nc, col_tc = st.columns(2)
            num_cuotas    = col_nc.number_input("Cantidad de cuotas", min_value=2, max_value=48, step=1, value=3)
            tarjeta_cuota = col_tc.selectbox("Tarjeta", db.TARJETAS)
            if monto > 0:
                st.info(f"Valor por cuota: $ {monto / num_cuotas:,.0f}  ·  {int(num_cuotas)} meses desde {db.MESES[fecha.month - 1]} {fecha.year}")

        comentarios = st.text_input("Comentarios (opcional)", placeholder="ej: con 20% descuento")
        enviado = st.form_submit_button("Guardar gasto", use_container_width=True)

    if enviado:
        if monto <= 0:
            st.error("El monto debe ser mayor a cero.")
        elif tiene_cuotas:
            db.agregar_gasto_en_cuotas(str(fecha), categoria, descripcion, pagado_por, tipo, tarjeta_cuota, monto, int(num_cuotas), casa_id)
            st.success(f"✅ {int(num_cuotas)} cuotas de $ {round(monto/num_cuotas,0):,.0f} guardadas.")
            st.balloons()
        else:
            db.agregar_gasto(str(fecha), categoria, descripcion, pagado_por, comentarios, tipo, monto, casa_id)
            st.success(f"✅ Gasto de $ {monto:,.0f} guardado.")
            st.balloons()


# ══════════════════════════════════════════════════════════════════════
# 3. VER GASTOS
# ══════════════════════════════════════════════════════════════════════
elif pagina == "📋 Ver gastos":
    nombre_mes = db.MESES[mes_sel - 1]
    st.markdown(f"<h1>Gastos de {nombre_mes} {anio_sel}</h1>", unsafe_allow_html=True)

    gastos = db.get_gastos_mes(anio_sel, mes_sel, casa_id)

    if not gastos:
        st.info("No hay gastos cargados para este mes.")
    else:
        cols_filter = st.columns(3)
        filtro_persona = cols_filter[0].selectbox("Persona", ["Todos"] + personas)
        filtro_tipo    = cols_filter[1].selectbox("Tipo",    ["Todos"] + db.TIPOS_PAGO)
        filtro_cat     = cols_filter[2].selectbox("Categoría", ["Todas"] + db.CATEGORIAS)

        df = pd.DataFrame(gastos, columns=["id","Fecha","Categoría","Descripción","Pagado por","Tipo","Monto","Comentarios"])
        if filtro_persona != "Todos":  df = df[df["Pagado por"] == filtro_persona]
        if filtro_tipo    != "Todos":  df = df[df["Tipo"]       == filtro_tipo]
        if filtro_cat     != "Todas":  df = df[df["Categoría"]  == filtro_cat]

        total_filtrado = df["Monto"].sum()
        st.markdown(f"""
        <div class="g-card" style="display:flex;justify-content:space-between;align-items:center;border-left:4px solid {GOLD};">
            <div><span style="color:{GRAY};font-size:12px;">TOTAL FILTRADO</span><br>
            <span style="color:{NAVY};font-size:26px;font-weight:800;">$ {total_filtrado:,.0f}</span></div>
            <div style="color:{GOLD};font-size:20px;font-weight:700;">{len(df)} registros</div>
        </div>""", unsafe_allow_html=True)

        for _, row in df.iterrows():
            if row['Pagado por'] == persona_1:
                tag = f"<span class='tag-p1'>{persona_1.upper()}</span>"
            else:
                tag = f"<span class='tag-p2'>{persona_2.upper()}</span>"
            with st.expander(f"{row['Fecha']}  —  {row['Descripción'] or row['Categoría']}  |  $ {row['Monto']:,.0f}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Categoría:** {row['Categoría']}")
                c2.markdown(f"**Quién:** {tag}", unsafe_allow_html=True)
                c3.write(f"**Tipo:** {row['Tipo']}")
                if row['Comentarios']:
                    st.caption(row['Comentarios'])
                if st.button("Eliminar", key=f"del_{row['id']}"):
                    db.eliminar_gasto(row['id'])
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════
# 4. CUOTAS TARJETA
# ══════════════════════════════════════════════════════════════════════
elif pagina == "💳 Cuotas tarjeta":
    compras_all = db.get_compras_tarjeta(casa_id)

    def _pagadas(primera, n):
        try:
            partes = (primera or "").strip().split()
            mes_ini = anio_ini = None
            if len(partes) == 2 and partes[0] in db.MESES:
                mes_ini, anio_ini = db.MESES.index(partes[0]) + 1, int(partes[1])
            else:
                for p in partes:
                    if p.capitalize() in db.MESES and mes_ini is None:
                        mes_ini = db.MESES.index(p.capitalize()) + 1
                    try:
                        y = int(p)
                        if 2020 <= y <= 2035: anio_ini = y
                    except ValueError:
                        pass
            if mes_ini is None:
                return 0
            if anio_ini is None:
                anio_ini = anio_sel
            return max(0, min(anio_sel * 12 + mes_sel - (anio_ini * 12 + mes_ini) + 1, n))
        except Exception:
            return 0

    compras_con_p = [
        (cid, det, vt, n, vc, mon, prim, tarj, pers, com, _pagadas(prim, n))
        for (cid, det, vt, n, vc, mon, prim, tarj, pers, com, _) in compras_all
    ]
    activas_mes = [c for c in compras_con_p if 1 <= c[10] <= c[3]]
    total_mes_cuotas = sum(c[4] for c in activas_mes)

    st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 58%,{BLUE} 100%);
            border-radius:20px 20px 0 0;padding:24px 30px 6px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div style="color:{GOLD_L};font-family:{DISPLAY};font-size:16px;font-weight:600;
           font-style:italic;letter-spacing:2px;text-transform:uppercase;">Cuotas · Tarjeta</div>
      <div style="color:#fff;font-family:{DISPLAY};font-size:40px;font-weight:600;line-height:1.05;">Cuotas con tarjeta</div>
    </div>
    <div style="text-align:right;">
      <div style="color:rgba(255,255,255,.55);font-size:10px;font-weight:700;letter-spacing:2px;">TOTAL / MES</div>
      <div style="color:#fff;font-family:{SERIF};font-size:32px;font-weight:500;">$ {total_mes_cuotas:,.0f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    if "form_cuota_n" not in st.session_state:
        st.session_state.form_cuota_n = 0

    tab_ver, tab_nueva = st.tabs(["Ver cuotas", "Nueva compra"])

    with tab_ver:
        if not activas_mes:
            st.info("No hay cuotas activas para este mes.")
        else:
            filtro_tarj = st.selectbox("Filtrar por tarjeta", ["Todas"] + db.TARJETAS, label_visibility="collapsed")
            vis = activas_mes if filtro_tarj == "Todas" else [c for c in activas_mes if c[7] == filtro_tarj]
            tot_vis = sum(c[4] for c in vis)

            st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
     background:{GOLD_P};border:1px solid rgba(201,168,76,.3);border-left:4px solid {GOLD};
     border-radius:13px;padding:14px 20px;margin:6px 0 14px;">
  <span style="font-size:10.5px;font-weight:800;letter-spacing:1.5px;color:#9a8c5e;">TOTAL CUOTAS / MES</span>
  <span style="font-family:{SERIF};font-size:30px;font-weight:600;color:{NAVY};">$ {tot_vis:,.0f}</span>
</div>""", unsafe_allow_html=True)

            for (cid, detalle_c, v_total, n, v_cuota, mon, primera, tarjeta_c, persona, coment, pagadas) in vis:
                pct = round(pagadas / n * 100) if n else 0
                chip_bg = "#e8f0fe" if persona == persona_1 else "rgba(201,168,76,.2)"
                chip_c  = BLUE     if persona == persona_1 else "#8a6d22"
                lbl = f"💳 {tarjeta_c}  ·  {detalle_c}  —  {mon} {v_cuota:,.0f}/mes  (cuota {pagadas}/{n})"
                with st.expander(lbl, expanded=False):
                    st.markdown(f"""
<div style="display:flex;justify-content:space-between;margin:6px 0 5px;">
  <span style="font-size:11px;font-weight:700;color:#6b7280;">cuota {pagadas} de {n}</span>
  <span style="font-size:11px;font-weight:700;color:#b7973f;">{pct}%</span>
</div>
<div style="height:7px;border-radius:5px;background:rgba(15,27,53,.08);overflow:hidden;">
  <div style="height:100%;background:linear-gradient(90deg,{GOLD},{GOLD_L});width:{pct}%;"></div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;margin-top:14px;">
  <div><div style="font-size:9.5px;font-weight:800;color:#9aa0ab;">VALOR TOTAL</div>
       <div style="font-family:{SERIF};font-size:17px;font-weight:600;">{mon} {v_total:,.0f}</div></div>
  <div><div style="font-size:9.5px;font-weight:800;color:#9aa0ab;">RESTA PAGAR</div>
       <div style="font-family:{SERIF};font-size:17px;font-weight:600;color:{GOLD_T};">{mon} {(n-pagadas)*v_cuota:,.0f}</div></div>
  <div><div style="font-size:9.5px;font-weight:800;color:#9aa0ab;">1RA CUOTA</div>
       <div style="font-size:13.5px;font-weight:600;">{primera}</div></div>
  <div><div style="font-size:9.5px;font-weight:800;color:#9aa0ab;">PAGA</div>
       <div style="font-size:13.5px;font-weight:600;"><span style="background:{chip_bg};color:{chip_c};padding:3px 9px;border-radius:7px;">{persona}</span></div></div>
</div>""", unsafe_allow_html=True)
                    if coment:
                        st.caption(coment)
                    if st.button("Eliminar", key=f"del_t_{cid}"):
                        db.eliminar_compra_tarjeta(cid)
                        st.rerun()

    with tab_nueva:
        with st.form(f"form_cuota_{st.session_state.form_cuota_n}", clear_on_submit=True):
            detalle = st.text_input("Qué compraste", placeholder="ej: Zapatillas, Mesa, Celular...")
            col_v, col_c, col_mon = st.columns([1.4, 1, 1])
            valor  = col_v.number_input("Valor total", min_value=0.0, step=100.0, format="%.0f")
            cuotas = col_c.number_input("Cuotas", min_value=1, max_value=48, step=1, value=1)
            moneda = col_mon.selectbox("Moneda", ["$", "U$S"])
            if cuotas > 0 and valor > 0:
                st.info(f"Valor por cuota: **{moneda} {valor/cuotas:,.0f}**")
            col_t, col_p = st.columns(2)
            tarjeta    = col_t.selectbox("Tarjeta", db.TARJETAS)
            pagado_por = col_p.selectbox("¿Quién?", personas)
            col_fc, col_mp = st.columns(2)
            fecha_compra      = col_fc.date_input("Fecha de compra", value=date.today())
            mes_primera_cuota = col_mp.selectbox("1ra cuota en", [f"{m} {anio_sel}" for m in db.MESES], index=datetime.today().month - 1)
            comentarios = st.text_input("Comentarios", placeholder="ej: con 20% descuento")
            enviado_cuota = st.form_submit_button("Guardar compra", use_container_width=True)
        if enviado_cuota:
            if valor <= 0 or not detalle:
                st.error("Completá el detalle y el valor.")
            else:
                db.agregar_compra_tarjeta(detalle, valor, cuotas, moneda, comentarios, str(fecha_compra), mes_primera_cuota, tarjeta, pagado_por, casa_id)
                st.success(f"✅ '{detalle}' guardada — {cuotas} cuota/s de {moneda} {valor/cuotas:,.0f}")
                st.session_state.form_cuota_n += 1
                st.rerun()


# ══════════════════════════════════════════════════════════════════════
# 5. GASTOS FIJOS
# ══════════════════════════════════════════════════════════════════════
elif pagina == "🔒 Gastos fijos":
    gastos_fijos = db.get_gastos_fijos(casa_id)
    excluidos_f  = db.get_fijos_excluidos_mes(anio_sel, mes_sel)
    activos      = [(gid, n, v, pg) for gid, n, v, _, pg in gastos_fijos]
    total        = sum(v for gid, _, v, _, _ in gastos_fijos if gid not in excluidos_f)
    n_activos    = sum(1 for gid, *_ in gastos_fijos if gid not in excluidos_f)

    st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 58%,{BLUE} 100%);
            border-radius:20px 20px 0 0;padding:24px 30px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;">
    <div>
      <div style="color:{GOLD_L};font-family:{DISPLAY};font-size:16px;font-weight:600;
           font-style:italic;letter-spacing:2px;text-transform:uppercase;">Editor · Gastos fijos</div>
      <div style="color:#fff;font-family:{DISPLAY};font-size:40px;font-weight:600;
           letter-spacing:.2px;line-height:1.05;">Gastos fijos mensuales</div>
      <div style="color:rgba(255,255,255,.5);font-size:12px;margin-top:3px;">
           Estos valores se dividen entre dos (c/u) · {n_activos} activos</div>
    </div>
    <div style="text-align:right;">
      <div style="color:rgba(255,255,255,.55);font-size:10px;font-weight:700;letter-spacing:2px;">TOTAL FIJOS</div>
      <div style="color:#fff;font-family:{SERIF};font-size:34px;font-weight:500;
           line-height:1.05;">$ {total:,.0f}</div>
      <div style="display:inline-flex;align-items:baseline;gap:6px;margin-top:5px;
           background:rgba(201,168,76,.22);border:1px solid rgba(245,208,96,.35);
           border-radius:9px;padding:4px 11px;">
        <span style="color:rgba(245,208,96,.8);font-size:9.5px;font-weight:800;letter-spacing:1px;">LE TOCA C/U</span>
        <span style="color:{GOLD_L};font-family:{SERIF};font-size:19px;font-weight:600;">$ {total/2:,.0f}</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with st.container(border=True):
        hc = st.columns([3, 2, 2, 2.2, 1.6, 1.2])
        for c, (txt, al, col) in zip(hc, [
            ("GASTO", "left", "#9aa0ab"), ("PAGA", "left", "#9aa0ab"),
            ("VALOR $", "right", "#9aa0ab"), ("LE TOCA C/U", "center", "#b7973f"),
            ("", "left", "#9aa0ab"), ("APLICA", "center", "#9aa0ab")]):
            c.markdown(f"<div style='font-size:9.5px;font-weight:800;letter-spacing:1.2px;"
                       f"color:{col};text-align:{al};padding-top:6px;'>{txt}</div>", unsafe_allow_html=True)

        for gid, nombre, valor, pagador in activos:
            excluido = gid in excluidos_f
            col_n, col_p, col_v, col_c, col_b, col_t = st.columns([3, 2, 2, 2.2, 1.6, 1.2])

            nombre_html = f"<s style='color:#9aa0ab;'>{nombre}</s>" if excluido else nombre
            col_n.markdown(f"<div style='font-size:17px;font-weight:600;color:{NAVY};"
                           f"padding-top:6px;'>{nombre_html}</div>", unsafe_allow_html=True)

            idx_p = 1 if pagador == persona_2 else 0
            nuevo_pagador = col_p.selectbox("Paga", personas, index=idx_p,
                                            key=f"pg_{gid}", label_visibility="collapsed", disabled=excluido)
            if nuevo_pagador != pagador:
                db.actualizar_pagador_fijo(gid, nuevo_pagador)
                st.rerun()

            nuevo_valor = col_v.number_input("Valor", value=float(valor), step=10.0, format="%.0f",
                                             key=f"fijo_{gid}", label_visibility="collapsed", disabled=excluido)

            if excluido:
                col_c.markdown("<div style='text-align:center;color:#b3b8c2;font-style:italic;"
                               "font-size:12px;padding-top:8px;'>no aplica</div>", unsafe_allow_html=True)
            else:
                col_c.markdown(f"<div style='text-align:center;font-family:{SERIF};font-size:22px;"
                               f"font-weight:600;color:{GOLD_T};padding-top:2px;'>$ {nuevo_valor/2:,.0f}</div>",
                               unsafe_allow_html=True)

            if col_b.button("Guardar", key=f"save_{gid}", disabled=excluido, use_container_width=True):
                db.actualizar_gasto_fijo(gid, nuevo_valor)
                st.success(f"✅ {nombre} actualizado")
                st.rerun()

            aplica = col_t.toggle("", value=not excluido, key=f"tog_{gid}", label_visibility="collapsed")
            if aplica == excluido:
                db.toggle_fijo_excluido(anio_sel, mes_sel, gid)
                st.rerun()

        st.markdown("---")
        st.markdown(f"<div style='font-size:10px;font-weight:800;letter-spacing:1.5px;"
                    f"color:#9aa0ab;'>AGREGAR GASTO FIJO</div>", unsafe_allow_html=True)
        with st.form("form_fijo", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 2, 1.4])
            nuevo_nombre = c1.text_input("Nombre", placeholder="ej: Internet, Gym…", label_visibility="collapsed")
            nuevo_monto  = c2.number_input("Valor", min_value=0.0, step=10.0, format="%.0f", label_visibility="collapsed")
            if c3.form_submit_button("Agregar", use_container_width=True):
                if nuevo_nombre and nuevo_monto > 0:
                    db.agregar_gasto_fijo(nuevo_nombre, nuevo_monto, casa_id)
                    st.success(f"✅ {nuevo_nombre} agregado")
                    st.rerun()
                else:
                    st.error("Completá nombre y valor.")


# ══════════════════════════════════════════════════════════════════════
# 6. PENDIENTES / LISTA DE COMPRAS
# ══════════════════════════════════════════════════════════════════════
elif pagina == "📝 Pendientes":
    ICON_CAT = {
        "Supermercado": "🛒", "Limpieza": "🧹", "Farmacia": "💊",
        "Ropa": "👕", "Hogar": "🏠", "Trámite": "📋", "Otro": "📌",
    }
    ICON_QUIEN = {"Ambos": "👫", persona_1: "🙋", persona_2: "🙋"}
    PRIO_COLOR = {"Alta": "#ef4444", "Normal": GOLD, "Baja": GRAY}

    st.markdown(
        f'<div style="background:{WHITE};border-radius:16px;padding:18px 22px;'
        f'box-shadow:0 2px 12px rgba(15,27,53,0.09);margin-bottom:16px;">'
        f'<div style="color:{NAVY};font-size:15px;font-weight:700;margin-bottom:10px;">✏️ Agregar a la lista</div>'
        f'</div>',
        unsafe_allow_html=True)

    with st.form("form_pendiente", clear_on_submit=True):
        descripcion = st.text_input("Qué necesitás", placeholder="ej: Nescafé, Detergente, Aceite...", label_visibility="collapsed")
        col_cat, col_pri, col_quien = st.columns(3)
        categoria  = col_cat.selectbox("Categoría", db.CATEGORIAS_PENDIENTES)
        prioridad  = col_pri.selectbox("Prioridad", db.PRIORIDADES)
        asignado_a = col_quien.selectbox("Para quién", ["Ambos"] + personas)
        enviado = st.form_submit_button("➕ Agregar", use_container_width=True, type="primary")

    if enviado:
        if descripcion.strip():
            db.agregar_pendiente(descripcion.strip(), categoria, prioridad, asignado_a, casa_id)
            st.rerun()
        else:
            st.error("Escribí algo primero.")

    pendientes = db.get_pendientes(solo_activos=False, casa_id=casa_id)
    activos    = [p for p in pendientes if not p[5]]
    hechos     = [p for p in pendientes if p[5]]

    from collections import defaultdict
    por_cat = defaultdict(list)
    for p in activos:
        por_cat[p[2]].append(p)

    if not activos:
        st.markdown(
            f'<div style="text-align:center;padding:40px;background:{WHITE};border-radius:16px;'
            f'box-shadow:0 2px 12px rgba(15,27,53,0.07);margin-top:8px;">'
            f'<div style="font-size:44px;">🛒</div>'
            f'<div style="color:{NAVY};font-size:18px;font-weight:700;margin-top:10px;">Lista vacía</div>'
            f'<div style="color:{GRAY};font-size:13px;margin-top:4px;">Agregá lo que necesitás comprar</div>'
            f'</div>',
            unsafe_allow_html=True)
    else:
        total_items = len(activos)
        st.markdown(
            f'<div style="color:{GRAY};font-size:13px;margin-bottom:10px;">'
            f'{total_items} item{"s" if total_items != 1 else ""} pendiente{"s" if total_items != 1 else ""}</div>',
            unsafe_allow_html=True)

        for cat, items in por_cat.items():
            icono = ICON_CAT.get(cat, "📌")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'margin:14px 0 6px;padding-bottom:4px;border-bottom:2px solid {GOLD};">'
                f'<span style="font-size:18px;">{icono}</span>'
                f'<span style="color:{NAVY};font-size:14px;font-weight:700;letter-spacing:0.5px;">{cat.upper()}</span>'
                f'<span style="color:{GRAY};font-size:12px;">({len(items)})</span>'
                f'</div>',
                unsafe_allow_html=True)

            for pid, desc, cat2, prio, quien, _, fecha in items:
                pc = PRIO_COLOR.get(prio, GRAY)
                iq = ICON_QUIEN.get(quien, "👫")
                editando = st.session_state.get("edit_pid") == pid

                if editando:
                    nuevo = st.text_input("Editar", value=desc, key=f"inp_{pid}", label_visibility="collapsed")
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("💾 Guardar", key=f"save_{pid}", use_container_width=True, type="primary"):
                            if nuevo.strip():
                                db.actualizar_pendiente(pid, nuevo.strip())
                            st.session_state.pop("edit_pid", None)
                            st.rerun()
                    with c2:
                        if st.button("Cancelar", key=f"cancel_{pid}", use_container_width=True):
                            st.session_state.pop("edit_pid", None)
                            st.rerun()
                else:
                    col_item, col_b1, col_b2, col_b3 = st.columns([6, 2, 2, 2])
                    with col_item:
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:10px;'
                            f'padding:9px 12px;background:{WHITE};border-radius:10px;'
                            f'border-left:4px solid {pc};margin-bottom:4px;'
                            f'box-shadow:0 1px 4px rgba(15,27,53,0.06);">'
                            f'<span style="color:{NAVY};font-size:14px;flex:1;">{desc}</span>'
                            f'<span style="color:{GRAY};font-size:12px;">{iq} {quien}</span>'
                            f'</div>',
                            unsafe_allow_html=True)
                    with col_b1:
                        if st.button("✏️", key=f"edit_{pid}", use_container_width=True, help="Editar"):
                            st.session_state["edit_pid"] = pid
                            st.rerun()
                    with col_b2:
                        if st.button("✓", key=f"check_{pid}", use_container_width=True, help="Listo"):
                            db.marcar_pendiente(pid, True)
                            st.rerun()
                    with col_b3:
                        if st.button("✕", key=f"del_p_{pid}", use_container_width=True, help="Eliminar"):
                            db.eliminar_pendiente(pid)
                            st.rerun()

    if hechos:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"✅ Ya comprado / hecho ({len(hechos)})"):
            for pid, desc, cat, prio, quien, _, fecha in hechos:
                ic = ICON_CAT.get(cat, "📌")
                col_txt, col_d = st.columns([11, 1])
                with col_txt:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #f0f0f0;">'
                        f'<span style="font-size:15px;opacity:0.35;">{ic}</span>'
                        f'<span style="color:{GRAY};text-decoration:line-through;font-size:14px;">{desc}</span>'
                        f'<span style="color:#d1d5db;font-size:11px;margin-left:4px;">— {quien}</span>'
                        f'</div>',
                        unsafe_allow_html=True)
                with col_d:
                    if st.button("↩", key=f"undo_{pid}", help="Deshacer"):
                        db.marcar_pendiente(pid, False)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# 7. GASTOS PERSONALES
# ══════════════════════════════════════════════════════════════════════
elif pagina == "💰 Personal":

    if "persona_personal" not in st.session_state:
        st.session_state.persona_personal = None

    st.markdown(f"""
    <div style="background:linear-gradient(140deg,{NAVY},{NAVY2} 70%,{BLUE});
         border-radius:18px;padding:28px 30px 22px;margin-bottom:20px;
         box-shadow:0 6px 24px rgba(15,27,53,.22);">
      <div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:3px;margin-bottom:6px;">GASTOS PERSONALES</div>
      <div style="color:#fff;font-family:{DISPLAY};font-size:46px;font-weight:600;line-height:1;">¿De quién?</div>
      <div style="color:rgba(255,255,255,.55);font-size:13px;margin-top:6px;">Elegí tu nombre para ver y cargar tus gastos personales.</div>
    </div>
    """, unsafe_allow_html=True)

    col_m, col_g = st.columns(2)
    persona_sel = st.session_state.persona_personal
    with col_m:
        if st.button(
            f"💙  {persona_1}",
            use_container_width=True,
            type="primary" if persona_sel == persona_1 else "secondary",
            key="btn_p1_personal",
        ):
            st.session_state.persona_personal = persona_1
            st.rerun()
    with col_g:
        if st.button(
            f"💛  {persona_2}",
            use_container_width=True,
            type="primary" if persona_sel == persona_2 else "secondary",
            key="btn_p2_personal",
        ):
            st.session_state.persona_personal = persona_2
            st.rerun()

    persona_sel = st.session_state.persona_personal

    if persona_sel:
        color_persona    = BLUE  if persona_sel == persona_1 else GOLD
        color_persona_bg = "#e8f0fe" if persona_sel == persona_1 else GOLD_P

        st.markdown("<br>", unsafe_allow_html=True)

        total_personal = db.get_total_personal_mes(anio_sel, mes_sel, persona_sel, casa_id)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{color_persona},{NAVY});
             border-radius:14px;padding:20px 24px;margin-bottom:18px;
             box-shadow:0 4px 16px rgba(15,27,53,.18);">
          <div style="color:rgba(255,255,255,.65);font-size:10px;font-weight:800;letter-spacing:2.5px;">
            GASTOS PERSONALES · {mes_nombre.upper()} {anio_sel}
          </div>
          <div style="color:#fff;font-family:{SERIF};font-size:44px;font-weight:600;line-height:1.05;margin-top:6px;">
            $ {total_personal:,.0f}
          </div>
          <div style="color:rgba(255,255,255,.5);font-size:12px;margin-top:2px;">{persona_sel} · solo uso personal</div>
        </div>
        """, unsafe_allow_html=True)

        tab_ver_p, tab_nuevo_p = st.tabs(["Ver gastos", "Nuevo gasto"])

        with tab_ver_p:
            gastos_p = db.get_gastos_personales_mes(anio_sel, mes_sel, persona_sel, casa_id)
            if not gastos_p:
                st.markdown(f"""
                <div style="text-align:center;padding:36px 20px;background:{color_persona_bg};
                     border-radius:14px;border:1px dashed {color_persona};">
                  <div style="font-size:32px;margin-bottom:10px;">💸</div>
                  <div style="color:{NAVY};font-size:15px;font-weight:600;">Sin gastos personales en {mes_nombre}</div>
                  <div style="color:{GRAY};font-size:13px;margin-top:4px;">Cargá uno desde "Nuevo gasto"</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                por_cat_p = {}
                for gid, fecha_g, cat_g, desc_g, monto_g, coment_g in gastos_p:
                    por_cat_p.setdefault(cat_g, []).append((gid, fecha_g, desc_g, monto_g, coment_g))

                for cat_g, items in por_cat_p.items():
                    subtotal = sum(m for _, _, _, m, _ in items)
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         padding:6px 12px;margin:10px 0 4px;
                         border-left:3px solid {color_persona};border-radius:0 6px 6px 0;
                         background:rgba(0,0,0,.03);">
                      <span style="color:{NAVY};font-size:12px;font-weight:700;letter-spacing:.5px;">{cat_g.upper()}</span>
                      <span style="color:{color_persona};font-size:13px;font-weight:700;">$ {subtotal:,.0f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    for gid, fecha_g, desc_g, monto_g, coment_g in items:
                        col_info, col_del = st.columns([11, 1])
                        with col_info:
                            nota = f' <span style="color:{GRAY};font-size:11px;">— {coment_g}</span>' if coment_g else ""
                            st.markdown(
                                f'<div style="display:grid;grid-template-columns:1fr auto;gap:10px;'
                                f'align-items:center;padding:9px 12px;margin-bottom:3px;'
                                f'background:#fff;border-radius:10px;'
                                f'box-shadow:0 1px 4px rgba(15,27,53,.06);">'
                                f'<div><div style="color:{NAVY};font-size:13px;font-weight:600;">{desc_g}{nota}</div>'
                                f'<div style="color:{GRAY};font-size:11px;margin-top:1px;">{fecha_g}</div></div>'
                                f'<span style="color:{color_persona};font-size:15px;font-weight:700;">$ {monto_g:,.0f}</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        with col_del:
                            if st.button("✕", key=f"del_gp_{gid}", help="Eliminar"):
                                db.eliminar_gasto_personal(gid)
                                st.rerun()

        with tab_nuevo_p:
            if "form_personal_n" not in st.session_state:
                st.session_state.form_personal_n = 0

            with st.form(f"form_personal_{st.session_state.form_personal_n}", clear_on_submit=True):
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{NAVY},{NAVY2});border-radius:14px;
                     padding:18px 20px 10px;margin-bottom:16px;">
                  <div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:2px;">NUEVO GASTO PERSONAL</div>
                  <div style="color:#fff;font-family:{DISPLAY};font-size:28px;font-weight:600;margin-top:4px;">{persona_sel}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                fecha_p = col1.date_input("Fecha", value=date.today(), key="fp_fecha")
                cat_p   = col2.selectbox("Categoría", db.CATEGORIAS_PERSONAL, key="fp_cat")
                desc_p  = st.text_input("Descripción", placeholder="ej: zapatillas, cena con amigas…", key="fp_desc")
                monto_p = st.number_input("Monto ($)", min_value=0.0, step=10.0, format="%.0f", key="fp_monto")
                coment_p = st.text_input("Comentarios (opcional)", placeholder="ej: en oferta, cuotas…", key="fp_coment")
                enviado_p = st.form_submit_button("Guardar gasto personal", use_container_width=True, type="primary")

            if enviado_p:
                if monto_p <= 0 or not desc_p.strip():
                    st.error("Completá la descripción y el monto.")
                else:
                    db.agregar_gasto_personal(str(fecha_p), cat_p, desc_p.strip(), persona_sel, monto_p, coment_p.strip(), casa_id)
                    st.success(f"✅ '{desc_p}' guardado — $ {monto_p:,.0f}")
                    st.session_state.form_personal_n += 1
                    st.rerun()
