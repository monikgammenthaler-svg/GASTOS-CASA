import streamlit as st
import pandas as pd
import db
from estilos import *


def _stat(label, valor, acento):
    return (
        f'<div style="background:#faf8f4;border:1px solid rgba(15,27,53,.07);'
        f'border-top:3px solid {acento};border-radius:13px;padding:14px 8px;text-align:center;">'
        f'<div style="color:#9aa0ab;font-size:9px;font-weight:800;letter-spacing:1px;">{label}</div>'
        f'<div style="color:{NAVY};font-family:{SERIF};font-size:clamp(16px,5vw,28px);'
        f'font-weight:600;margin-top:4px;">$ {valor:,.0f}</div></div>'
    )


def _tarjeta_compromisos(filas, total_f, p1_f, p2_f, persona_1, persona_2):
    cu_total = total_f / 2
    n_filas  = len(filas)

    th = (
        f'<div style="display:grid;grid-template-columns:minmax(80px,1fr) 52px 80px 62px;gap:6px;'
        f'align-items:center;padding:12px 10px 9px;border-bottom:1px solid rgba(15,27,53,.1);">'
        f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">GASTO</span>'
        f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;">PAGA</span>'
        f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">TOTAL</span>'
        f'<span style="font-size:9.5px;font-weight:800;letter-spacing:1.2px;color:#9aa0ab;text-align:right;">C/U</span>'
        f'</div>'
    )

    def _fila(nombre, valor, pagado_por, pagado=False):
        if pagado_por == persona_1:
            badge = (f'<span style="background:#e8f0fe;color:{BLUE};font-size:9px;font-weight:800;'
                     f'letter-spacing:0;padding:3px 6px;border-radius:20px;white-space:nowrap;">'
                     f'{persona_1.upper()}</span>')
        else:
            badge = (f'<span style="background:rgba(201,168,76,.2);color:#8a6d22;font-size:9px;'
                     f'font-weight:800;letter-spacing:0;padding:3px 6px;border-radius:20px;white-space:nowrap;">'
                     f'{persona_2.upper()}</span>')
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
            f'<div style="display:grid;grid-template-columns:minmax(80px,1fr) 52px 80px 62px;gap:6px;'
            f'align-items:center;padding:11px 10px;border-radius:10px;opacity:{op};">'
            f'<div style="display:flex;align-items:center;gap:8px;min-width:0;overflow:hidden;">{check}'
            f'<span style="color:{NAVY};font-size:13px;font-weight:500;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;text-decoration:{deco};">{nombre}</span></div>'
            f'<div style="overflow:hidden;">{badge}</div>'
            f'<span style="text-align:right;color:{NAVY};font-family:{SERIF};font-size:14px;font-weight:500;'
            f'font-variant-numeric:tabular-nums;text-decoration:{deco};">$ {valor:,.0f}</span>'
            f'<span style="text-align:right;color:#b7973f;font-size:12.5px;font-weight:700;'
            f'font-variant-numeric:tabular-nums;">$ {valor/2:,.0f}</span>'
            f'</div>'
        )

    filas_html = "".join(_fila(f[0], f[1], f[2], f[3] if len(f) > 3 else False) for f in filas)

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


