import streamlit as st
from datetime import date
import db
from estilos import *


def render(ctx):
    personas  = ctx["personas"]
    casa_id   = ctx["casa_id"]
    anio_sel  = ctx["anio_sel"]
    mes_sel   = ctx["mes_sel"]

    st.markdown(f'<div style="color:{NAVY};font-family:{DISPLAY};font-size:46px;font-weight:600;'
                f'line-height:1;margin-bottom:10px;">Cargar gasto</div>', unsafe_allow_html=True)

    tiene_cuotas   = st.checkbox("¿Pago en cuotas?")
    tarjetas_casa  = [t[1] for t in db.get_tarjetas(casa_id)]

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
            num_cuotas = col_nc.number_input("Cantidad de cuotas", min_value=2, max_value=48, step=1, value=3)
            if tarjetas_casa:
                tarjeta_cuota = col_tc.selectbox("Tarjeta", tarjetas_casa)
            else:
                col_tc.info("No hay tarjetas configuradas. Agregá una en el menú **Tarjetas**.")
            if monto > 0:
                st.info(f"Valor por cuota: $ {monto / num_cuotas:,.0f}  ·  "
                        f"{int(num_cuotas)} meses desde {db.MESES[fecha.month - 1]} {fecha.year}")

        comentarios = st.text_input("Comentarios (opcional)", placeholder="ej: con 20% descuento")
        enviado = st.form_submit_button("Guardar gasto", use_container_width=True)

    if enviado:
        if monto <= 0:
            st.error("El monto debe ser mayor a cero.")
        elif tiene_cuotas and not tarjeta_cuota:
            st.error("Agregá una tarjeta en el menú Tarjetas antes de cargar un gasto en cuotas.")
        elif tiene_cuotas:
            db.agregar_gasto_en_cuotas(str(fecha), categoria, descripcion, pagado_por,
                                        tipo, tarjeta_cuota, monto, int(num_cuotas), casa_id)
            st.success(f"✅ {int(num_cuotas)} cuotas de $ {round(monto/num_cuotas,0):,.0f} guardadas.")
            st.balloons()
        else:
            db.agregar_gasto(str(fecha), categoria, descripcion, pagado_por,
                             comentarios, tipo, monto, casa_id)
            st.success(f"✅ Gasto de $ {monto:,.0f} guardado.")
            st.balloons()
