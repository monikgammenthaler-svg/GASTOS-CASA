import psycopg2
import streamlit as st
import db
from estilos import *


def render(ctx):
    casa_id   = ctx["casa_id"]
    duenos    = ctx["personas"] + ["Compartida"]

    tarjetas = db.get_tarjetas(casa_id)

    st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 58%,{BLUE} 100%);
            border-radius:20px 20px 0 0;padding:24px 30px;">
  <div style="color:{GOLD_L};font-family:{DISPLAY};font-size:16px;font-weight:600;
       font-style:italic;letter-spacing:2px;text-transform:uppercase;">Editor · Tarjetas</div>
  <div style="color:#fff;font-family:{DISPLAY};font-size:40px;font-weight:600;
       letter-spacing:.2px;line-height:1.05;">Tarjetas del hogar</div>
  <div style="color:rgba(255,255,255,.5);font-size:12px;margin-top:3px;">
       {len(tarjetas)} tarjeta/s configurada/s</div>
</div>""", unsafe_allow_html=True)

    with st.container(border=True):
        if not tarjetas:
            st.info("Todavía no configuraste ninguna tarjeta. Agregá la primera abajo.")
        else:
            hc = st.columns([2.3, 0.5, 2.2, 1.5])
            for c, txt in zip(hc, ["TARJETA", "", "DUEÑO", ""]):
                c.markdown(f"<div style='font-size:9.5px;font-weight:800;letter-spacing:1.2px;"
                           f"color:#9aa0ab;padding-top:6px;'>{txt}</div>", unsafe_allow_html=True)

            for tid, nombre, dueno, _ in tarjetas:
                editando = st.session_state.get(f"editando_tarj_{tid}", False)
                col_n, col_e, col_d, col_b = st.columns([2.3, 0.5, 2.2, 1.5])

                if editando:
                    nuevo_nombre = col_n.text_input("Nombre", value=nombre, key=f"input_nombre_{tid}",
                                                     label_visibility="collapsed")
                    if col_e.button("✔️", key=f"guardar_tarj_{tid}", use_container_width=True):
                        if not nuevo_nombre or nuevo_nombre == nombre:
                            st.session_state[f"editando_tarj_{tid}"] = False
                            st.rerun()
                        else:
                            try:
                                db.actualizar_nombre_tarjeta(tid, nuevo_nombre)
                                st.session_state[f"editando_tarj_{tid}"] = False
                                st.rerun()
                            except psycopg2.errors.UniqueViolation:
                                st.error(f"Ya existe una tarjeta '{nuevo_nombre}' con ese dueño.")
                else:
                    col_n.markdown(f"<div style='font-size:17px;font-weight:600;color:{NAVY};"
                                   f"padding-top:6px;'>{nombre}</div>", unsafe_allow_html=True)
                    if col_e.button("✏️", key=f"editbtn_tarj_{tid}", use_container_width=True):
                        st.session_state[f"editando_tarj_{tid}"] = True
                        st.rerun()

                idx = duenos.index(dueno) if dueno in duenos else 0
                nuevo_dueno = col_d.selectbox("Dueño", duenos, index=idx,
                                              key=f"dueno_{tid}", label_visibility="collapsed")
                if nuevo_dueno != dueno:
                    db.actualizar_dueno_tarjeta(tid, nuevo_dueno)
                    st.rerun()

                if col_b.button("Eliminar", key=f"del_tarj_{tid}", use_container_width=True):
                    db.desactivar_tarjeta(tid)
                    st.rerun()

        st.markdown("---")
        st.markdown(f"<div style='font-size:10px;font-weight:800;letter-spacing:1.5px;"
                    f"color:#9aa0ab;'>AGREGAR TARJETA</div>", unsafe_allow_html=True)
        with st.form("form_tarjeta", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 2, 1.4])
            nuevo_nombre = c1.text_input("Nombre", placeholder="ej: Visa Santander", label_visibility="collapsed")
            nuevo_dueno  = c2.selectbox("Dueño", duenos, label_visibility="collapsed")
            if c3.form_submit_button("Agregar", use_container_width=True):
                if not nuevo_nombre:
                    st.error("Completá el nombre de la tarjeta.")
                else:
                    try:
                        db.agregar_tarjeta(nuevo_nombre, nuevo_dueno, casa_id)
                        st.success(f"✅ {nuevo_nombre} agregada")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error(f"Ya existe una tarjeta llamada '{nuevo_nombre}'.")
