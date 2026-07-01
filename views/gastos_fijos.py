import streamlit as st
import db
from estilos import *


def render(ctx):
    casa_id   = ctx["casa_id"]
    personas  = ctx["personas"]
    persona_1 = ctx["persona_1"]
    persona_2 = ctx["persona_2"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]

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
      <div style="color:#fff;font-family:{SERIF};font-size:34px;font-weight:500;line-height:1.05;">$ {total:,.0f}</div>
      <div style="display:inline-flex;align-items:baseline;gap:6px;margin-top:5px;
           background:rgba(201,168,76,.22);border:1px solid rgba(245,208,96,.35);
           border-radius:9px;padding:4px 11px;">
        <span style="color:rgba(245,208,96,.8);font-size:9.5px;font-weight:800;letter-spacing:1px;">LE TOCA C/U</span>
        <span style="color:{GOLD_L};font-family:{SERIF};font-size:19px;font-weight:600;">$ {total/2:,.0f}</span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

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
