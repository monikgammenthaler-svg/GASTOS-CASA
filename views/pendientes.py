import streamlit as st
from collections import defaultdict
import db
from estilos import *

ICON_CAT = {
    "Supermercado": "🛒", "Limpieza": "🧹", "Farmacia": "💊",
    "Ropa": "👕", "Hogar": "🏠", "Trámite": "📋", "Otro": "📌",
}
PRIO_COLOR = {"Alta": "#ef4444", "Normal": GOLD, "Baja": GRAY}


def render(ctx):
    casa_id   = ctx["casa_id"]
    personas  = ctx["personas"]

    ICON_QUIEN = {"Todos": "👫", **{p: "🙋" for p in personas}}

    st.markdown(
        f'<div style="background:{WHITE};border-radius:16px;padding:18px 22px;'
        f'box-shadow:0 2px 12px rgba(15,27,53,0.09);margin-bottom:16px;">'
        f'<div style="color:{NAVY};font-size:15px;font-weight:700;margin-bottom:10px;">✏️ Agregar a la lista</div>'
        f'</div>', unsafe_allow_html=True)

    with st.form("form_pendiente", clear_on_submit=True):
        descripcion = st.text_input("Qué necesitás", placeholder="ej: Nescafé, Detergente, Aceite...",
                                    label_visibility="collapsed")
        col_cat, col_pri, col_quien = st.columns(3)
        categoria  = col_cat.selectbox("Categoría", db.CATEGORIAS_PENDIENTES)
        prioridad  = col_pri.selectbox("Prioridad", db.PRIORIDADES)
        asignado_a = col_quien.selectbox("Para quién", ["Todos"] + personas)
        enviado = st.form_submit_button("➕ Agregar", use_container_width=True, type="primary")

    if enviado:
        if descripcion.strip():
            db.agregar_pendiente(descripcion.strip(), categoria, prioridad, asignado_a, casa_id)
            st.rerun()
        else:
            st.error("Escribí algo primero.")

    todos    = db.get_pendientes(solo_activos=False, casa_id=casa_id)
    activos  = [p for p in todos if not p[5]]
    hechos   = [p for p in todos if p[5]]

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
            f'</div>', unsafe_allow_html=True)
    else:
        total_items = len(activos)
        st.markdown(
            f'<div style="color:{GRAY};font-size:13px;margin-bottom:10px;">'
            f'{total_items} item{"s" if total_items != 1 else ""} '
            f'pendiente{"s" if total_items != 1 else ""}</div>', unsafe_allow_html=True)

        for cat, items in por_cat.items():
            icono = ICON_CAT.get(cat, "📌")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'margin:14px 0 6px;padding-bottom:4px;border-bottom:2px solid {GOLD};">'
                f'<span style="font-size:18px;">{icono}</span>'
                f'<span style="color:{NAVY};font-size:14px;font-weight:700;letter-spacing:0.5px;">{cat.upper()}</span>'
                f'<span style="color:{GRAY};font-size:12px;">({len(items)})</span>'
                f'</div>', unsafe_allow_html=True)

            for pid, desc, cat2, prio, quien, _, fecha in items:
                pc       = PRIO_COLOR.get(prio, GRAY)
                iq       = ICON_QUIEN.get(quien, "👫")
                editando = st.session_state.get("edit_pid") == pid

                if editando:
                    nuevo = st.text_input("Editar", value=desc, key=f"inp_{pid}", label_visibility="collapsed")
                    c1, c2 = st.columns(2)
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
                            f'</div>', unsafe_allow_html=True)
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
                        f'</div>', unsafe_allow_html=True)
                with col_d:
                    if st.button("↩", key=f"undo_{pid}", help="Deshacer"):
                        db.marcar_pendiente(pid, False)
                        st.rerun()