def _render_hero(mes_nombre, anio_sel, p1_pago, p2_pago, corresponde_cu,
                 deudor, acreedor, balance, persona_1, persona_2,
                 total_ant=None, balance_ant=None, deudor_ant=None, acreedor_ant=None):
    p1_pct = round(p1_pago / (p1_pago + p2_pago) * 100) if (p1_pago + p2_pago) else 50

    st.markdown(f"""
<div style="padding:28px 16px 8px;">
  <div style="color:#b7973f;font-family:{DISPLAY};font-size:17px;font-weight:600;
       font-style:italic;letter-spacing:3px;text-transform:uppercase;">Resumen del mes</div>
  <div style="color:{NAVY};font-family:{DISPLAY};font-size:clamp(38px,11vw,72px);font-weight:600;
       line-height:.98;margin-top:4px;letter-spacing:-.5px;">{mes_nombre} {anio_sel}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:0 16px;">
  <div style="display:flex;align-items:center;gap:10px;background:#faf8f4;border-left:3px solid {GOLD};
       border-radius:8px;padding:9px 13px;">
    <span style="width:6px;height:6px;border-radius:50%;background:{GOLD};flex:none;"></span>
    <span style="font-size:12px;color:#6b5d38;">Los gastos de <b style="color:{NAVY};">{mes_nombre}</b>
    se pagan con el sueldo de <b style="color:{NAVY};">principios del mes siguiente</b>.</span>
  </div>
</div>""", unsafe_allow_html=True)

    if balance_ant is not None and total_ant:
        st.markdown(f"""
<div style="padding:8px 16px 0;">
  <div style="display:flex;align-items:center;gap:10px;background:#eef7f1;border-left:3px solid #1f9d57;
       border-radius:8px;padding:9px 13px;">
    <span style="width:6px;height:6px;border-radius:50%;background:#1f9d57;flex:none;"></span>
    <span style="font-size:12px;color:#2f6b48;">A pagar <b>este mes</b>: Total
    <b>$ {total_ant:,.0f}</b> · {deudor_ant} le paga a {acreedor_ant} <b>$ {balance_ant:,.0f}</b></span>
  </div>
</div>""", unsafe_allow_html=True)

    if balance < 1:
        hero_inner = f"""
      <div style="color:#86efac;font-size:11px;font-weight:800;letter-spacing:2px;">ESTÁN AL DÍA</div>
      <div style="color:#fff;font-family:{SERIF};font-size:clamp(36px,12vw,54px);font-weight:600;line-height:1.02;margin-top:6px;">$ 0</div>
      <div style="color:rgba(255,255,255,.55);font-size:12px;margin-top:2px;">Los dos gastaron lo mismo</div>"""
    else:
        hero_inner = f"""
      <div style="color:{GOLD_L};font-size:11px;font-weight:800;letter-spacing:2px;">{deudor} LE DEBE A {acreedor}</div>
      <div style="color:#fff;font-family:{SERIF};font-size:clamp(36px,12vw,54px);font-weight:600;line-height:1.02;margin-top:6px;">$ {balance:,.0f}</div>
      <div style="color:rgba(255,255,255,.55);font-size:12px;margin-top:2px;">para quedar iguales</div>"""

    st.markdown(f"""
<div style="margin:18px 8px 8px;background:linear-gradient(140deg,{NAVY},{NAVY2} 70%,{BLUE});
     border-radius:18px;padding:22px 16px;box-shadow:0 6px 24px rgba(15,27,53,.22);">
  <div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:3px;">LIQUIDACIÓN DEL MES</div>
  <div style="text-align:center;padding:14px 0 18px;">{hero_inner}</div>
  <div style="display:flex;height:10px;border-radius:6px;overflow:hidden;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);">
    <div style="background:linear-gradient(90deg,{BLUE},#3f86e0);width:{p1_pct}%;"></div>
    <div style="background:linear-gradient(90deg,{GOLD},{GOLD_L});flex:1;"></div>
  </div>
  <div style="display:flex;align-items:stretch;gap:10px;margin-top:16px;">
    <div style="flex:1;min-width:0;background:rgba(45,107,196,.28);border-radius:13px;padding:12px 10px;text-align:center;">
      <div style="color:#93c5fd;font-size:10px;font-weight:700;letter-spacing:1px;">{persona_1.upper()} PAGÓ</div>
      <div style="color:#fff;font-family:{SERIF};font-size:clamp(18px,5.5vw,26px);font-weight:600;margin-top:4px;">$ {p1_pago:,.0f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:10px;margin-top:3px;">le corresponde $ {corresponde_cu:,.0f}</div>
    </div>
    <div style="display:flex;align-items:center;color:{GOLD_L};font-size:18px;opacity:.7;flex:none;">⇄</div>
    <div style="flex:1;min-width:0;background:rgba(201,168,76,.22);border-radius:13px;padding:12px 10px;text-align:center;">
      <div style="color:{GOLD_L};font-size:10px;font-weight:700;letter-spacing:1px;">{persona_2.upper()} PAGÓ</div>
      <div style="color:#fff;font-family:{SERIF};font-size:clamp(18px,5.5vw,26px);font-weight:600;margin-top:4px;">$ {p2_pago:,.0f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:10px;margin-top:3px;">le corresponde $ {corresponde_cu:,.0f}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


def render(ctx):
    casa_id   = ctx["casa_id"]
    persona_1 = ctx["persona_1"]
    persona_2 = ctx["persona_2"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]
    mes_nombre = ctx["mes_nombre"]

    mes_ant_num = mes_sel - 1 if mes_sel > 1 else 12
    anio_ant    = anio_sel if mes_sel > 1 else anio_sel - 1

    gastos_fijos     = db.get_gastos_fijos(casa_id)
    excluidos_res    = db.get_fijos_excluidos_mes(anio_sel, mes_sel)
    p1_fijos         = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == persona_1)
    p2_fijos         = sum(v for gid, _, v, _, pg in gastos_fijos if gid not in excluidos_res and pg == persona_2)
    total_fijos_base = p1_fijos + p2_fijos
    total_fijos      = total_fijos_base

    total_por_persona       = db.get_totales_mes(anio_sel, mes_sel, casa_id)
    cuotas_persona, cuotas_items = db.get_total_cuotas_activas_mes(anio_sel, mes_sel, casa_id)
    p1_vars   = total_por_persona.get(persona_1, 0)
    p1_cuotas = cuotas_persona.get(persona_1, 0)
    p2_vars   = total_por_persona.get(persona_2, 0)
    p2_cuotas = cuotas_persona.get(persona_2, 0)
    p2_pago        = p2_vars + p2_cuotas + p2_fijos
    total_variable = sum(total_por_persona.values()) + sum(cuotas_persona.values())
    total_general  = total_fijos + total_variable
    p1_pago        = p1_vars + p1_cuotas + p1_fijos
    mitad          = total_general / 2
    balance        = p1_pago - mitad

    tot_ant_persona    = db.get_totales_mes(anio_ant, mes_ant_num, casa_id)
    cuotas_ant, _      = db.get_total_cuotas_activas_mes(anio_ant, mes_ant_num, casa_id)
    total_ant          = total_fijos + sum(tot_ant_persona.values()) + sum(cuotas_ant.values())
    p1_ant             = tot_ant_persona.get(persona_1, 0) + cuotas_ant.get(persona_1, 0) + total_fijos_base
    balance_ant        = p1_ant - total_ant / 2

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

    _render_hero(mes_nombre, anio_sel, p1_pago, p2_pago, mitad,
                 deudor, acreedor, balance_show, persona_1, persona_2, **kw_ant)

    st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;padding:16px 8px 28px;">
  {_stat("TOTAL DEL MES", total_general, GOLD)}
  {_stat("VARIABLES", total_variable, BLUE)}
  {_stat("FIJOS", total_fijos, NAVY2)}
</div>""", unsafe_allow_html=True)

    # Por categoría
    por_cat = db.get_por_categoria_mes(anio_sel, mes_sel, casa_id)
    if por_cat:
        st.markdown("---")
        st.markdown("<h3>Por categoría</h3>", unsafe_allow_html=True)
        df_cat = pd.DataFrame(por_cat, columns=["Categoría", "Monto"])
        df_cat["Monto"] = df_cat["Monto"].round(0).astype(int)
        st.bar_chart(df_cat.set_index("Categoría"), height=220, color=BLUE)
        for cat, monto in por_cat:
            pct = (monto / total_variable * 100) if total_variable > 0 else 0
            st.markdown(f"""
<div style="display:flex;align-items:center;margin-bottom:6px;gap:10px;">
  <div style="width:130px;font-size:13px;color:{NAVY};font-weight:500;">{cat}</div>
  <div style="flex:1;background:#e2e8f0;border-radius:4px;height:8px;">
    <div style="width:{int(pct)}%;background:linear-gradient(90deg,{BLUE},{GOLD});height:8px;border-radius:4px;"></div>
  </div>
  <div style="width:80px;text-align:right;font-size:13px;font-weight:700;color:{NAVY};">$ {monto:,.0f}</div>
  <div style="width:38px;font-size:11px;color:{GRAY};">{pct:.0f}%</div>
</div>""", unsafe_allow_html=True)

    # Por tipo de pago
    por_tipo = db.get_por_tipo_mes(anio_sel, mes_sel, casa_id)
    if por_tipo:
        st.markdown("---")
        st.markdown("<h3>Por tipo de pago</h3>", unsafe_allow_html=True)
        iconos = {"Débito": "💳", "Crédito": "🏦", "Efectivo": "💵"}
        cols = st.columns(len(por_tipo))
        for i, (tipo, monto) in enumerate(por_tipo):
            cols[i].markdown(f"""
<div class="g-card" style="text-align:center;border-top:3px solid {NAVY2};">
  <div style="font-size:22px;">{iconos.get(tipo,"💰")}</div>
  <div style="color:{GRAY};font-size:12px;margin-top:4px;">{tipo}</div>
  <div style="color:{NAVY};font-size:22px;font-weight:800;">$ {monto:,.0f}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Compromisos del mes
    fijos_excluidos = [(nombre_ex,) for gid, nombre_ex, _, _, _ in gastos_fijos if gid in excluidos_res]
    filas_card      = [(nombre_f, v, pg) for gid, nombre_f, v, _, pg in gastos_fijos if gid not in excluidos_res]
    st.markdown(_tarjeta_compromisos(filas_card, total_fijos_base, p1_fijos, p2_fijos, persona_1, persona_2),
                unsafe_allow_html=True)

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
            f'{excl_html}</div>', unsafe_allow_html=True)

    if cuotas_items:
        partes = []
        for p, t, d, vc, cn, tc in cuotas_items:
            bg  = "#eef3fc" if p == persona_1 else "rgba(201,168,76,.1)"
            col = BLUE      if p == persona_1 else GOLD
            partes.append(
                f'<div style="display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;'
                f'padding:10px 12px;margin-bottom:4px;background:{bg};'
                f'border-radius:10px;border-left:3px solid {col};">'
                f'<div><div style="color:{NAVY};font-size:13px;font-weight:600;">{d}</div>'
                f'<div style="color:{GRAY};font-size:11px;">{t} · cuota {cn}/{tc} · paga {p}</div></div>'
                f'<span style="color:{NAVY};font-size:15px;font-weight:700;">$ {vc:,.0f}</span></div>'
            )
        st.markdown(
            f'<div style="background:#f8fafc;border-radius:12px;padding:12px 16px;margin-bottom:8px;">'
            f'<div style="color:{GRAY};font-size:10px;font-weight:700;letter-spacing:1px;margin-bottom:8px;">CUOTAS DE TARJETA</div>'
            f'{"".join(partes)}</div>', unsafe_allow_html=True)
