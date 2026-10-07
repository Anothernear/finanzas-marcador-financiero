import streamlit as st
import pandas as pd

def render_inversion_inicial():
    """
    Módulo de Inversión Inicial y Ficha Técnica de Activos.
    Especificaciones técnicas de maquinaria, potencia, dimensiones, instalación y vida útil.
    """
    st.markdown("#### 🛠️ Fase 1A: Inversión Inicial y Ficha Técnica de Activos")
    st.caption("Especificaciones técnicas de la maquinaria y equipo nuevo indispensable para la operación.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("##### 📋 Ficha Técnica del Activo / Línea Principal")
        nombre_equipo = st.text_input(
            "Nombre de la Maquinaria / Equipo Principal:",
            value="Línea de Envasado y Empaque Automatizado",
            key="ind_nom_eq"
        )
        capacidad_nom = st.text_input(
            "Capacidad Nominal de Producción:",
            value="600 unidades / hora",
            key="ind_cap_nom"
        )
        potencia_kw = st.number_input(
            "Potencia Eléctrica Requerida (kW):",
            min_value=0.1,
            value=22.5,
            step=0.5,
            key="ind_pot_kw"
        )
        potencia_hp = potencia_kw * 1.34102
        st.caption(f"⚡ Equivalencia en HP: **{potencia_hp:.2f} HP**")

        factor_potencia_nom = st.slider(
            "Factor de Potencia Nominal (FP):",
            min_value=0.70,
            max_value=1.00,
            value=0.88,
            step=0.01,
            key="ind_fp_nom"
        )

    with col_right:
        st.markdown("##### 📐 Instalación y Vida Útil")
        dims_fisicas = st.text_input(
            "Dimensiones Físicas (Largo x Ancho x Alto m):",
            value="4.5m x 1.8m x 2.2m",
            key="ind_dims"
        )
        req_inst = st.text_area(
            "Requerimientos de Instalación / Acometida:",
            value="Trifásica 440V, Aire comprimido 90 PSI, Cimentación reforzada 15cm",
            key="ind_inst"
        )
        vida_util_anios = st.number_input(
            "Vida Útil Estimada (Años):",
            min_value=1,
            max_value=30,
            value=10,
            key="ind_vida_util"
        )

    st.markdown("---")
    st.markdown("##### 📄 Resumen Ficha Técnica Registrada")

    df_ficha = pd.DataFrame([
        {"Parámetro Técnico": "Equipo Principal", "Valor Especificado": nombre_equipo},
        {"Parámetro Técnico": "Capacidad Nominal", "Valor Especificado": capacidad_nom},
        {"Parámetro Técnico": "Potencia Requerida (kW / HP)", "Valor Especificado": f"{potencia_kw:.1f} kW ({potencia_hp:.2f} HP)"},
        {"Parámetro Técnico": "Factor de Potencia Nominal", "Valor Especificado": f"{factor_potencia_nom:.2f}"},
        {"Parámetro Técnico": "Dimensiones Físicas", "Valor Especificado": dims_fisicas},
        {"Parámetro Técnico": "Requerimientos de Acometida", "Valor Especificado": req_inst},
        {"Parámetro Técnico": "Vida Útil Estimada", "Valor Especificado": f"{vida_util_anios} años"}
    ])
    st.dataframe(df_ficha, use_container_width=True)
