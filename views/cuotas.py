import streamlit as st
from datetime import date, datetime
import db
from estilos import *


def render(ctx):
    casa_id   = ctx["casa_id"]
    personas  = ctx["personas"]
    persona_1 = ctx["persona_1"]
    persona_2 = ctx["persona_2"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]

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
            if mes_ini is None: return 0
            if anio_ini is None: anio_ini = anio_sel
            return max(0, min(anio_sel * 12 + mes_sel - (anio_ini * 12 + mes_ini) + 1, n))
        except Exception:
            return 0

    compras_con_p = [
        (cid, det, vt, n, vc, mon, prim, tarj, pers, com, _pagadas(prim, n))
        for (cid, det, vt, n, vc, mon, prim, tarj, pers, com, _) in compras_all
    ]
    activas_mes      = [c for c in compras_con_p if 1 <= c[10] <= c[3]]
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
</div>""", unsafe_allow_html=True)

    if "form_cuota_n" not in st.session_state:
        st.session_state.form_cuota_n = 0

    with st.container(border=True):
        tab_ver, tab_nueva = st.tabs(["Ver cuotas", "Nueva compra"])

        with tab_ver:
            if not activas_mes:
                st.info("No hay cuotas activas para este mes.")
            else:
                tarjetas_usadas = sorted({c[7] for c in activas_mes})
                filtro_tarj = st.selectbox("Filtrar por tarjeta", ["Todas"] + tarjetas_usadas, label_visibility="collapsed")
                vis     = activas_mes if filtro_tarj == "Todas" else [c for c in activas_mes if c[7] == filtro_tarj]
                tot_vis = sum(c[4] for c in vis)

                st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
         background:{GOLD_P};border:1px solid rgba(201,168,76,.3);border-left:4px solid {GOLD};
         border-radius:13px;padding:14px 20px;margin:6px 0 14px;">
      <span style="font-size:10.5px;font-weight:800;letter-spacing:1.5px;color:#9a8c5e;">TOTAL CUOTAS / MES</span>
      <span style="font-family:{SERIF};font-size:30px;font-weight:600;color:{NAVY};">$ {tot_vis:,.0f}</span>
    </div>""", unsafe_allow_html=True)

                for (cid, detalle_c, v_total, n, v_cuota, mon, primera, tarjeta_c, persona, coment, pagadas) in vis:
                    pct     = round(pagadas / n * 100) if n else 0
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
            tarjetas_casa = [f"{nombre} ({dueno})" for _, nombre, dueno, _ in db.get_tarjetas(casa_id)]
            if not tarjetas_casa:
                st.info("No hay tarjetas configuradas. Agregá una en el menú **Tarjetas**.")

            with st.form(f"form_cuota_{st.session_state.form_cuota_n}", clear_on_submit=True):
                detalle = st.text_input("Qué compraste", placeholder="ej: Zapatillas, Mesa, Celular...")
                col_v, col_c, col_mon = st.columns([1.4, 1, 1])
                valor  = col_v.number_input("Valor total", min_value=0.0, step=100.0, format="%.0f")
                cuotas = col_c.number_input("Cuotas", min_value=1, max_value=48, step=1, value=1)
                moneda = col_mon.selectbox("Moneda", ["$", "U$S"])
                if cuotas > 0 and valor > 0:
                    st.info(f"Valor por cuota: **{moneda} {valor/cuotas:,.0f}**")
                col_t, col_p = st.columns(2)
                tarjeta    = col_t.selectbox("Tarjeta", tarjetas_casa) if tarjetas_casa else None
                pagado_por = col_p.selectbox("¿Quién?", personas)
                col_fc, col_mp = st.columns(2)
                fecha_compra      = col_fc.date_input("Fecha de compra", value=date.today())
                mes_primera_cuota = col_mp.selectbox("1ra cuota en",
                                                      [f"{m} {anio_sel}" for m in db.MESES],
                                                      index=datetime.today().month - 1)
                comentarios   = st.text_input("Comentarios", placeholder="ej: con 20% descuento")
                enviado_cuota = st.form_submit_button("Guardar compra", use_container_width=True)

            if enviado_cuota:
                if valor <= 0 or not detalle:
                    st.error("Completá el detalle y el valor.")
                elif not tarjeta:
                    st.error("Agregá una tarjeta en el menú Tarjetas antes de cargar una compra.")
                else:
                    db.agregar_compra_tarjeta(detalle, valor, cuotas, moneda, comentarios,
                                               str(fecha_compra), mes_primera_cuota, tarjeta, pagado_por, casa_id)
                    st.success(f"✅ '{detalle}' guardada — {cuotas} cuota/s de {moneda} {valor/cuotas:,.0f}")
                    st.session_state.form_cuota_n += 1
                    st.rerun()
