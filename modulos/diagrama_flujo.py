import streamlit as st

def render_diagrama_flujo():
    """
    Módulo de Ingeniería de Producción: Diagrama de Flujo (Mermaid.js ANSI) y Estudio de Tiempos y Movimientos.
    """
    st.markdown("#### ⚙️ Fase 2: Ingeniería de Producción y Balance Operativo")
    st.caption("Diagrama de flujo en Mermaid.js estándar ANSI y Estudio Cronológico de Tiempos y Movimientos.")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("##### 🔀 Diagrama de Flujo del Proceso (Simbología ANSI / Code)")
        default_mermaid = """graph TD
    A([Inicio: Recepción de Materia Prima]) --> B[/Entrada: Insumos e Inspección/]
    B --> C{¿Materia Prima Conforme?}
    C -- No --> D[Rechazo y Devolución a Proveedor]
    C -- Sí --> E[Operación 1: Mezclado y Formulación]
    E --> F[Operación 2: Transformación / Maquinado]
    F --> G[Operación 3: Envasado y Empaque]
    G --> H{¿Inspección de Calidad Final?}
    H -- No --> I[Scrap / Reproceso]
    H -- Sí --> J[/Salida: Producto Terminado/]
    J --> K([Fin: Almacén de Producto Terminado])"""

        mermaid_code = st.text_area(
            "Código Mermaid.js del Proceso:",
            value=default_mermaid,
            height=250,
            key="ind_mermaid_code"
        )
        st.markdown("##### 📌 Renderizado del Diagrama:")
        st.markdown(f"```mermaid\n{mermaid_code}\n```")

    with col_b:
        st.markdown("##### ⏱️ Estudio de Tiempos y Movimientos (Por Lote de Producción)")
        t_setup = st.number_input("Tiempo de Preparación / Set-up (min):", min_value=0.0, value=30.0, step=5.0, key="ind_t_setup")
        t_transf = st.number_input("Tiempo Efectivo de Transformación (min):", min_value=0.1, value=120.0, step=5.0, key="ind_t_transf")
        t_espera = st.number_input("Tiempos Muertos / Espera / Inspección (min):", min_value=0.0, value=15.0, step=5.0, key="ind_t_espera")
        tam_lote = st.number_input("Tamaño del Lote (Unidades por ciclo):", min_value=1, value=500, step=10, key="ind_tam_lote")

        t_total_ciclo = t_setup + t_transf + t_espera
        t_total_horas = t_total_ciclo / 60.0

        # Almacenar en session_state para uso inter-módulo (prorrateo de energía CFE)
        st.session_state.tam_lote_val = tam_lote
        st.session_state.t_total_horas_val = t_total_horas

        cap_efectiva_hora = (tam_lote / t_total_horas) if t_total_horas > 0 else 0
        eficiencia_operativa = (t_transf / t_total_ciclo * 100) if t_total_ciclo > 0 else 0

        st.markdown("---")
        st.markdown("###### 📊 Resumen del Ciclo Operativo:")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.metric("Tiempo Total de Ciclo", f"{t_total_ciclo:.1f} min", delta=f"{t_total_horas:.2f} horas/lote")
            st.metric("Eficiencia de Transformación", f"{eficiencia_operativa:.1f}%", help="Tiempo efectivo sobre tiempo total")
        with col_t2:
            st.metric("Capacidad Efectiva Real", f"{cap_efectiva_hora:.0f} unid/hora")
            st.metric("Tiempo Muerto + Set-up", f"{t_setup + t_espera:.1f} min", delta_color="inverse")
