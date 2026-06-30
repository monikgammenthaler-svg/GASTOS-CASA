import streamlit as st
import pandas as pd
from datetime import date, datetime
import db

db.init_db()

st.set_page_config(
    page_title="Gastos de la Casa",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Paleta: Azul marino + Dorado + Blanco ────────────────────────────
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
    /* Fondo general */
    .stApp {{ background-color: #fde8f0; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {NAVY2} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
    [data-testid="stSidebar"] .stRadio label {{ color: {WHITE} !important; }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.15) !important; }}
    [data-testid="stSidebar"] select {{
        background: rgba(255,255,255,0.1) !important;
        color: {WHITE} !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }}
    /* Botón primario */
    .stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, {GOLD}, {GOLD_L}) !important;
        color: {NAVY} !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {GOLD_L}, {GOLD}) !important;
        transform: translateY(-1px);
    }}
    /* Títulos */
    h1 {{ color: {NAVY} !important; }}
    h2, h3 {{ color: {NAVY2} !important; }}
    /* Separador */
    hr {{ border-color: #e2e8f0 !important; }}
    /* Tags */
    .tag-moni  {{ background:{BLUE};  color:{WHITE}; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    .tag-guille {{ background:{GOLD}; color:{NAVY};  border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    /* Card genérica */
    .g-card {{
        background: {WHITE};
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(15,27,53,0.08);
        margin-bottom: 16px;
    }}
    div[data-testid="stSidebarNav"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:28px;font-weight:800;letter-spacing:1px;padding:8px 0 4px;color:{GOLD}'>🏠 Gastos Casa</div>", unsafe_allow_html=True)
    st.markdown("---")
    pagina = st.radio(
        "Menú",
        ["📊 Resumen del mes", "➕ Cargar gasto", "📋 Ver gastos", "💳 Cuotas tarjeta", "🔒 Gastos fijos", "📝 Pendientes"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    anos = list(range(2024, 2029))
    anio_sel = st.selectbox("Año", anos, index=anos.index(datetime.today().year) if datetime.today().year in anos else 0)
    mes_nombre = st.selectbox("Mes", db.MESES, index=datetime.today().month - 1)
    mes_sel = db.MESES.index(mes_nombre) + 1

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

# ══════════════════════════════════════════════════════════════════════
# 1. RESUMEN DEL MES
# ══════════════════════════════════════════════════════════════════════
if pagina == "📊 Resumen del mes":
    nombre_mes = db.MESES[mes_sel - 1]

    mes_ant_num   = mes_sel - 1 if mes_sel > 1 else 12
    anio_ant      = anio_sel if mes_sel > 1 else anio_sel - 1
    nombre_mes_ant = db.MESES[mes_ant_num - 1]

    mes_sig_num   = mes_sel + 1 if mes_sel < 12 else 1
    nombre_mes_sig = db.MESES[mes_sig_num - 1]

    st.markdown(f"<h1 style='margin-bottom:4px;'>{nombre_mes} {anio_sel}</h1>", unsafe_allow_html=True)
    st.markdown(
        banner(f"Los gastos de <b>{nombre_mes}</b> se pagan con el sueldo de <b>principios de {nombre_mes_sig}</b>.", "gold"),
        unsafe_allow_html=True,
    )

    gastos_fijos      = db.get_gastos_fijos()
    excluidos_res     = db.get_fijos_excluidos_mes(anio_sel, mes_sel)
    moni_fijos        = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == "Moni")
    guille_fijos      = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == "Guille")
    total_fijos_base  = moni_fijos + guille_fijos
    oca_total, oca_items = db.get_total_oca_compartida_mes(anio_sel, mes_sel)
    total_fijos       = total_fijos_base + oca_total
    total_por_persona = db.get_totales_mes(anio_sel, mes_sel)
    cuotas_persona, cuotas_items = db.get_total_cuotas_activas_mes(anio_sel, mes_sel)
    moni_vars         = total_por_persona.get("Moni", 0)
    moni_cuotas       = cuotas_persona.get("Moni", 0)
    guille_vars       = total_por_persona.get("Guille", 0)
    guille_cuotas     = cuotas_persona.get("Guille", 0)
    guille_pago       = guille_vars + guille_cuotas + guille_fijos
    total_variable    = sum(total_por_persona.values()) + sum(cuotas_persona.values())
    total_general     = total_fijos + total_variable
    moni_pago         = moni_vars + moni_cuotas + moni_fijos
    mitad             = total_general / 2
    balance           = moni_pago - mitad

    # Banner "a pagar este mes" (datos del mes anterior)
    tot_ant_persona    = db.get_totales_mes(anio_ant, mes_ant_num)
    cuotas_ant, _      = db.get_total_cuotas_activas_mes(anio_ant, mes_ant_num)
    total_variable_ant = sum(tot_ant_persona.values()) + sum(cuotas_ant.values())
    total_ant          = total_fijos + total_variable_ant
    moni_ant           = tot_ant_persona.get("Moni", 0) + cuotas_ant.get("Moni", 0) + total_fijos_base
    balance_ant        = moni_ant - total_ant / 2
    if total_ant > 0:
        if abs(balance_ant) < 1:
            deuda_txt = "Estaban al dia"
            tip = "success"
        elif balance_ant > 0:
            deuda_txt = f"<b>Guille le paga a Moni $ {balance_ant:,.0f}</b>"
            tip = "success"
        else:
            deuda_txt = f"<b>Moni le paga a Guille $ {abs(balance_ant):,.0f}</b>"
            tip = "info"
        st.markdown(
            banner(f"A pagar ESTE mes (gastos de {nombre_mes_ant}): Total $ {total_ant:,.0f}  &nbsp;·&nbsp;  {deuda_txt}", tip),
            unsafe_allow_html=True,
        )

    # ── TARJETA LIQUIDACIÓN ──────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{NAVY},{NAVY2});border-radius:18px;padding:28px 32px 20px;margin:8px 0 16px;box-shadow:0 4px 20px rgba(15,27,53,0.25);">
        <div style="color:{GOLD};font-size:11px;font-weight:700;letter-spacing:2px;margin-bottom:20px;">LIQUIDACIÓN DEL MES</div>
        <div style="display:flex;justify-content:space-around;align-items:center;gap:12px;">
            <div style="text-align:center;flex:1;">
                <div style="background:rgba(45,107,196,0.3);border-radius:12px;padding:16px 12px;">
                    <div style="color:#93c5fd;font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:8px;">MONI pagó</div>
                    <div style="color:{WHITE};font-size:30px;font-weight:900;line-height:1;">$ {moni_pago:,.0f}</div>
                    <div style="color:#94a3b8;font-size:11px;margin-top:6px;">le corresponde $ {mitad:,.0f}</div>
                </div>
            </div>
            <div style="color:{GOLD};font-size:22px;opacity:0.6;">⇄</div>
            <div style="text-align:center;flex:1;">
                <div style="background:rgba(201,168,76,0.2);border-radius:12px;padding:16px 12px;">
                    <div style="color:{GOLD_L};font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:8px;">GUILLE pagó</div>
                    <div style="color:{WHITE};font-size:30px;font-weight:900;line-height:1;">$ {guille_pago:,.0f}</div>
                    <div style="color:#94a3b8;font-size:11px;margin-top:6px;">le corresponde $ {mitad:,.0f}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESULTADO ────────────────────────────────────────────────────
    if abs(balance) < 1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#14532d,#166534);border-radius:14px;padding:20px;text-align:center;margin-bottom:20px;">
            <div style="color:#86efac;font-size:13px;font-weight:700;letter-spacing:1px;">ESTAN AL DIA</div>
            <div style="color:{WHITE};font-size:18px;margin-top:4px;">Los dos gastaron lo mismo este mes</div>
        </div>""", unsafe_allow_html=True)
    elif balance > 0:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{NAVY2},{BLUE});border-radius:14px;padding:22px;text-align:center;margin-bottom:20px;box-shadow:0 4px 16px rgba(45,107,196,0.3);">
            <div style="color:{GOLD_L};font-size:12px;font-weight:700;letter-spacing:2px;margin-bottom:6px;">GUILLE LE DEBE A MONI</div>
            <div style="color:{WHITE};font-size:42px;font-weight:900;line-height:1.1;">$ {balance:,.0f}</div>
            <div style="color:#94a3b8;font-size:12px;margin-top:6px;">para quedar iguales</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#78350f,#92400e);border-radius:14px;padding:22px;text-align:center;margin-bottom:20px;box-shadow:0 4px 16px rgba(201,168,76,0.3);">
            <div style="color:{GOLD_L};font-size:12px;font-weight:700;letter-spacing:2px;margin-bottom:6px;">MONI LE DEBE A GUILLE</div>
            <div style="color:{WHITE};font-size:42px;font-weight:900;line-height:1.1;">$ {abs(balance):,.0f}</div>
            <div style="color:#fde68a;font-size:12px;margin-top:6px;">para quedar iguales</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── TOTALES ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    for col, label, valor in [(col1,"Total del mes",total_general),(col2,"Variables",total_variable),(col3,"Fijos",total_fijos)]:
        col.markdown(f"""
        <div class="g-card" style="text-align:center;border-top:3px solid {GOLD};">
            <div style="color:{GRAY};font-size:12px;font-weight:600;letter-spacing:1px;">{label.upper()}</div>
            <div style="color:{NAVY};font-size:24px;font-weight:800;margin-top:4px;">$ {valor:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── POR CATEGORÍA ────────────────────────────────────────────────
    por_cat = db.get_por_categoria_mes(anio_sel, mes_sel)
    if por_cat:
        st.markdown(f"<h3>Por categoría</h3>", unsafe_allow_html=True)
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
    por_tipo = db.get_por_tipo_mes(anio_sel, mes_sel)
    if por_tipo:
        st.markdown(f"<h3>Por tipo de pago</h3>", unsafe_allow_html=True)
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

    def tarjeta_compromisos(filas, total_fijos, moni_fijos, guille_fijos):
        cu_total = total_fijos / 2
        n_filas = len(filas)
        th = (
            f'<div style="display:grid;grid-template-columns:1fr 76px 100px 92px;gap:10px;'
            f'align-items:center;padding:12px 10px 9px;border-bottom:1px solid rgba(15,27,53,.1);">'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">GASTO</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">PAGA</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">TOTAL</span>'
            f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">C/U</span>'
            f'</div>'
        )
        def _fila(nombre, valor, pagado_por, pagado=False):
            if pagado_por == "Moni":
                badge = (f'<span style="background:#e8f0fe;color:{BLUE};font-size:9.5px;font-weight:800;'
                         f'letter-spacing:.5px;padding:3px 9px;border-radius:20px;">MONI</span>')
            else:
                badge = (f'<span style="background:rgba(201,168,76,.2);color:#8a6d22;font-size:9.5px;'
                         f'font-weight:800;letter-spacing:.5px;padding:3px 9px;border-radius:20px;">GUILLE</span>')
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
                f'<div style="display:grid;grid-template-columns:1fr 76px 100px 92px;gap:10px;'
                f'align-items:center;padding:11px 10px;border-radius:10px;opacity:{op};">'
                f'<div style="display:flex;align-items:center;gap:11px;min-width:0;">{check}'
                f'<span style="color:{NAVY};font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;'
                f'text-overflow:ellipsis;text-decoration:{deco};">{nombre}</span></div>'
                f'<div>{badge}</div>'
                f'<span style="text-align:right;color:{NAVY};font-family:{SERIF};font-size:18px;font-weight:500;'
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
            f'letter-spacing:-1px;line-height:1;font-variant-numeric:tabular-nums;">$ {total_fijos:,.0f}</div>'
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
            f'<div style="color:rgba(255,255,255,.65);font-size:10px;font-weight:700;letter-spacing:.5px;">PAGA MONI</div>'
            f'<div style="color:#fff;font-family:{SERIF};font-size:19px;font-weight:500;font-variant-numeric:tabular-nums;">$ {moni_fijos:,.0f}</div>'
            f'</div>'
            f'<div style="flex:1;background:rgba(201,168,76,.28);border-radius:11px;padding:9px 13px;">'
            f'<div style="color:rgba(255,255,255,.65);font-size:10px;font-weight:700;letter-spacing:.5px;">PAGA GUILLE</div>'
            f'<div style="color:{GOLD_L};font-family:{SERIF};font-size:19px;font-weight:500;font-variant-numeric:tabular-nums;">$ {guille_fijos:,.0f}</div>'
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
    for d, vc, cn, tc in oca_items:
        filas_card.append((f"OCA VISA: {d} ({cn}/{tc})", vc, "Guille"))
    guille_fijos_card = guille_fijos + oca_total
    st.markdown(
        tarjeta_compromisos(filas_card, total_fijos, moni_fijos, guille_fijos_card),
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

    if cuotas_items:
        cuotas_html_parts = []
        for p, t, d, vc, cn, tc in cuotas_items:
            bg = "#eef3fc" if p == "Moni" else "rgba(201,168,76,.1)"
            col = BLUE if p == "Moni" else GOLD
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
    st.markdown(f"<h1>Cargar gasto</h1>", unsafe_allow_html=True)

    tiene_cuotas = st.checkbox("¿Pago en cuotas?")

    with st.form("form_gasto", clear_on_submit=True):
        col_f, col_p = st.columns([2, 1])
        fecha      = col_f.date_input("Fecha", value=date.today())
        pagado_por = col_p.selectbox("¿Quién pagó?", db.PERSONAS)

        col_cat, col_tipo = st.columns(2)
        categoria = col_cat.selectbox("Categoría", db.CATEGORIAS)
        tipo      = col_tipo.selectbox("Tipo de pago", db.TIPOS_PAGO)

        descripcion = st.text_input("Descripción", placeholder="ej: Super Paulino, taxi, farmacia...")
        monto       = st.number_input("Monto total ($)", min_value=0.0, step=10.0, format="%.0f")

        num_cuotas   = 1
        tarjeta_cuota = None
        if tiene_cuotas:
            st.markdown("---")
            col_nc, col_tc = st.columns(2)
            num_cuotas    = col_nc.number_input("Cantidad de cuotas", min_value=2, max_value=48, step=1, value=3)
            tarjeta_cuota = col_tc.selectbox("Tarjeta", db.TARJETAS)
            if monto > 0:
                st.info(f"Valor por cuota: $ {monto / num_cuotas:,.0f}  ·  {int(num_cuotas)} meses desde {db.MESES[fecha.month - 1]} {fecha.year}")

        comentarios = st.text_input("Comentarios (opcional)", placeholder="ej: con 20% descuento")
        enviado = st.form_submit_button("Guardar gasto", use_container_width=True, type="primary")

    if enviado:
        if monto <= 0:
            st.error("El monto debe ser mayor a cero.")
        elif tiene_cuotas:
            db.agregar_gasto_en_cuotas(str(fecha), categoria, descripcion, pagado_por, tipo, tarjeta_cuota, monto, int(num_cuotas))
            valor_cuota = round(monto / num_cuotas, 0)
            st.success(f"✅ {int(num_cuotas)} cuotas de $ {valor_cuota:,.0f} guardadas.")
            st.balloons()
        else:
            db.agregar_gasto(str(fecha), categoria, descripcion, pagado_por, comentarios, tipo, monto)
            st.success(f"✅ Gasto de $ {monto:,.0f} guardado.")
            st.balloons()


# ══════════════════════════════════════════════════════════════════════
# 3. VER GASTOS
# ══════════════════════════════════════════════════════════════════════
elif pagina == "📋 Ver gastos":
    nombre_mes = db.MESES[mes_sel - 1]
    st.markdown(f"<h1>Gastos de {nombre_mes} {anio_sel}</h1>", unsafe_allow_html=True)

    gastos = db.get_gastos_mes(anio_sel, mes_sel)

    if not gastos:
        st.info("No hay gastos cargados para este mes.")
    else:
        cols_filter = st.columns(3)
        filtro_persona = cols_filter[0].selectbox("Persona", ["Todos"] + db.PERSONAS)
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
            tag = f"<span class='tag-moni'>MONI</span>" if row['Pagado por'] == "Moni" else f"<span class='tag-guille'>GUILLE</span>"
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
    st.markdown(f"<h1>Cuotas con tarjeta</h1>", unsafe_allow_html=True)

    tab_ver, tab_nueva = st.tabs(["Ver cuotas", "Nueva compra"])

    with tab_ver:
        compras = db.get_compras_tarjeta()
        if not compras:
            st.info("No hay compras en cuotas cargadas.")
        else:
            filtro_tarj = st.selectbox("Filtrar por tarjeta", ["Todas"] + db.TARJETAS)
            df = pd.DataFrame(compras, columns=["id","Detalle","Valor total","Cuotas","Valor cuota","Moneda","1ra cuota en","Tarjeta","Pagado por","Comentarios","Fecha compra"])
            if filtro_tarj != "Todas":
                df = df[df["Tarjeta"] == filtro_tarj]

            total_cuotas = df["Valor cuota"].sum()
            st.markdown(f"""
            <div class="g-card" style="border-left:4px solid {GOLD};margin-bottom:16px;">
                <span style="color:{GRAY};font-size:12px;">TOTAL CUOTAS / MES</span><br>
                <span style="color:{NAVY};font-size:26px;font-weight:800;">$ {total_cuotas:,.0f}</span>
            </div>""", unsafe_allow_html=True)

            for _, row in df.iterrows():
                with st.expander(f"💳 {row['Tarjeta'] or '—'}  |  {row['Detalle']}  —  $ {row['Valor cuota']:,.0f}/mes ({row['Cuotas']} cuotas)"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Valor total:** {row['Moneda']} {row['Valor total']:,.0f}")
                    c2.write(f"**1ra cuota:** {row['1ra cuota en']}")
                    c1.write(f"**Pagado por:** {row['Pagado por']}")
                    c2.write(f"**Tarjeta:** {row['Tarjeta']}")
                    if row['Comentarios']:
                        st.caption(row['Comentarios'])
                    if st.button("Eliminar", key=f"del_t_{row['id']}"):
                        db.eliminar_compra_tarjeta(row['id'])
                        st.rerun()

    with tab_nueva:
        st.subheader("Registrar compra en cuotas")
        with st.form("form_cuota", clear_on_submit=True):
            detalle = st.text_input("Qué compraste", placeholder="ej: Zapatillas, Mesa, Celular...")
            col_v, col_c, col_mon = st.columns(3)
            valor  = col_v.number_input("Valor total", min_value=0.0, step=100.0, format="%.0f")
            cuotas = col_c.number_input("Cuotas", min_value=1, max_value=48, step=1, value=1)
            moneda = col_mon.selectbox("Moneda", ["$", "U$S"])
            if cuotas > 0 and valor > 0:
                st.info(f"Valor por cuota: {moneda} {valor/cuotas:,.0f}")
            col_t, col_p = st.columns(2)
            tarjeta    = col_t.selectbox("Tarjeta", db.TARJETAS)
            pagado_por = col_p.selectbox("¿Quién?", db.PERSONAS)
            col_fc, col_mp = st.columns(2)
            fecha_compra      = col_fc.date_input("Fecha de compra", value=date.today())
            mes_primera_cuota = col_mp.selectbox("1ra cuota en", [f"{m} {anio_sel}" for m in db.MESES], index=datetime.today().month - 1)
            comentarios = st.text_input("Comentarios", placeholder="ej: con 20% descuento")
            enviado = st.form_submit_button("Guardar", use_container_width=True, type="primary")
        if enviado:
            if valor <= 0 or not detalle:
                st.error("Completá el detalle y el valor.")
            else:
                db.agregar_compra_tarjeta(detalle, valor, cuotas, moneda, comentarios, str(fecha_compra), mes_primera_cuota, tarjeta, pagado_por)
                st.success(f"✅ '{detalle}' guardada — {cuotas} cuota/s de {moneda} {valor/cuotas:,.0f}")


# ══════════════════════════════════════════════════════════════════════
# 5. GASTOS FIJOS
# ══════════════════════════════════════════════════════════════════════
elif pagina == "🔒 Gastos fijos":
    st.markdown(f"""
<style>
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input {{
    border-radius: 9px !important;
    border: 1px solid rgba(15,27,53,.14) !important;
    background: #fff !important;
}}
div[data-testid="stNumberInput"] input {{
    font-family: {SERIF} !important;
    font-size: 16px !important;
    text-align: right !important;
    color: {NAVY} !important;
}}
div[data-testid="column"] button[kind="secondary"] {{
    border: 1.5px solid rgba(45,107,196,.4) !important;
    color: {BLUE} !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}}
</style>
""", unsafe_allow_html=True)

    gastos_fijos = db.get_gastos_fijos()
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

        idx_p = 1 if pagador == "Guille" else 0
        nuevo_pagador = col_p.selectbox("Paga", ["Moni", "Guille"], index=idx_p,
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
                db.agregar_gasto_fijo(nuevo_nombre, nuevo_monto)
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
    ICON_QUIEN = {"Ambos": "👫", "Moni": "👩", "Guille": "👨"}
    PRIO_COLOR = {"Alta": "#ef4444", "Normal": GOLD, "Baja": GRAY}

    # ── Formulario rápido ────────────────────────────────────────────
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
        asignado_a = col_quien.selectbox("Para quién", ["Ambos"] + db.PERSONAS)
        enviado = st.form_submit_button("➕ Agregar", use_container_width=True, type="primary")

    if enviado:
        if descripcion.strip():
            db.agregar_pendiente(descripcion.strip(), categoria, prioridad, asignado_a)
            st.rerun()
        else:
            st.error("Escribí algo primero.")

    # ── Lista ────────────────────────────────────────────────────────
    pendientes = db.get_pendientes(solo_activos=False)
    activos    = [p for p in pendientes if not p[5]]
    hechos     = [p for p in pendientes if p[5]]

    # Agrupar por categoría
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
            # Encabezado de categoría
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
                    col_item, col_b1, col_b2, col_b3 = st.columns([10, 1, 1, 1])
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

    # ── Comprados ────────────────────────────────────────────────────
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
