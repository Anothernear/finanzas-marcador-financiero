"""
tabla_comparativa.py — Tabla comparativa de los 3 presupuestos y selección de proveedor.

Muestra:
- DataFrame con todos los rubros por proveedor.
- Highlight del proveedor con menor Total DDP.
- Selectbox para proveedor elegido + campo de justificación.
- Guarda la selección en state.py.
"""

import streamlit as st
import pandas as pd
from . import state


def render_tabla_comparativa(idx_activo: int, nombre_activo: str):
    """
    Renderiza la tabla comparativa de 3 presupuestos para el activo dado.

    Args:
        idx_activo: Índice del activo en la lista de sesión.
        nombre_activo: Nombre del activo para el encabezado.
    """
    activos = state.get_activos()
    if idx_activo < 0 or idx_activo >= len(activos):
        st.warning("Activo no encontrado en la sesión.")
        return

    activo = activos[idx_activo]
    presupuestos = activo.get("presupuestos", [])

    if not presupuestos or all(p.get("total_ddp", 0.0) == 0.0 for p in presupuestos):
        st.info(
            "⏳ Aún no se han capturado los 3 presupuestos para este activo. "
            "Llénalos en la sección de arriba y presiona **Guardar los 3 Presupuestos**."
        )
        return

    # ── Construir DataFrame comparativo ──────────────────────────────────────
    nombres_prov = [
        p.get("nombre") or f"Proveedor {i+1}"
        for i, p in enumerate(presupuestos)
    ]

    rubros = [
        ("Precio Base del Equipo ($MXN)", "precio_base"),
        ("Flete y Maniobras ($MXN)", "flete"),
        ("Instalación y Puesta en Marcha ($MXN)", "instalacion"),
        ("Subtotal Antes de IVA ($MXN)", "subtotal"),
        ("IVA 16% ($MXN)", "iva"),
        ("TOTAL DDP — Puesto en Planta ($MXN)", "total_ddp"),
        ("Garantía (meses)", "garantia"),
        ("¿Incluye Capacitación?", "capacitacion"),
        ("Tiempo de Entrega", "tiempo_entrega"),
        ("Folio de Cotización", "folio"),
        ("Vigencia de la Cotización", "vigencia"),
    ]

    filas = []
    for lbl, campo in rubros:
        fila = {"Concepto / Rubro": lbl}
        for i, (prov_nombre, pres) in enumerate(zip(nombres_prov, presupuestos)):
            val = pres.get(campo, "—")
            if campo in ("precio_base", "flete", "instalacion", "subtotal", "iva", "total_ddp"):
                fila[prov_nombre] = f"${float(val):,.2f}"
            elif campo == "garantia":
                fila[prov_nombre] = f"{val} meses" if val else "Sin garantía"
            elif campo == "capacitacion":
                fila[prov_nombre] = "✅ Sí" if val else "❌ No"
            else:
                fila[prov_nombre] = str(val) if val else "—"
        filas.append(fila)

    df_comp = pd.DataFrame(filas)

    # ── Highlight del proveedor con menor Total DDP ───────────────────────────
    totales = [p.get("total_ddp", float("inf")) for p in presupuestos]
    idx_menor = totales.index(min(t for t in totales if t > 0)) if any(t > 0 for t in totales) else -1

    st.markdown(f"##### 📊 Tabla Comparativa — {nombre_activo}")

    if idx_menor >= 0:
        st.success(
            f"💡 **Opción de menor costo total:** {nombres_prov[idx_menor]} "
            f"— Total DDP: **${totales[idx_menor]:,.2f} MXN**"
        )

    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # ── Selección de proveedor ────────────────────────────────────────────────
    st.markdown("##### 🎯 Selección del Proveedor")

    sel_previa = activo.get("proveedor_sel") or {}
    idx_sel_prev = sel_previa.get("idx", 0)
    criterio_prev = sel_previa.get("criterio", "")

    opciones = [f"Proveedor {i+1} — {n}" for i, n in enumerate(nombres_prov)]

    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        sel_opcion = st.selectbox(
            "Proveedor seleccionado:",
            options=opciones,
            index=min(idx_sel_prev, len(opciones) - 1),
            key=f"tc_{idx_activo}_sel_prov",
        )
        idx_sel = opciones.index(sel_opcion)

        total_sel = presupuestos[idx_sel].get("total_ddp", 0.0)
        unidades = activo["ficha"].get("unidades", 1)
        st.metric(
            "Total a Invertir (este activo)",
            f"${total_sel * unidades:,.2f} MXN",
            help=f"Total DDP × {unidades} unidad(es)",
        )

    with col_s2:
        criterio = st.text_area(
            "Criterio y Justificación de Selección:",
            value=criterio_prev,
            placeholder=(
                "Ej: Mejor relación costo-beneficio, garantía de 2 años en sitio, "
                "menor tiempo de entrega, proveedor certificado ISO 9001..."
            ),
            height=110,
            key=f"tc_{idx_activo}_criterio",
        )

    if st.button(
        "✅ Confirmar Selección de Proveedor",
        key=f"tc_{idx_activo}_confirmar",
        type="primary",
    ):
        if not criterio.strip():
            st.warning("⚠️ Por favor escribe la justificación antes de confirmar.")
        else:
            state.seleccionar_proveedor(idx_activo, idx_sel, criterio.strip())
            st.success(
                f"✅ Proveedor confirmado: **{nombres_prov[idx_sel]}** | "
                f"Total: **${total_sel * unidades:,.2f} MXN**"
            )
            st.rerun()
