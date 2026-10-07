import streamlit as st
import pandas as pd

def render_cotizaciones_presupuestos():
    """
    Módulo de Cotizaciones y Validación de Mercado (3 Presupuestos Comparativos en MXN).
    Desglose de IVA 16%, flete/maniobras y criterio de selección del proveedor.
    """
    st.markdown("#### 💰 Fase 1B: Cotizaciones y Presupuestos Comparativos (Mercado Nacional)")
    st.caption("3 presupuestos comparativos de distribuidores en México. Precios puestos en sitio (DDP/PDU en MXN) desglosando IVA 16% y fletes.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 🏢 Proveedor 1")
        p1_nombre = st.text_input("Nombre / Razón Social:", value="Grupo Industrial Monterrey S.A. de C.V.", key="ind_p1_n")
        p1_precio = st.number_input("Precio Base ($ MXN):", min_value=0.0, value=350000.0, step=5000.0, key="ind_p1_p")
        p1_flete = st.number_input("Flete y Maniobras ($ MXN):", min_value=0.0, value=15000.0, step=1000.0, key="ind_p1_f")

    with col2:
        st.markdown("##### 🏢 Proveedor 2")
        p2_nombre = st.text_input("Nombre / Razón Social:", value="Equipos y Maquinaria del Bajío S.A. de C.V.", key="ind_p2_n")
        p2_precio = st.number_input("Precio Base ($ MXN):", min_value=0.0, value=380000.0, step=5000.0, key="ind_p2_p")
        p2_flete = st.number_input("Flete y Maniobras ($ MXN):", min_value=0.0, value=10000.0, step=1000.0, key="ind_p2_f")

    with col3:
        st.markdown("##### 🏢 Proveedor 3")
        p3_nombre = st.text_input("Nombre / Razón Social:", value="Maquinaria del Centro y Procesos S.A. de C.V.", key="ind_p3_n")
        p3_precio = st.number_input("Precio Base ($ MXN):", min_value=0.0, value=330000.0, step=5000.0, key="ind_p3_p")
        p3_flete = st.number_input("Flete y Maniobras ($ MXN):", min_value=0.0, value=25000.0, step=1000.0, key="ind_p3_f")

    st.markdown("---")
    col_sel1, col_sel2 = st.columns([1, 1])

    with col_sel1:
        prov_seleccionado = st.selectbox(
            "🎯 Proveedor Seleccionado:",
            [p1_nombre, p2_nombre, p3_nombre],
            key="ind_prov_sel"
        )
    with col_sel2:
        criterio_sel = st.text_area(
            "💡 Criterio y Justificación de Selección:",
            value="Excelente relación costo-beneficio, garantía de 2 años en sitio y menor costo de flete regional.",
            key="ind_crit_sel"
        )

    # Cálculos
    p1_subtotal = p1_precio + p1_flete
    p1_iva = p1_subtotal * 0.16
    p1_total = p1_subtotal + p1_iva

    p2_subtotal = p2_precio + p2_flete
    p2_iva = p2_subtotal * 0.16
    p2_total = p2_subtotal + p2_iva

    p3_subtotal = p3_precio + p3_flete
    p3_iva = p3_subtotal * 0.16
    p3_total = p3_subtotal + p3_iva

    st.markdown("---")
    st.markdown("##### 📊 Tabla Comparativa de Ofertas Mercado Nacional (MXN)")

    df_cot = pd.DataFrame([
        {
            "Concepto / Rubro": "Precio Base Maquinaria",
            p1_nombre: f"${p1_precio:,.2f}",
            p2_nombre: f"${p2_precio:,.2f}",
            p3_nombre: f"${p3_precio:,.2f}"
        },
        {
            "Concepto / Rubro": "Flete y Maniobras (Puesto en Planta)",
            p1_nombre: f"${p1_flete:,.2f}",
            p2_nombre: f"${p2_flete:,.2f}",
            p3_nombre: f"${p3_flete:,.2f}"
        },
        {
            "Concepto / Rubro": "Subtotal Antes de IVA",
            p1_nombre: f"${p1_subtotal:,.2f}",
            p2_nombre: f"${p2_subtotal:,.2f}",
            p3_nombre: f"${p3_subtotal:,.2f}"
        },
        {
            "Concepto / Rubro": "IVA (16%)",
            p1_nombre: f"${p1_iva:,.2f}",
            p2_nombre: f"${p2_iva:,.2f}",
            p3_nombre: f"${p3_iva:,.2f}"
        },
        {
            "Concepto / Rubro": "PRECIO TOTAL PUESTO EN SITIO",
            p1_nombre: f"${p1_total:,.2f}",
            p2_nombre: f"${p2_total:,.2f}",
            p3_nombre: f"${p3_total:,.2f}"
        }
    ])
    st.dataframe(df_cot, use_container_width=True)
    st.success(f"✅ **Proveedor Seleccionado:** {prov_seleccionado} | **Justificación:** {criterio_sel}")
