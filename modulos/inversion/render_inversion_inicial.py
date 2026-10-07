"""
render_inversion_inicial.py — Orquestador de la pestaña "Inversión Inicial (Ficha Técnica)".

Flujo:
1. Muestra la lista de activos ya registrados en sesión.
2. Botón para agregar un nuevo activo.
3. Para cada activo existente: expander con opción de ver/editar ficha.
4. Al final: resumen de inversión consolidado.
"""

import streamlit as st
from . import state
from .ficha_tecnica import render_ficha_form, render_resumen_ficha
from .resumen_inversion import render_resumen_inversion


def render_inversion_inicial():
    """
    Punto de entrada público para la pestaña de Inversión Inicial.
    Compatible con la firma existente en modulos/__init__.py.
    """
    st.markdown("#### 🛠️ Fase 1A: Inversión Inicial — Registro de Activos y Maquinaria")
    st.caption(
        "Registra cada activo/equipo **nuevo** que necesitas adquirir. "
        "Para cada uno se capturará la ficha técnica y posteriormente los 3 presupuestos comparativos."
    )

    activos = state.get_activos()

    # ── Activos ya registrados ────────────────────────────────────────────────
    if activos:
        st.markdown(f"**📦 Activos registrados en esta sesión: {len(activos)}**")
        st.markdown("---")

        for i, activo in enumerate(activos):
            ficha = activo.get("ficha", {})
            nombre = ficha.get("nombre", f"Activo {i + 1}")
            tiene_presup = bool(activo.get("presupuestos"))
            tiene_sel = activo.get("proveedor_sel") is not None

            # Badge de estado
            if tiene_sel:
                badge = "✅"
            elif tiene_presup:
                badge = "⏳"
            else:
                badge = "📋"

            with st.expander(f"{badge} **Activo {i + 1}: {nombre}**", expanded=False):
                col_exp1, col_exp2 = st.columns([3, 1])
                with col_exp1:
                    render_resumen_ficha(ficha)
                with col_exp2:
                    st.markdown("")
                    if activo.get("proveedor_sel"):
                        sel = activo["proveedor_sel"]
                        presupuestos = activo.get("presupuestos", [])
                        idx_p = sel.get("idx", 0)
                        pres_sel = presupuestos[idx_p] if idx_p < len(presupuestos) else {}
                        st.success(
                            f"✅ **Proveedor confirmado**\n\n"
                            f"{pres_sel.get('nombre', '—')}\n\n"
                            f"${pres_sel.get('total_ddp', 0.0):,.2f} MXN"
                        )
                    elif tiene_presup:
                        st.warning("⏳ Presupuestos capturados.\nFalta confirmar proveedor.")
                    else:
                        st.info("📋 Sin presupuestos aún.\nVe a la pestaña de cotizaciones.")

                    st.markdown("")
                    # Edición de ficha técnica
                    if st.toggle(f"✏️ Editar ficha", key=f"toggle_edit_{i}"):
                        st.markdown("---")
                        ficha_nueva = render_ficha_form(idx=i, ficha_previa=ficha)
                        if ficha_nueva:
                            state.actualizar_ficha(i, ficha_nueva)
                            st.success("✅ Ficha actualizada.")
                            st.rerun()

                    st.markdown("")
                    if st.button(
                        f"🗑️ Eliminar activo",
                        key=f"del_activo_{i}",
                        use_container_width=True,
                    ):
                        state.eliminar_activo(i)
                        st.rerun()

        st.markdown("---")

    # ── Formulario para agregar nuevo activo ──────────────────────────────────
    agregar_key = "mostrar_form_nuevo_activo"
    if agregar_key not in st.session_state:
        st.session_state[agregar_key] = False

    if not st.session_state[agregar_key]:
        if st.button(
            "➕ Agregar Nuevo Activo / Maquinaria",
            key="btn_agregar_activo",
            use_container_width=True,
            type="primary" if not activos else "secondary",
        ):
            st.session_state[agregar_key] = True
            st.rerun()
    else:
        st.markdown("### ➕ Nuevo Activo — Ficha Técnica")
        with st.container(border=True):
            ficha_nueva = render_ficha_form(idx=None, ficha_previa=None)
            if ficha_nueva:
                idx_nuevo = state.agregar_activo(ficha_nueva)
                st.session_state[agregar_key] = False
                st.success(f"✅ Activo registrado: **{ficha_nueva['nombre']}** (Activo #{idx_nuevo + 1})")
                st.rerun()

            if st.button("❌ Cancelar", key="btn_cancelar_nuevo"):
                st.session_state[agregar_key] = False
                st.rerun()

    # ── Resumen de inversión ──────────────────────────────────────────────────
    if activos:
        st.markdown("---")
        render_resumen_inversion()
