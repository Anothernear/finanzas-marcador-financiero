"""
resumen_inversion.py — Vista consolidada de todos los activos y el total de inversión inicial.

Muestra:
- Lista de activos registrados con ficha y proveedor seleccionado.
- Tabla resumen: Activo | Proveedor | Total DDP | Unidades | Subtotal.
- Métrica principal: Total de Inversión Inicial a Solicitar.
- Botón para limpiar toda la sesión de inversión.
"""

import streamlit as st
import pandas as pd
from . import state


def render_resumen_inversion():
    """
    Renderiza el resumen consolidado de todos los activos y presupuestos en sesión.
    Muestra el monto total de inversión a solicitar.
    """
    activos = state.get_activos()

    st.markdown("#### 💼 Resumen de Solicitud de Inversión Inicial")

    if not activos:
        st.info(
            "📋 Aún no has registrado activos. "
            "Ve a la pestaña **'1️⃣ Inversión Inicial (Ficha Técnica)'** "
            "y agrega los equipos que necesitas cotizar."
        )
        return

    # ── Tabla resumen ─────────────────────────────────────────────────────────
    filas_resumen = []
    inversion_total = 0.0

    for i, activo in enumerate(activos):
        ficha = activo.get("ficha", {})
        presupuestos = activo.get("presupuestos", [])
        sel = activo.get("proveedor_sel")

        nombre_activo = ficha.get("nombre", f"Activo {i + 1}")
        unidades = ficha.get("unidades", 1)

        if sel is not None and presupuestos:
            idx_p = sel.get("idx", 0)
            pres_sel = presupuestos[idx_p] if idx_p < len(presupuestos) else {}
            nombre_prov = pres_sel.get("nombre") or f"Proveedor {idx_p + 1}"
            total_ddp = pres_sel.get("total_ddp", 0.0)
            total_activo = total_ddp * unidades
            estado = "✅ Completo"
        elif presupuestos:
            nombre_prov = "⏳ Sin seleccionar"
            total_ddp = 0.0
            total_activo = 0.0
            estado = "⏳ Falta seleccionar proveedor"
        else:
            nombre_prov = "📋 Sin presupuestos"
            total_ddp = 0.0
            total_activo = 0.0
            estado = "📋 Falta capturar presupuestos"

        inversion_total += total_activo

        filas_resumen.append({
            "N°": i + 1,
            "Activo / Maquinaria": nombre_activo,
            "Condición": ficha.get("condicion", "Nuevo"),
            "Unidades": unidades,
            "Proveedor Seleccionado": nombre_prov,
            "Total DDP c/u ($MXN)": f"${total_ddp:,.2f}" if total_ddp > 0 else "—",
            "Subtotal Activo ($MXN)": f"${total_activo:,.2f}" if total_activo > 0 else "—",
            "Estado": estado,
        })

    df_resumen = pd.DataFrame(filas_resumen)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Métrica principal ─────────────────────────────────────────────────────
    activos_completos = sum(1 for a in activos if a.get("proveedor_sel") is not None)
    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.metric(
            "📦 Total de Activos Registrados",
            len(activos),
        )
    with col_m2:
        st.metric(
            "✅ Activos con Proveedor Confirmado",
            activos_completos,
            delta=f"{len(activos) - activos_completos} pendiente(s)" if activos_completos < len(activos) else "Todos completos",
            delta_color="inverse" if activos_completos < len(activos) else "normal",
        )
    with col_m3:
        st.metric(
            "🏦 Total de Inversión Inicial a Solicitar",
            f"${inversion_total:,.2f} MXN",
            help="Suma de Totales DDP × Unidades de los proveedores seleccionados (IVA incluido).",
        )

    if inversion_total > 0:
        st.success(
            f"💰 **Monto Total de Inversión Inicial:** **${inversion_total:,.2f} MXN** "
            f"(IVA 16% incluido, puesto en planta)"
        )

    # ── Desglose por activo ───────────────────────────────────────────────────
    if any(a.get("proveedor_sel") is not None for a in activos):
        st.markdown("---")
        st.markdown("##### 📋 Detalle por Activo")

        for i, activo in enumerate(activos):
            ficha = activo.get("ficha", {})
            sel = activo.get("proveedor_sel")
            presupuestos = activo.get("presupuestos", [])
            nombre_activo = ficha.get("nombre", f"Activo {i + 1}")

            with st.expander(f"**{i + 1}. {nombre_activo}**", expanded=False):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f"**Unidades:** {ficha.get('unidades', 1)}")
                    st.markdown(f"**Condición:** {ficha.get('condicion', 'Nuevo')}")
                    if ficha.get("capacidad_nom"):
                        st.markdown(f"**Capacidad:** {ficha.get('capacidad_nom')}")
                    if ficha.get("vida_util"):
                        st.markdown(f"**Vida Útil:** {ficha.get('vida_util')} años")

                with col_d2:
                    if sel and presupuestos:
                        idx_p = sel.get("idx", 0)
                        pres_sel = presupuestos[idx_p] if idx_p < len(presupuestos) else {}
                        st.markdown(f"**Proveedor:** {pres_sel.get('nombre', '—')}")
                        st.markdown(f"**Total DDP:** ${pres_sel.get('total_ddp', 0.0):,.2f} MXN")
                        st.markdown(f"**Criterio:** {sel.get('criterio', '—')}")
                    else:
                        st.info("Sin proveedor confirmado.")

    # ── Control de sesión ─────────────────────────────────────────────────────
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.caption("⚠️ Esta acción elimina todos los activos y presupuestos de la sesión actual.")
        if st.button("🗑️ Limpiar Todo — Reiniciar Solicitud", key="resumen_reset", use_container_width=True):
            state.reset_inversion()
            st.success("✅ Solicitud de inversión reiniciada.")
            st.rerun()
    with col_btn2:
        st.caption(f"📝 Activos registrados en esta sesión: {len(activos)}")
