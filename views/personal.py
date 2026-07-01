import streamlit as st
from datetime import date
import db
from estilos import *


def render(ctx):
    casa_id   = ctx["casa_id"]
    persona_1 = ctx["persona_1"]
    persona_2 = ctx["persona_2"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]
    mes_nombre = ctx["mes_nombre"]

    if "persona_personal" not in st.session_state:
        st.session_state.persona_personal = None

    st.markdown(f"""
<div style="background:linear-gradient(140deg,{NAVY},{NAVY2} 70%,{BLUE});
     border-radius:18px;padding:28px 30px 22px;margin-bottom:20px;
     box-shadow:0 6px 24px rgba(15,27,53,.22);">
  <div style="color:{GOLD_L};font-size:10px;font-weight:800;letter-spacing:3px;margin-bottom:6px;">GASTOS PERSONALES</div>
  <div style="color:#fff;font-family:{DISPLAY};font-size:46px;font-weight:600;line-height:1;">¿De quién?</div>
  <div style="color:rgba(255,255,255,.55);font-size:13px;margin-top:6px;">Elegí tu nombre para ver y cargar tus gastos personales.</div>
</div>""", unsafe_allow_html=True)

    persona_sel = st.session_state.persona_personal
    col_m, col_g = st.columns(2)
    with col_m:
        if st.button(f"💙  {persona_1}", use_container_width=True,
                     type="primary" if persona_sel == persona_1 else "secondary",
                     key="btn_p1_personal"):
            st.session_state.persona_personal = persona_1
            st.rerun()
    with col_g:
        if st.button(f"💛  {persona_2}", use_container_width=True,
                     type="primary" if persona_sel == persona_2 else "secondary",
                     key="btn_p2_personal"):
            st.session_state.persona_personal = persona_2
            st.rerun()

    persona_sel = st.session_state.persona_personal
    if not persona_sel:
        return

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
</div>""", unsafe_allow_html=True)

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
</div>""", unsafe_allow_html=True)
        else:
            por_cat_p = {}
            for gid, fecha_g, cat_g, desc_g, monto_g, coment_g in gastos_p:
                por_cat_p.setdefault(cat_g, []).append((gid, fecha_g, desc_g, monto_g, coment_g))

            for cat_g, items in por_cat_p.items():
                subtotal = sum(m for _, _, _, m, _ in items)
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
     padding:6px 12px;margin:10px 0 4px;
     border-left:3px solid {color_persona};border-radius:0 6px 6px 0;background:rgba(0,0,0,.03);">
  <span style="color:{NAVY};font-size:12px;font-weight:700;letter-spacing:.5px;">{cat_g.upper()}</span>
  <span style="color:{color_persona};font-size:13px;font-weight:700;">$ {subtotal:,.0f}</span>
</div>""", unsafe_allow_html=True)
                for gid, fecha_g, desc_g, monto_g, coment_g in items:
                    col_info, col_del = st.columns([11, 1])
                    with col_info:
                        nota = (f' <span style="color:{GRAY};font-size:11px;">— {coment_g}</span>'
                                if coment_g else "")
                        st.markdown(
                            f'<div style="display:grid;grid-template-columns:1fr auto;gap:10px;'
                            f'align-items:center;padding:9px 12px;margin-bottom:3px;'
                            f'background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(15,27,53,.06);">'
                            f'<div><div style="color:{NAVY};font-size:13px;font-weight:600;">{desc_g}{nota}</div>'
                            f'<div style="color:{GRAY};font-size:11px;margin-top:1px;">{fecha_g}</div></div>'
                            f'<span style="color:{color_persona};font-size:15px;font-weight:700;">$ {monto_g:,.0f}</span>'
                            f'</div>', unsafe_allow_html=True)
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
</div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            fecha_p  = col1.date_input("Fecha", value=date.today(), key="fp_fecha")
            cat_p    = col2.selectbox("Categoría", db.CATEGORIAS_PERSONAL, key="fp_cat")
            desc_p   = st.text_input("Descripción", placeholder="ej: zapatillas, cena con amigas…", key="fp_desc")
            monto_p  = st.number_input("Monto ($)", min_value=0.0, step=10.0, format="%.0f", key="fp_monto")
            coment_p = st.text_input("Comentarios (opcional)", placeholder="ej: en oferta, cuotas…", key="fp_coment")
            enviado_p = st.form_submit_button("Guardar gasto personal", use_container_width=True, type="primary")

        if enviado_p:
            if monto_p <= 0 or not desc_p.strip():
                st.error("Completá la descripción y el monto.")
            else:
                db.agregar_gasto_personal(str(fecha_p), cat_p, desc_p.strip(),
                                           persona_sel, monto_p, coment_p.strip(), casa_id)
                st.success(f"✅ '{desc_p}' guardado — $ {monto_p:,.0f}")
                st.session_state.form_personal_n += 1
                st.rerun()
