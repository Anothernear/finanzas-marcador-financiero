"""
presupuestos.py — Formulario de captura de 3 presupuestos comparativos por activo.

Reglas:
- Sin ningún valor de precio hardcodeado.
- Cálculo automático: Subtotal + IVA 16% = Total DDP (puesto en planta, MXN).
- Los datos se persisten en sesión mediante state.py.
"""

import streamlit as st
from datetime import date
from . import state


IVA_TASA = 0.16


def _calcular_totales(precio_base: float, flete: float, instalacion: float) -> dict:
    """Calcula subtotal, IVA y total DDP para un proveedor."""
    subtotal = precio_base + flete + instalacion
    iva = subtotal * IVA_TASA
    total_ddp = subtotal + iva
    return {
        "subtotal": round(subtotal, 2),
        "iva": round(iva, 2),
        "total_ddp": round(total_ddp, 2),
    }


def _formulario_proveedor(num: int, prefix: str, prev: dict) -> dict:
    """
    Renderiza el formulario de UN proveedor dentro de su columna.

    Args:
        num: Número del proveedor (1, 2 o 3) para etiquetas.
        prefix: Prefijo único de las llaves de widget.
        prev: Datos previos del proveedor para pre-poblar al editar.

    Returns:
        Dict con todos los datos capturados del proveedor.
    """
    p = prev or {}

    st.markdown(f"##### 🏢 Proveedor {num}")

    nombre = st.text_input(
        "Nombre / Razón Social:",
        value=p.get("nombre", ""),
        placeholder="Ej: Maquinaria del Bajío S.A. de C.V.",
        key=f"{prefix}nombre",
    )
    rfc = st.text_input(
        "RFC (opcional):",
        value=p.get("rfc", ""),
        placeholder="Ej: MBJ930415AB1",
        key=f"{prefix}rfc",
    )
    folio = st.text_input(
        "Número de Cotización / Folio:",
        value=p.get("folio", ""),
        placeholder="Ej: COT-2026-00123",
        key=f"{prefix}folio",
    )

    vigencia_prev = p.get("vigencia")
    if vigencia_prev:
        try:
            vigencia_prev = date.fromisoformat(str(vigencia_prev))
        except Exception:
            vigencia_prev = date.today()
    else:
        vigencia_prev = date.today()

    vigencia = st.date_input(
        "Vigencia de la cotización:",
        value=vigencia_prev,
        min_value=date.today(),
        key=f"{prefix}vigencia",
        help="Fecha límite en que el precio es válido según el proveedor.",
    )

    st.markdown("**💰 Desglose de Precios ($ MXN, sin IVA)**")

    precio_base = st.number_input(
        "Precio base del equipo:",
        min_value=0.0,
        value=float(p.get("precio_base", 0.0)),
        step=1000.0,
        format="%.2f",
        key=f"{prefix}precio_base",
        help="Precio del equipo indicado en la cotización formal, antes de IVA.",
    )
    flete = st.number_input(
        "Flete y maniobras (puesto en planta):",
        min_value=0.0,
        value=float(p.get("flete", 0.0)),
        step=500.0,
        format="%.2f",
        key=f"{prefix}flete",
        help="Costo de transporte y descarga hasta tu instalación.",
    )
    instalacion = st.number_input(
        "Instalación y puesta en marcha:",
        min_value=0.0,
        value=float(p.get("instalacion", 0.0)),
        step=500.0,
        format="%.2f",
        key=f"{prefix}instalacion",
        help="Costo de montaje, conexiones y arranque inicial.",
    )

    totales = _calcular_totales(precio_base, flete, instalacion)

    st.markdown("**📊 Cálculo Automático**")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Subtotal (sin IVA)", f"${totales['subtotal']:,.2f}")
    with col_c2:
        st.metric("IVA 16%", f"${totales['iva']:,.2f}")
    with col_c3:
        st.metric("Total DDP 🏭", f"${totales['total_ddp']:,.2f}")

    st.markdown("**📋 Condiciones Adicionales**")

    garantia = st.number_input(
        "Garantía (meses):",
        min_value=0,
        value=int(p.get("garantia", 0)),
        step=1,
        key=f"{prefix}garantia",
    )
    capacitacion = st.checkbox(
        "¿Incluye capacitación al personal?",
        value=bool(p.get("capacitacion", False)),
        key=f"{prefix}cap",
    )
    tiempo_entrega = st.text_input(
        "Tiempo de entrega estimado:",
        value=p.get("tiempo_entrega", ""),
        placeholder="Ej: 4 semanas, 60 días hábiles",
        key=f"{prefix}entrega",
    )
    observaciones = st.text_area(
        "Observaciones adicionales:",
        value=p.get("observaciones", ""),
        placeholder="Garantía extendida, repuestos incluidos, servicio técnico, etc.",
        height=80,
        key=f"{prefix}obs",
    )

    return {
        "nombre": nombre.strip(),
        "rfc": rfc.strip(),
        "folio": folio.strip(),
        "vigencia": vigencia.isoformat() if vigencia else "",
        "precio_base": float(precio_base),
        "flete": float(flete),
        "instalacion": float(instalacion),
        "subtotal": totales["subtotal"],
        "iva": totales["iva"],
        "total_ddp": totales["total_ddp"],
        "garantia": int(garantia),
        "capacitacion": bool(capacitacion),
        "tiempo_entrega": tiempo_entrega.strip(),
        "observaciones": observaciones.strip(),
    }


def render_presupuestos_form(idx_activo: int, nombre_activo: str):
    """
    Renderiza el formulario completo de 3 presupuestos para el activo indicado.

    Args:
        idx_activo: Índice del activo en la lista de sesión.
        nombre_activo: Nombre del activo para mostrarlo en el encabezado.
    """
    activos = state.get_activos()
    presupuestos_prev = activos[idx_activo].get("presupuestos", []) if 0 <= idx_activo < len(activos) else []

    def _prev(i: int) -> dict:
        return presupuestos_prev[i] if i < len(presupuestos_prev) else {}

    prefix = f"pres_{idx_activo}_"

    st.info(
        f"💡 **Orientación de precios en México:** Los precios ingresados deben corresponder a cotizaciones "
        f"formales emitidas por el proveedor en MXN. Verifica que incluya IVA, flete y condiciones reales "
        f"puestas en tu planta. No se admiten listas de precios de catálogo sin cotización formal."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        datos_p1 = _formulario_proveedor(1, f"{prefix}p1_", _prev(0))
    with col2:
        datos_p2 = _formulario_proveedor(2, f"{prefix}p2_", _prev(1))
    with col3:
        datos_p3 = _formulario_proveedor(3, f"{prefix}p3_", _prev(2))

    st.markdown("")
    if st.button(
        "💾 Guardar los 3 Presupuestos",
        key=f"{prefix}guardar",
        type="primary",
        use_container_width=True,
    ):
        presupuestos = [datos_p1, datos_p2, datos_p3]
        state.actualizar_presupuestos(idx_activo, presupuestos)
        st.success(f"✅ Presupuestos guardados para: **{nombre_activo}**")
        st.rerun()
