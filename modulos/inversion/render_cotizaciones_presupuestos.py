"""
render_cotizaciones_presupuestos.py — Orquestador de la pestaña de Presupuestos y Cotizaciones.

Flujo:
1. Verifica que haya activos registrados en sesión.
2. Selectbox para elegir qué activo se va a cotizar.
3. Formulario de 3 presupuestos (presupuestos.py).
4. Tabla comparativa y selección de proveedor (tabla_comparativa.py).
"""

import streamlit as st
from . import state
from .presupuestos import render_presupuestos_form
from .tabla_comparativa import render_tabla_comparativa


def render_cotizaciones_presupuestos():
    """
    Punto de entrada público para la pestaña de Cotizaciones y Presupuestos.
    Compatible con la firma existente en modulos/__init__.py.
    """
    st.markdown("#### 💰 Fase 1B: Presupuestos y Cotizaciones Comparativas (Mercado Nacional)")
    st.caption(
        "Captura 3 presupuestos reales de distintos proveedores mexicanos para cada activo. "
        "Los precios deben corresponder a cotizaciones formales emitidas en MXN, "
        "puestas en planta (DDP), incluyendo IVA 16%."
    )

    activos = state.get_activos()

    if not activos:
        st.warning(
            "⚠️ **Primero registra los activos a cotizar.**\n\n"
            "Ve a la pestaña **'1️⃣ Inversión Inicial (Ficha Técnica)'** "
            "y agrega al menos un equipo o maquinaria antes de capturar presupuestos."
        )
        return

    # ── Selector de activo a cotizar ──────────────────────────────────────────
    nombres_activos = [
        f"Activo {i + 1} — {a['ficha'].get('nombre', 'Sin nombre')}"
        for i, a in enumerate(activos)
    ]

    col_sel, col_estado = st.columns([2, 1])
    with col_sel:
        activo_opcion = st.selectbox(
            "🎯 Selecciona el activo a cotizar:",
            options=nombres_activos,
            key="cot_sel_activo",
            help="Elige el equipo para el que quieres capturar los 3 presupuestos de proveedores.",
        )
    with col_estado:
        idx_activo = nombres_activos.index(activo_opcion)
        activo_sel = activos[idx_activo]
        presup = activo_sel.get("presupuestos", [])
        prov_sel = activo_sel.get("proveedor_sel")

        if prov_sel:
            st.success("✅ Proveedor confirmado")
        elif presup:
            st.warning("⏳ Presupuestos sin confirmar")
        else:
            st.info("📋 Sin presupuestos aún")

    nombre_activo = activos[idx_activo]["ficha"].get("nombre", f"Activo {idx_activo + 1}")

    st.markdown("---")

    # ── Formulario 3 proveedores ───────────────────────────────────────────────
    st.markdown(f"##### ✍️ Captura de Presupuestos — **{nombre_activo}**")
    render_presupuestos_form(idx_activo, nombre_activo)

    # ── Tabla comparativa + selección ─────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"##### 📊 Comparativa y Selección de Proveedor — **{nombre_activo}**")
    render_tabla_comparativa(idx_activo, nombre_activo)
