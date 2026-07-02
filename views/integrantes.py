import psycopg2
import streamlit as st
import db
from estilos import *


def render(ctx):
    casa_id  = ctx["casa_id"]
    personas = ctx["personas"]

    st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 58%,{BLUE} 100%);
            border-radius:20px 20px 0 0;padding:24px 30px;">
  <div style="color:{GOLD_L};font-family:{DISPLAY};font-size:16px;font-weight:600;
       font-style:italic;letter-spacing:2px;text-transform:uppercase;">Editor · Integrantes</div>
  <div style="color:#fff;font-family:{DISPLAY};font-size:40px;font-weight:600;
       letter-spacing:.2px;line-height:1.05;">Integrantes del hogar</div>
  <div style="color:rgba(255,255,255,.5);font-size:12px;margin-top:3px;">
       {len(personas)} persona/s · los gastos se reparten en partes iguales entre todas</div>
</div>""", unsafe_allow_html=True)

    with st.container(border=True):
        for persona in personas:
            editando = st.session_state.get(f"editando_persona_{persona}", False)
            col_n, col_e, col_b = st.columns([4, 0.8, 1.8])

            if editando:
                nuevo_nombre = col_n.text_input("Nombre", value=persona, key=f"input_persona_{persona}",
                                                 label_visibility="collapsed")
                if col_e.button("✔️", key=f"guardar_persona_{persona}", use_container_width=True):
                    if not nuevo_nombre or nuevo_nombre == persona:
                        st.session_state[f"editando_persona_{persona}"] = False
                        st.rerun()
                    else:
                        try:
                            db.renombrar_persona_casa(casa_id, persona, nuevo_nombre)
                            st.session_state["personas"] = db.obtener_personas_casa(casa_id)
                            st.session_state[f"editando_persona_{persona}"] = False
                            st.success(f"✅ '{persona}' ahora es '{nuevo_nombre}' (se actualizó también en todo el historial)")
                            st.rerun()
                        except psycopg2.errors.UniqueViolation:
                            st.error(f"Ya existe una persona llamada '{nuevo_nombre}'.")
            else:
                col_n.markdown(f"<div style='font-size:17px;font-weight:600;color:{NAVY};"
                               f"padding-top:6px;'>{persona}</div>", unsafe_allow_html=True)
                if col_e.button("✏️", key=f"editbtn_persona_{persona}", use_container_width=True):
                    st.session_state[f"editando_persona_{persona}"] = True
                    st.rerun()

            if col_b.button("Eliminar", key=f"del_persona_{persona}", use_container_width=True,
                             disabled=len(personas) <= 1,
                             help="No se puede eliminar a la última persona del hogar" if len(personas) <= 1 else None):
                db.eliminar_persona_casa(casa_id, persona)
                st.session_state["personas"] = db.obtener_personas_casa(casa_id)
                st.rerun()

        st.caption("Al eliminar una persona, los gastos que ya cargó quedan en el historial tal cual — solo deja de aparecer para cargar gastos nuevos.")

        st.markdown("---")
        st.markdown(f"<div style='font-size:10px;font-weight:800;letter-spacing:1.5px;"
                    f"color:#9aa0ab;'>AGREGAR PERSONA</div>", unsafe_allow_html=True)
        with st.form("form_persona", clear_on_submit=True):
            c1, c2 = st.columns([4, 1.4])
            nuevo_nombre = c1.text_input("Nombre", placeholder="Nombre de la persona", label_visibility="collapsed")
            if c2.form_submit_button("Agregar", use_container_width=True):
                if not nuevo_nombre:
                    st.error("Escribí un nombre.")
                else:
                    try:
                        db.agregar_persona_casa(casa_id, nuevo_nombre.strip())
                        st.session_state["personas"] = db.obtener_personas_casa(casa_id)
                        st.success(f"✅ {nuevo_nombre} agregado")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error(f"Ya existe una persona llamada '{nuevo_nombre}'.")
