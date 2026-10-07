import streamlit as st
import pandas as pd

def render_balance_energetico():
    """
    Módulo de Balance Energético y Costeo Eléctrico con Tarifas Industriales CFE (GDMTO / GDMTH).
    Modela demanda facturable, energía base/intermedio/punta, ajuste por Factor de Potencia (FP) y costo unitario.
    """
    st.markdown("#### ⚡ Fase 3: Balance Energético y Costeo Eléctrico (Esquema CFE)")
    st.caption("Cálculo de recibo industrial CFE bajo tarifas GDMTO / GDMTH con penalización/bonificación por Factor de Potencia.")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("##### 🔌 Balance de Cargas Eléctricas")
        demanda_contratada_kw = st.number_input(
            "Demanda Contratada / Potencia Total Instalada (kW):",
            min_value=1.0, value=45.0, step=5.0, key="ind_demanda_kw"
        )
        factor_carga_pct = st.slider(
            "Factor de Carga / Utilización Promedio (%):",
            min_value=10, max_value=100, value=75, step=5, key="ind_fc_pct"
        )
        horas_diarias_op = st.number_input(
            "Horas Diarias de Operación de Planta:",
            min_value=1, max_value=24, value=12, key="ind_hrs_diarias"
        )
        dias_mes_op = st.number_input(
            "Días Operativos al Mes:",
            min_value=1, max_value=31, value=24, key="ind_dias_mes"
        )
        fp_real = st.slider(
            "Factor de Potencia de Planta (FP real):",
            min_value=0.60, max_value=1.00, value=0.92, step=0.01, key="ind_fp_real"
        )

    with col_b:
        st.markdown("##### 🏛️ Selección de Tarifa CFE e Indicadores")
        tarifa_sugerida = "GDMTH (Gran Demanda Media Tensión Horaria)" if demanda_contratada_kw > 100 else "GDMTO (Gran Demanda Media Tensión Ordinaria)"
        tipo_tarifa = st.selectbox(
            "Tarifa CFE Aplicable:",
            ["GDMTO (Gran Demanda Media Tensión Ordinaria)", "GDMTH (Gran Demanda Media Tensión Horaria)"],
            index=0 if demanda_contratada_kw <= 100 else 1,
            key="ind_tipo_tarifa"
        )
        st.info(f"💡 **Tarifa Recomendada por CFE según demanda de {demanda_contratada_kw:.1f} kW:** {tarifa_sugerida}")

        cargo_fijo_mes = st.number_input("Cargo Fijo Mensual CFE ($ MXN):", min_value=0.0, value=650.0, step=50.0, key="ind_cfg")
        costo_kw_capacidad = st.number_input("Precio por kW de Capacidad/Distribución ($/kW):", min_value=0.0, value=320.0, step=10.0, key="ind_p_kw")

        if "GDMTH" in tipo_tarifa:
            precio_kwh_base = st.number_input("Precio kWh Base ($ MXN):", min_value=0.0, value=1.45, step=0.05, key="ind_p_base")
            precio_kwh_inter = st.number_input("Precio kWh Intermedio ($ MXN):", min_value=0.0, value=1.95, step=0.05, key="ind_p_inter")
            precio_kwh_punta = st.number_input("Precio kWh Punta ($ MXN):", min_value=0.0, value=2.45, step=0.05, key="ind_p_punta")
            pct_base = 0.50
            pct_inter = 0.35
            pct_punta = 0.15
        else:
            precio_kwh_unico = st.number_input("Precio kWh Energía Único ($ MXN):", min_value=0.0, value=1.85, step=0.05, key="ind_p_unico")

    # Cálculos energéticos y financieros CFE
    potencia_efectiva_kw = demanda_contratada_kw * (factor_carga_pct / 100.0)
    consumo_diario_kwh = potencia_efectiva_kw * horas_diarias_op
    consumo_mensual_kwh = consumo_diario_kwh * dias_mes_op

    costo_capacidad_total = demanda_contratada_kw * costo_kw_capacidad

    if "GDMTH" in tipo_tarifa:
        kwh_base = consumo_mensual_kwh * pct_base
        kwh_inter = consumo_mensual_kwh * pct_inter
        kwh_punta = consumo_mensual_kwh * pct_punta
        costo_energia = (kwh_base * precio_kwh_base) + (kwh_inter * precio_kwh_inter) + (kwh_punta * precio_kwh_punta)
    else:
        costo_energia = consumo_mensual_kwh * precio_kwh_unico

    subtotal_recibo = cargo_fijo_mes + costo_capacidad_total + costo_energia

    # Penalización / Bonificación Factor de Potencia según Fórmulas CFE
    if fp_real < 0.90:
        pct_fp = (3.0 / 5.0) * ((0.90 / fp_real) - 1.0) * 100.0
        monto_fp = subtotal_recibo * (pct_fp / 100.0)
        txt_fp = f"⚠️ Penalización por Bajo FP ({fp_real:.2f} < 0.90): +{pct_fp:.2f}% (+${monto_fp:,.2f})"
    else:
        pct_fp = (1.0 / 4.0) * (1.0 - (0.90 / fp_real)) * 100.0
        monto_fp = -subtotal_recibo * (pct_fp / 100.0)
        txt_fp = f"✅ Bonificación por Alto FP ({fp_real:.2f} ≥ 0.90): -{pct_fp:.2f}% (-${abs(monto_fp):,.2f})"

    subtotal_con_fp = subtotal_recibo + monto_fp
    iva_cfe = subtotal_con_fp * 0.16
    total_recibo_cfe = subtotal_con_fp + iva_cfe

    # Prorrateo unitario de energía usando el lote y ciclo del estudio de tiempos
    lote_val = st.session_state.get("tam_lote_val", 500)
    hrs_val = st.session_state.get("t_total_horas_val", 2.75)
    unidades_mensuales_prod = (lote_val / (hrs_val if hrs_val > 0 else 1)) * horas_diarias_op * dias_mes_op
    costo_electrico_unitario = (total_recibo_cfe / unidades_mensuales_prod) if unidades_mensuales_prod > 0 else 0.0

    st.markdown("---")
    st.markdown("##### 📑 Desglose Estimado del Recibo Mensual CFE ($ MXN)")

    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    with col_res1:
        st.metric("Consumo Mensual", f"{consumo_mensual_kwh:,.0f} kWh", delta=f"{consumo_diario_kwh:,.1f} kWh/día")
    with col_res2:
        st.metric("Subtotal de Energía + Demanda", f"${subtotal_recibo:,.2f}")
    with col_res3:
        st.metric("Ajuste por FP", f"${monto_fp:,.2f}", delta=txt_fp.split(":")[0])
    with col_res4:
        st.metric("TOTAL RECIBO CFE (con IVA)", f"${total_recibo_cfe:,.2f}")

    st.markdown(f"**Ajuste Factor de Potencia:** {txt_fp}")

    st.markdown("###### 📊 Tabla Detallada del Recibo y Costo Unitario:")
    df_cfe_detalle = pd.DataFrame([
        {"Concepto CFE": "Cargo Fijo Mensual", "Monto ($ MXN)": f"${cargo_fijo_mes:,.2f}", "Observaciones": "Cuota fija de facturación"},
        {"Concepto CFE": "Demanda Facturable (Capacidad y Distribución)", "Monto ($ MXN)": f"${costo_capacidad_total:,.2f}", "Observaciones": f"{demanda_contratada_kw:.1f} kW × ${costo_kw_capacidad:,.2f}/kW"},
        {"Concepto CFE": "Costo por Energía Consumida (kWh)", "Monto ($ MXN)": f"${costo_energia:,.2f}", "Observaciones": f"{consumo_mensual_kwh:,.0f} kWh en tarifa {tipo_tarifa.split()[0]}"},
        {"Concepto CFE": "Ajuste Factor de Potencia (FP)", "Monto ($ MXN)": f"${monto_fp:,.2f}", "Observaciones": txt_fp},
        {"Concepto CFE": "IVA (16%)", "Monto ($ MXN)": f"${iva_cfe:,.2f}", "Observaciones": "Impuesto al valor agregado"},
        {"Concepto CFE": "COSTO ELÉCTRICO TOTAL MENSUAL", "Monto ($ MXN)": f"${total_recibo_cfe:,.2f}", "Observaciones": "Factura estimada puesto en planta"},
        {"Concepto CFE": "⚡ COSTO ELÉCTRICO UNITARIO POR UNIDAD", "Monto ($ MXN)": f"${costo_electrico_unitario:,.4f} / unidad", "Observaciones": f"Prorrateado sobre {unidades_mensuales_prod:,.0f} unidades/mes"}
    ])
    st.dataframe(df_cfe_detalle, use_container_width=True)
