import streamlit as st
import pandas as pd
import numpy as np

def generar_codigo_mermaid_desde_df(df_pasos):
    """
    Motor interno que convierte la tabla de actividades del usuario en código Mermaid.js válido
    utilizando simbología estándar ANSI/programación sin que el usuario escriba código.
    """
    lines = ["graph TD"]
    
    if df_pasos.empty:
        return "graph TD\n    A([Inicio del Proceso]) --> B([Fin del Proceso])"
    
    node_ids = []
    for idx, row in df_pasos.iterrows():
        nid = f"N{idx+1}"
        node_ids.append(nid)
        nombre = str(row.get("Actividad / Etapa", f"Paso {idx+1}")).strip().replace('"', '').replace("'", "").replace('\n', ' ')
        tipo_simb = str(row.get("Simbología ANSI", "⚙️ Operación / Proceso"))
        
        # Asignar forma Mermaid según simbología ANSI
        if "Inicio" in tipo_simb or "Fin" in tipo_simb:
            shape = f'{nid}(["{nombre}"])'
        elif "Decisión" in tipo_simb or "Inspección" in tipo_simb:
            shape = f'{nid}{{"{nombre}"}}'
        elif "Entrada" in tipo_simb or "Salida" in tipo_simb:
            shape = f'{nid}[/"{nombre}"/]'
        else:  # Operación / Proceso
            shape = f'{nid}["{nombre}"]'
            
        lines.append(f"    {shape}")
    
    # Enlazar pasos secuenciales
    for i in range(len(node_ids) - 1):
        curr_id = node_ids[i]
        next_id = node_ids[i+1]
        tipo_curr = str(df_pasos.iloc[i].get("Simbología ANSI", ""))
        
        if "Decisión" in tipo_curr or "Inspección" in tipo_curr:
            lines.append(f'    {curr_id} -- "Conforme / Sí" --> {next_id}')
            # Si hay un rechazo/reproceso en inspección
            lines.append(f'    {curr_id} -. "No Conforme" .-> R{i+1}["Scrap / Reproceso"]')
        else:
            lines.append(f"    {curr_id} --> {next_id}")
            
    return "\n".join(lines)


