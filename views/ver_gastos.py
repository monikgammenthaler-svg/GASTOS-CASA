import streamlit as st
import pandas as pd
import db
from estilos import *


def render(ctx):
    casa_id   = ctx["casa_id"]
    personas  = ctx["personas"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]
    mes_nombre = ctx["mes_nombre"]

    st.markdown(f"<h1>Gastos de {mes_nombre} {anio_sel}</h1>", unsafe_allow_html=True)

    gastos = db.get_gastos_mes(anio_sel, mes_sel, casa_id)

    if not gastos:
        st.info("No hay gastos cargados para este mes.")
        return

    cols_filter = st.columns(3)
    filtro_persona = cols_filter[0].selectbox("Persona",   ["Todos"] + personas)
    filtro_tipo    = cols_filter[1].selectbox("Tipo",      ["Todos"] + db.TIPOS_PAGO)
    filtro_cat     = cols_filter[2].selectbox("Categoría", ["Todas"] + db.CATEGORIAS)

    df = pd.DataFrame(gastos, columns=["id", "Fecha", "Categoría", "Descripción",
                                        "Pagado por", "Tipo", "Monto", "Comentarios"])
    if filtro_persona != "Todos": df = df[df["Pagado por"] == filtro_persona]
    if filtro_tipo    != "Todos": df = df[df["Tipo"]       == filtro_tipo]
    if filtro_cat     != "Todas": df = df[df["Categoría"]  == filtro_cat]

    total_filtrado = df["Monto"].sum()
    st.markdown(f"""
<div class="g-card" style="display:flex;justify-content:space-between;align-items:center;border-left:4px solid {GOLD};">
  <div><span style="color:{GRAY};font-size:12px;">TOTAL FILTRADO</span><br>
  <span style="color:{NAVY};font-size:26px;font-weight:800;">$ {total_filtrado:,.0f}</span></div>
  <div style="color:{GOLD};font-size:20px;font-weight:700;">{len(df)} registros</div>
</div>""", unsafe_allow_html=True)

    for _, row in df.iterrows():
        col = color_persona(row["Pagado por"], personas)
        tag = (f"<span style='background:{col};color:{WHITE};font-size:12px;font-weight:700;"
               f"border-radius:6px;padding:3px 10px;'>{row['Pagado por'].upper()}</span>")
        with st.expander(f"{row['Fecha']}  —  {row['Descripción'] or row['Categoría']}  |  $ {row['Monto']:,.0f}"):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Categoría:** {row['Categoría']}")
            c2.markdown(f"**Quién:** {tag}", unsafe_allow_html=True)
            c3.write(f"**Tipo:** {row['Tipo']}")
            if row["Comentarios"]:
                st.caption(row["Comentarios"])
            if st.button("Eliminar", key=f"del_{row['id']}"):
                db.eliminar_gasto(row["id"])
                st.rerun()
