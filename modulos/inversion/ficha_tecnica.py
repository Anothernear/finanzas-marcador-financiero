"""
ficha_tecnica.py — Formulario de captura de la ficha técnica de un activo/maquinaria.

Reglas:
- Solo maquinaria/equipo NUEVO (no se aceptan usados).
- Sin ningún valor hardcodeado; todos los campos inician vacíos o en 0.
- Retorna un dict con los datos capturados.
"""

import streamlit as st


def render_ficha_form(idx: int | None = None, ficha_previa: dict | None = None) -> dict | None:
    """
    Renderiza el formulario de ficha técnica para un activo.

    Args:
        idx: Índice del activo en la lista de sesión (None si es nuevo).
        ficha_previa: Dict con datos previos para pre-poblar al editar.

    Returns:
        Dict con la ficha capturada si el usuario presiona Guardar, o None.
    """
    fp = ficha_previa or {}

    es_edicion = idx is not None
    prefix = f"ft_{idx}_" if es_edicion else "ft_new_"

    st.markdown("##### 📋 Ficha Técnica del Activo")
    st.caption(
        "Solo se aceptan maquinaria y equipos **nuevos** (sin uso previo). "
        "Llena todos los campos con la información técnica real del equipo a adquirir."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🏷️ Identificación del Activo**")

        nombre = st.text_input(
            "Nombre del Activo / Maquinaria:",
            value=fp.get("nombre", ""),
            placeholder="Ej: Tractor Agrícola John Deere 5075E",
            help="Especifica marca y modelo exacto si ya se identificó.",
            key=f"{prefix}nombre",
        )

        condicion = st.selectbox(
            "Condición del Activo:",
            ["Nuevo"],
            index=0,
            key=f"{prefix}condicion",
            help="Solo se permiten activos nuevos en esta solicitud.",
        )

        unidades = st.number_input(
            "Número de unidades a adquirir:",
            min_value=1,
            max_value=999,
            value=int(fp.get("unidades", 1)),
            step=1,
            key=f"{prefix}unidades",
            help="Cantidad de piezas/equipos del mismo tipo a comprar.",
        )

        capacidad_nom = st.text_input(
            "Capacidad Nominal de Producción / Operación:",
            value=fp.get("capacidad_nom", ""),
            placeholder="Ej: 4 ha/día, 600 kg/h, 200 L/turno",
            key=f"{prefix}cap_nom",
        )

        descripcion = st.text_area(
            "Descripción Técnica Detallada:",
            value=fp.get("descripcion", ""),
            placeholder=(
                "Ej: Motor diesel 75 HP, transmisión sincronizada de 9 velocidades, "
                "tracción 4x4, cabina cerrada con A/C, sistema hidráulico 3 puntos..."
            ),
            height=130,
            key=f"{prefix}descripcion",
        )

    with col_b:
        st.markdown("**⚡ Especificaciones Eléctricas y Físicas**")

        potencia_kw = st.number_input(
            "Potencia Eléctrica Requerida (kW):",
            min_value=0.0,
            value=float(fp.get("potencia_kw", 0.0)),
            step=0.5,
            format="%.2f",
            key=f"{prefix}pot_kw",
            help="Si el equipo es mecánico/hidráulico y no consume electricidad, deja en 0.",
        )
        if potencia_kw > 0:
            potencia_hp = potencia_kw * 1.34102
            st.caption(f"⚡ Equivalencia: **{potencia_hp:.2f} HP**")

        factor_potencia = st.slider(
            "Factor de Potencia Nominal (FP):",
            min_value=0.70,
            max_value=1.00,
            value=float(fp.get("factor_potencia", 0.85)),
            step=0.01,
            key=f"{prefix}fp",
            help="Aplica si es equipo eléctrico. Valor típico industrial: 0.85–0.95.",
        )

        dims = st.text_input(
            "Dimensiones Físicas (Largo × Ancho × Alto):",
            value=fp.get("dims", ""),
            placeholder="Ej: 4.50m × 1.80m × 2.20m",
            key=f"{prefix}dims",
        )

        req_inst = st.text_area(
            "Requisitos de Instalación / Acometida:",
            value=fp.get("req_inst", ""),
            placeholder=(
                "Ej: Trifásica 440V / 60 Hz, aire comprimido 90 PSI, "
                "cimentación reforzada 15 cm, fosa de drenaje..."
            ),
            height=100,
            key=f"{prefix}req_inst",
        )

        vida_util = st.number_input(
            "Vida Útil Estimada (años):",
            min_value=1,
            max_value=50,
            value=int(fp.get("vida_util", 10)),
            step=1,
            key=f"{prefix}vida_util",
        )

    st.markdown("**📝 Justificación**")
    justificacion = st.text_area(
        "Justificación de la Necesidad:",
        value=fp.get("justificacion", ""),
        placeholder=(
            "Explica por qué este activo es indispensable para el proyecto: "
            "qué proceso habilita, qué cuello de botella resuelve, "
            "qué capacidad productiva agrega..."
        ),
        height=90,
        key=f"{prefix}justif",
    )

    st.markdown("")
    lbl_btn = "💾 Actualizar Ficha Técnica" if es_edicion else "✅ Guardar Ficha Técnica"
    if st.button(lbl_btn, key=f"{prefix}btn_guardar", type="primary"):
        if not nombre.strip():
            st.error("⚠️ El nombre del activo es obligatorio.")
            return None

        ficha = {
            "nombre": nombre.strip(),
            "condicion": condicion,
            "unidades": int(unidades),
            "capacidad_nom": capacidad_nom.strip(),
            "descripcion": descripcion.strip(),
            "potencia_kw": float(potencia_kw),
            "factor_potencia": float(factor_potencia),
            "dims": dims.strip(),
            "req_inst": req_inst.strip(),
            "vida_util": int(vida_util),
            "justificacion": justificacion.strip(),
        }
        return ficha

    return None


def render_resumen_ficha(ficha: dict):
    """Muestra la tabla resumen de una ficha técnica ya guardada."""
    import pandas as pd

    potencia_kw = ficha.get("potencia_kw", 0.0)
    potencia_hp = potencia_kw * 1.34102

    rows = [
        {"Parámetro Técnico": "Nombre del Activo", "Valor Especificado": ficha.get("nombre", "—")},
        {"Parámetro Técnico": "Condición", "Valor Especificado": ficha.get("condicion", "Nuevo")},
        {"Parámetro Técnico": "Unidades a Adquirir", "Valor Especificado": str(ficha.get("unidades", 1))},
        {"Parámetro Técnico": "Capacidad Nominal", "Valor Especificado": ficha.get("capacidad_nom", "—") or "—"},
        {"Parámetro Técnico": "Potencia Requerida", "Valor Especificado": f"{potencia_kw:.2f} kW ({potencia_hp:.2f} HP)" if potencia_kw > 0 else "No aplica (equipo no eléctrico)"},
        {"Parámetro Técnico": "Factor de Potencia Nominal", "Valor Especificado": f"{ficha.get('factor_potencia', 0.85):.2f}" if potencia_kw > 0 else "N/A"},
        {"Parámetro Técnico": "Dimensiones Físicas", "Valor Especificado": ficha.get("dims", "—") or "—"},
        {"Parámetro Técnico": "Requisitos de Instalación", "Valor Especificado": ficha.get("req_inst", "—") or "—"},
        {"Parámetro Técnico": "Vida Útil Estimada", "Valor Especificado": f"{ficha.get('vida_util', 10)} años"},
        {"Parámetro Técnico": "Justificación", "Valor Especificado": ficha.get("justificacion", "—") or "—"},
        {"Parámetro Técnico": "Descripción Técnica", "Valor Especificado": ficha.get("descripcion", "—") or "—"},
    ]

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