def render_diagrama_flujo():
    """
    Motor Interactivo de Diagrama de Flujo, Tiempos y Movimientos, y Balance de Consumo kWh.
    Permite modificar actividades directamente desde la interfaz gráfica sin escribir código.
    """
    st.markdown("#### ⚙️ Motor Interactivo: Diagrama de Flujo, Estudio de Tiempos y Consumo Energético")
    st.caption("Crea y modifica las actividades de tu proceso directamente en la tabla. El sistema construirá el diagrama ANSI, calculará los tiempos y generará la tabla de consumo kW/h automáticamente.")

    # Datos por defecto parametrizables para iniciar el motor
    if "df_actividades_proceso" not in st.session_state:
        sample_actividades = [
            {
                "Paso": 1,
                "Actividad / Etapa": "Recepción de Materia Prima",
                "Simbología ANSI": "🚀 Inicio / Fin (Cápsula)",
                "Set-up (min)": 15.0,
                "Transformación (min)": 0.0,
                "Espera/Muerto (min)": 5.0,
                "Potencia (kW)": 1.5,
                "Factor Carga (%)": 50
            },
            {
                "Paso": 2,
                "Actividad / Etapa": "Pesado y Formulación de Insumos",
                "Simbología ANSI": "📦 Entrada / Salida (Paralelogramo)",
                "Set-up (min)": 10.0,
                "Transformación (min)": 15.0,
                "Espera/Muerto (min)": 2.0,
                "Potencia (kW)": 3.0,
                "Factor Carga (%)": 60
            },
            {
                "Paso": 3,
                "Actividad / Etapa": "Mezclado Industrial y Homogeneizado",
                "Simbología ANSI": "⚙️ Operación / Proceso (Rectángulo)",
                "Set-up (min)": 5.0,
                "Transformación (min)": 45.0,
                "Espera/Muerto (min)": 0.0,
                "Potencia (kW)": 18.5,
                "Factor Carga (%)": 85
            },
            {
                "Paso": 4,
                "Actividad / Etapa": "Inspección de Calidad y Mezcla",
                "Simbología ANSI": "🔍 Decisión / Inspección (Rombo)",
                "Set-up (min)": 2.0,
                "Transformación (min)": 10.0,
                "Espera/Muerto (min)": 5.0,
                "Potencia (kW)": 0.5,
                "Factor Carga (%)": 40
            },
            {
                "Paso": 5,
                "Actividad / Etapa": "Envasado, Empaque y Sellado Automatizado",
                "Simbología ANSI": "⚙️ Operación / Proceso (Rectángulo)",
                "Set-up (min)": 10.0,
                "Transformación (min)": 60.0,
                "Espera/Muerto (min)": 3.0,
                "Potencia (kW)": 22.0,
                "Factor Carga (%)": 80
            },
            {
                "Paso": 6,
                "Actividad / Etapa": "Almacenamiento de Producto Terminado",
                "Simbología ANSI": "🚀 Inicio / Fin (Cápsula)",
                "Set-up (min)": 5.0,
                "Transformación (min)": 0.0,
                "Espera/Muerto (min)": 10.0,
                "Potencia (kW)": 2.0,
                "Factor Carga (%)": 30
            }
        ]
        st.session_state.df_actividades_proceso = pd.DataFrame(sample_actividades)

    # Parametrización del Lote
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        tam_lote = st.number_input("📦 Tamaño del Lote (Unidades por ciclo):", min_value=1, value=500, step=25, key="ind_tam_lote_motor")
    with col_l2:
        horas_turno = st.number_input("⏱️ Horas del Turno Diario (hrs):", min_value=1, max_value=24, value=8, key="ind_hrs_turno_motor")
    with col_l3:
        dias_mes = st.number_input("🗓️ Días Operativos al Mes:", min_value=1, max_value=31, value=24, key="ind_dias_mes_motor")

    st.markdown("---")
    st.markdown("##### 📝 1. Tabla Editable de Actividades del Proceso (Modifica directamente aquí)")
    st.caption("Añade, edita o elimina filas para ajustar los pasos. El diagrama ANSI y las métricas se actualizarán instantáneamente.")

    # Data Editor interactivo para modificar el flujo sin escribir código
    opciones_simbologia = [
        "🚀 Inicio / Fin (Cápsula)",
        "⚙️ Operación / Proceso (Rectángulo)",
        "🔍 Decisión / Inspección (Rombo)",
        "📦 Entrada / Salida (Paralelogramo)"
    ]

    edited_df = st.data_editor(
        st.session_state.df_actividades_proceso,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Paso": st.column_config.NumberColumn("Paso #", min_value=1, step=1, required=True),
            "Actividad / Etapa": st.column_config.TextColumn("Nombre de la Actividad / Etapa", required=True, width="large"),
            "Simbología ANSI": st.column_config.SelectboxColumn("Simbología ANSI (Forma)", options=opciones_simbologia, required=True, width="medium"),
            "Set-up (min)": st.column_config.NumberColumn("Set-up (min)", min_value=0.0, step=1.0, format="%.1f min"),
            "Transformación (min)": st.column_config.NumberColumn("Transformación (min)", min_value=0.0, step=1.0, format="%.1f min"),
            "Espera/Muerto (min)": st.column_config.NumberColumn("T. Muerto / Espera (min)", min_value=0.0, step=1.0, format="%.1f min"),
            "Potencia (kW)": st.column_config.NumberColumn("Potencia Equipo (kW)", min_value=0.0, step=0.5, format="%.1f kW"),
            "Factor Carga (%)": st.column_config.NumberColumn("Factor Carga (%)", min_value=0, max_value=100, step=5, format="%d%%")
        },
        key="editor_motor_proceso"
    )

    st.session_state.df_actividades_proceso = edited_df

    # Generar código Mermaid automático desde el dataframe
    mermaid_auto = generar_codigo_mermaid_desde_df(edited_df)

    st.markdown("---")
    st.markdown("##### 📌 2. Diagrama de Flujo de Producción (Generado Automáticamente)")
    st.markdown(f"```mermaid\n{mermaid_auto}\n```")

    with st.expander("👁️ Ver Código Mermaid.js Generado Automáticamente"):
        st.code(mermaid_auto, language="mermaid")

    st.markdown("---")
    st.markdown("##### ⏱️ 3. Estudio de Tiempos, Movimientos y Capacidad de Planta")

    if not edited_df.empty:
        total_setup = float(edited_df["Set-up (min)"].sum())
        total_transf = float(edited_df["Transformación (min)"].sum())
        total_espera = float(edited_df["Espera/Muerto (min)"].sum())
        t_ciclo_total = total_setup + total_transf + total_espera
        t_ciclo_horas = t_ciclo_total / 60.0

        oee_eficiencia = (total_transf / t_ciclo_total * 100.0) if t_ciclo_total > 0 else 0.0
        capacidad_hora = (tam_lote / t_ciclo_horas) if t_ciclo_horas > 0 else 0.0
        lotes_por_turno = (horas_turno * 60.0 / t_ciclo_total) if t_ciclo_total > 0 else 0.0
        produccion_diaria = lotes_por_turno * tam_lote

        # Guardar en session_state para consumo inter-módulo (CFE)
        st.session_state.tam_lote_val = tam_lote
        st.session_state.t_total_horas_val = t_ciclo_horas

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Tiempo Total de Ciclo", f"{t_ciclo_total:.1f} min", delta=f"{t_ciclo_horas:.2f} hrs/lote")
        with col_m2:
            st.metric("Eficiencia de Transformación", f"{oee_eficiencia:.1f}%", help="Tiempo efectivo sobre tiempo total del lote")
        with col_m3:
            st.metric("Capacidad Efectiva Real", f"{capacidad_hora:,.0f} unid/hora")
        with col_m4:
            st.metric("Producción Estimada / Turno", f"{produccion_diaria:,.0f} unidades", delta=f"{lotes_por_turno:.1f} lotes/día")

    st.markdown("---")
    st.markdown("##### ⚡ 4. Tabla de Balance y Consumo de Energía (Kilowatts / Hora - kWh)")
    st.caption("Cálculo automático de consumo eléctrico individual por cada actividad y acumulado total por lote, día y mes.")

    if not edited_df.empty:
        df_energia = edited_df.copy()

        # Tiempo de operación de la maquinaria por lote (horas)
        df_energia["Tiempo Op. (hrs/lote)"] = (df_energia["Set-up (min)"] + df_energia["Transformación (min)"]) / 60.0
        
        # Consumo de potencia efectiva (kW efectivos = kW nominal * factor de carga %)
        df_energia["Potencia Efectiva (kW)"] = df_energia["Potencia (kW)"] * (df_energia["Factor Carga (%)"] / 100.0)
        
        # Consumo kWh por lote = Potencia efectiva kW * horas de operación por lote
        df_energia["Consumo kWh / Lote"] = df_energia["Potencia Efectiva (kW)"] * df_energia["Tiempo Op. (hrs/lote)"]
        
        # Consumo kWh Diario = kWh por lote * lotes por turno
        df_energia["Consumo kWh / Día"] = df_energia["Consumo kWh / Lote"] * lotes_por_turno
        
        # Consumo kWh Mensual = kWh diario * días operativos al mes
        df_energia["Consumo kWh / Mes"] = df_energia["Consumo kWh / Día"] * dias_mes

        # Formateo para la visualización
        df_disp_energia = pd.DataFrame({
            "Paso": df_energia["Paso"],
            "Actividad": df_energia["Actividad / Etapa"],
            "Potencia Nominal (kW)": df_energia["Potencia (kW)"].map("{:.1f} kW".format),
            "Factor Carga (%)": df_energia["Factor Carga (%)"].map("{:d}%".format),
            "Tiempo Op. (hrs/lote)": df_energia["Tiempo Op. (hrs/lote)"].map("{:.2f} hrs".format),
            "Consumo kWh / Lote": df_energia["Consumo kWh / Lote"].map("{:.2f} kWh".format),
            "Consumo kWh / Día": df_energia["Consumo kWh / Día"].map("{:.1f} kWh".format),
            "Consumo kWh / Mes": df_energia["Consumo kWh / Mes"].map("{:,.0f} kWh".format)
        })

        st.dataframe(df_disp_energia, use_container_width=True)

        kwh_total_lote = float(df_energia["Consumo kWh / Lote"].sum())
        kwh_total_dia = float(df_energia["Consumo kWh / Día"].sum())
        kwh_total_mes = float(df_energia["Consumo kWh / Mes"].sum())
        kw_demanda_maxima = float(df_energia["Potencia Efectiva (kW)"].sum())

        # Guardar balance energético calculado para el recibo CFE
        st.session_state.kwh_total_mes_calculado = kwh_total_mes
        st.session_state.kw_demanda_maxima_calculada = kw_demanda_maxima

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.metric("Demanda Máxima Coincidente", f"{kw_demanda_maxima:.1f} kW", help="Suma de potencias efectivas instaladas")
        with col_k2:
            st.metric("Consumo kWh por Lote", f"{kwh_total_lote:.2f} kWh/lote")
        with col_k3:
            st.metric("Consumo kWh Diario", f"{kwh_total_dia:.1f} kWh/día")
        with col_k4:
            st.metric("Consumo Energético Mensual", f"{kwh_total_mes:,.0f} kWh/mes", help="Integrado directamente al recibo CFE")
