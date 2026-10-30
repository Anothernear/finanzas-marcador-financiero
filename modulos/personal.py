import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime, date
from modulos.auth import cargar_usuarios, guardar_usuarios, hash_password, render_user_badge_sidebar
from modulos.biometrico import modal_simulador_huella
from modulos.ticket_printer import mostrar_dialogo_ticket, render_verificador_pago_simulado
from modulos.sistema_integral import generar_svg_producto, asegurar_columnas_productos

def actualizar_metodo_pago_ticket(folio: str, nuevo_metodo: str, csv_file: str = "hermes_financial_db.csv") -> bool:
    """
    Actualiza el método de pago de una transacción/ticket en la base de datos CSV
    y en el estado de sesión activo del ticket.
    """
    if not os.path.exists(csv_file):
        return False
    try:
        df = pd.read_csv(csv_file)
        if 'folio' not in df.columns or 'metodo_pago' not in df.columns:
            return False
        
        folio_limpio = str(folio).strip()
        mask = (df['folio'].astype(str).str.strip() == folio_limpio) & (df['tipo'] == 'venta')
        if not mask.any():
            return False
            
        df.loc[mask, 'metodo_pago'] = nuevo_metodo
        df.to_csv(csv_file, index=False)
        
        # Sincronizar el ticket activo en sesión si corresponde al mismo folio
        if 'ultimo_ticket' in st.session_state and st.session_state.ultimo_ticket:
            if str(st.session_state.ultimo_ticket.get('folio', '')).strip() == folio_limpio:
                st.session_state.ultimo_ticket['metodo_pago'] = nuevo_metodo
                
        return True
    except Exception as e:
        print(f"Error al actualizar método de pago en ticket: {e}")
        return False

def render_administracion_personal(df_db: pd.DataFrame):
    """
    Panel de Gerencia: Administración de Personal, Auditoría de Ventas por Cajero y Jornada,
    y Bitácora de Autorizaciones Biométricas.
    """
    st.markdown("### 👥 Administración de Personal & Auditoría de Jornadas")
    st.caption("Panel exclusivo de Gerencia para gestionar cajeros, supervisar cobros en tiempo real y auditar autorizaciones.")

    sub_emp1, sub_emp2, sub_emp3 = st.tabs([
        "👤 Gestión de Empleados y Cuentas",
        "📊 Ventas por Empleado y Jornada",
        "👆 Bitácora de Huella y Autorizaciones"
    ])

    df_usuarios = cargar_usuarios()

    # -------------------------------------------------------------
    # 1. GESTIÓN DE EMPLEADOS
    # -------------------------------------------------------------
    with sub_emp1:
        st.markdown("#### 📋 Empleados y Usuarios del Sistema")
        st.caption("Administra los permisos de acceso y el estado de los cajeros.")

        # Mostrar tabla de empleados actuales
        df_disp = df_usuarios[['username', 'nombre', 'rol', 'activo', 'pin_biometrico', 'fecha_registro']].copy()
        df_disp.columns = ['Usuario', 'Nombre Completo', 'Rol', 'Activo', 'PIN Biométrico', 'Fecha Registro']
        
        # Mapeo visual de roles
        df_disp['Rol'] = df_disp['Rol'].map({'gerente': '👑 Gerente', 'empleado': '👤 Empleado / Cajero'})
        st.dataframe(df_disp, use_container_width=True)

        st.markdown("---")
        col_nuevo, col_mod = st.columns([1, 1])

        with col_nuevo:
            with st.container(border=True):
                st.markdown("##### ➕ Registrar Nuevo Empleado / Cajero")
                with st.form("form_alta_empleado", clear_on_submit=True):
                    nuevo_nombre = st.text_input("Nombre Completo:", placeholder="ej. Carlos Sánchez")
                    nuevo_usuario = st.text_input("Nombre de Usuario (@):", placeholder="ej. csanchez")
                    nuevo_rol = st.selectbox("Rol:", ["empleado", "gerente"], format_func=lambda r: "👤 Empleado (Cajero)" if r == 'empleado' else "👑 Gerente (Administrador)")
                    nuevo_pass = st.text_input("Contraseña de Acceso:", type="password", placeholder="••••••••")
                    nuevo_pin = st.text_input("PIN Biométrico (4 dígitos):", value="1234", max_chars=6)
                    
                    btn_crear = st.form_submit_button("💾 Guardar Usuario", type="primary", use_container_width=True)

                    if btn_crear:
                        if not nuevo_nombre.strip() or not nuevo_usuario.strip() or not nuevo_pass:
                            st.error("⚠️ Todos los campos son obligatorios.")
                        elif nuevo_usuario.strip().lower() in df_usuarios['username'].str.lower().tolist():
                            st.error(f"⚠️ El nombre de usuario @{nuevo_usuario} ya está en uso.")
                        else:
                            nuevo_registro = {
                                "username": nuevo_usuario.strip().lower(),
                                "nombre": nuevo_nombre.strip(),
                                "password_hash": hash_password(nuevo_pass),
                                "rol": nuevo_rol,
                                "pin_biometrico": nuevo_pin.strip(),
                                "activo": True,
                                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            df_actualizado = pd.concat([df_usuarios, pd.DataFrame([nuevo_registro])], ignore_index=True)
                            guardar_usuarios(df_actualizado)
                            st.success(f"¡Usuario @{nuevo_usuario} creado exitosamente!")
                            st.rerun()

        with col_mod:
            with st.container(border=True):
                st.markdown("##### ⚙️ Activar / Suspender o Cambiar Clave")
                usuarios_modificables = df_usuarios['username'].tolist()
                user_a_mod = st.selectbox("Selecciona Usuario a Modificar:", usuarios_modificables)
                
                u_datos = df_usuarios[df_usuarios['username'] == user_a_mod].iloc[0]
                estado_actual = bool(u_datos['activo'])
                
                st.write(f"**Nombre:** {u_datos['nombre']} | **Rol:** {u_datos['rol'].capitalize()}")
                nuevo_estado = st.toggle("Cuenta Activa (Permite Login)", value=estado_actual, key=f"toggle_act_{user_a_mod}")

                cambiar_pass = st.checkbox("Restablecer Contraseña", key=f"chk_pw_{user_a_mod}")
                nueva_pass_input = ""
                if cambiar_pass:
                    nueva_pass_input = st.text_input("Nueva Contraseña:", type="password", key=f"new_pw_{user_a_mod}")

                if st.button("💾 Aplicar Cambios al Usuario", use_container_width=True):
                    idx = df_usuarios.index[df_usuarios['username'] == user_a_mod].tolist()[0]
                    df_usuarios.at[idx, 'activo'] = nuevo_estado
                    if cambiar_pass and nueva_pass_input:
                        df_usuarios.at[idx, 'password_hash'] = hash_password(nueva_pass_input)
                    guardar_usuarios(df_usuarios)
                    st.success(f"Cambios guardados para @{user_a_mod}")
                    st.rerun()

    # -------------------------------------------------------------
    # 2. VENTAS POR EMPLEADO Y JORNADA
    # -------------------------------------------------------------
    with sub_emp2:
        st.markdown("#### 📊 Desglose de Ventas por Empleado en su Jornada")
        st.caption("Supervisa los montos cobrados, métodos de pago y cantidad de tickets de cada cajero.")

        df_ventas = df_db[df_db['tipo'] == 'venta'].copy()
        if 'usuario' not in df_ventas.columns:
            df_ventas['usuario'] = 'sistema'

        # Filtros de búsqueda
        col_f_emp, col_f_fecha = st.columns([1, 1])
        with col_f_emp:
            lista_cajeros = ["Todos los Empleados"] + sorted(list(set(df_usuarios['username'].tolist() + df_ventas['usuario'].dropna().tolist())))
            cajero_sel = st.selectbox("Filtrar por Empleado / Cajero:", lista_cajeros)
        with col_f_fecha:
            filtro_tiempo = st.selectbox("Filtrar Período:", ["Hoy", "Ayer", "Últimos 7 días", "Todo el Historial"])

        # Aplicación de filtros
        df_filtrado = df_ventas.copy()
        hoy_str = date.today().strftime("%Y-%m-%d")
        ayer_str = (date.today() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        hace7_str = (date.today() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")

        if filtro_tiempo == "Hoy":
            df_filtrado = df_filtrado[df_filtrado['fecha'] == hoy_str]
        elif filtro_tiempo == "Ayer":
            df_filtrado = df_filtrado[df_filtrado['fecha'] == ayer_str]
        elif filtro_tiempo == "Últimos 7 días":
            df_filtrado = df_filtrado[df_filtrado['fecha'] >= hace7_str]

        if cajero_sel != "Todos los Empleados":
            df_filtrado = df_filtrado[df_filtrado['usuario'] == cajero_sel]

        total_recaudado = float(df_filtrado['monto'].sum()) if not df_filtrado.empty else 0.0
        cant_tickets = len(df_filtrado)
        ticket_prom = (total_recaudado / cant_tickets) if cant_tickets > 0 else 0.0

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.metric("Total Cobrado", f"${total_recaudado:,.2f}", delta=f"{filtro_tiempo}")
        with col_k2:
            st.metric("Tickets Emitidos", f"{cant_tickets}", delta="Transacciones")
        with col_k3:
            st.metric("Ticket Promedio", f"${ticket_prom:,.2f}")

        # Gráfico comparativo si se seleccionan todos
        if cajero_sel == "Todos los Empleados" and not df_filtrado.empty:
            df_agrup_emp = df_filtrado.groupby('usuario')['monto'].agg(['sum', 'count']).reset_index()
            df_agrup_emp.columns = ['Empleado', 'Venta Total ($)', 'Núm Tickets']
            
            fig_emp = px.bar(
                df_agrup_emp,
                x='Empleado',
                y='Venta Total ($)',
                text='Venta Total ($)',
                title="🏆 Ventas Totales por Empleado / Cajero",
                color='Venta Total ($)',
                color_continuous_scale='Blues'
            )
            fig_emp.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
            st.plotly_chart(fig_emp, use_container_width=True)

        st.markdown("##### 📜 Lista de Ventas Registradas")
        if not df_filtrado.empty:
            cols_mostrar = ['fecha', 'hora', 'folio', 'usuario', 'concepto', 'monto', 'metodo_pago']
            # Asegurar existencia de columnas
            for c in cols_mostrar:
                if c not in df_filtrado.columns:
                    df_filtrado[c] = ""
            df_tabla_v = df_filtrado[cols_mostrar].copy()
            df_tabla_v.columns = ['Fecha', 'Hora', 'Folio Ticket', 'Cajero', 'Concepto / Detalle', 'Monto ($)', 'Método Cobro']
            st.dataframe(df_tabla_v.sort_values(by=['Fecha', 'Hora'], ascending=False), use_container_width=True)

            with st.expander("💳 Rectificar Método de Pago de una Venta Registrada", expanded=False):
                lista_fol_adm = [f for f in df_filtrado['folio'].dropna().unique().tolist() if str(f).strip() != ""]
                if lista_fol_adm:
                    col_ad1, col_ad2, col_ad3 = st.columns([1.5, 1.5, 1])
                    with col_ad1:
                        fol_adm_sel = st.selectbox("Selecciona Folio a Modificar:", lista_fol_adm, key="sel_fol_admin_mp")
                    with col_ad2:
                        mp_adm_actual = df_filtrado[df_filtrado['folio'] == fol_adm_sel]['metodo_pago'].values[0] if not df_filtrado[df_filtrado['folio'] == fol_adm_sel].empty else "💵 Efectivo"
                        lista_mp = ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"]
                        idx_adm = lista_mp.index(mp_adm_actual) if mp_adm_actual in lista_mp else 0
                        nvo_mp_adm = st.selectbox("Nuevo Método de Cobro:", lista_mp, index=idx_adm, key="sel_nvo_mp_admin")
                    with col_ad3:
                        st.write("")
                        if st.button("💾 Guardar Cambio", use_container_width=True, key="btn_save_mp_admin"):
                            if nvo_mp_adm != mp_adm_actual:
                                actualizar_metodo_pago_ticket(fol_adm_sel, nvo_mp_adm)
                                st.success(f"¡Venta {fol_adm_sel} actualizada a {nvo_mp_adm}!")
                                st.rerun()
                            else:
                                st.info("Ya tiene ese método de cobro.")
        else:
            st.info("No se encontraron ventas para los filtros seleccionados.")

    # -------------------------------------------------------------
    # 3. BITÁCORA DE HUELLA Y AUTORIZACIONES
    # -------------------------------------------------------------
    with sub_emp3:
        st.markdown("#### 👆 Bitácora de Auditoría: Cambios de Fecha con Huella de Gerente")
        st.caption("Registro inmutable de todas las transacciones donde un cajero solicitó autorización biométrica para modificar la fecha/hora del sistema.")

        cols_bio = ['fecha', 'hora', 'folio', 'usuario', 'monto', 'autorizado_por', 'motivo_autorizacion']
        for cb in cols_bio:
            if cb not in df_db.columns:
                df_db[cb] = ""

        df_bio = df_db[df_db['autorizado_por'].astype(str).str.strip() != ""].copy()
        df_bio = df_bio[df_bio['autorizado_por'].notna()]

        if not df_bio.empty:
            st.warning(f"⚠️ Se han registrado **{len(df_bio)} transacciones con autorización especial de Gerencia**.")
            df_bio_disp = df_bio[['fecha', 'hora', 'folio', 'usuario', 'autorizado_por', 'motivo_autorizacion', 'monto']].copy()
            df_bio_disp.columns = ['Fecha Asignada', 'Hora', 'Folio', 'Cajero Solicitante', 'Gerente Autorizador', 'Motivo / Justificación', 'Monto ($)']
            st.dataframe(df_bio_disp.sort_values(by=['Fecha Asignada', 'Hora'], ascending=False), use_container_width=True)
        else:
            st.success("✅ **Bitácora Limpia:** No se han realizado registros retroactivos o con fecha alterada. Todas las ventas han sido en tiempo real.")

def render_dashboard_empleado(df_db: pd.DataFrame, usuario_actual: dict, m: dict, d: dict, archivo_productos: str = "productos_template.csv"):
    """
    Vista especializada y ergonómica para el Empleado / Cajero:
    - IZQUIERDA (Sidebar): Badge de cajero, corte de turno, métricas de jornada y último ticket emitido.
    - CENTRO (Pantalla Principal): Terminal Punto de Venta (POS) para cobrar productos del inventario,
      administrar la cuenta del cliente en tiempo real, solicitar autorización biométrica si se altera fecha
    """
    if not usuario_actual:
        usuario_actual = {}
    hoy_str = date.today().strftime("%Y-%m-%d")
    hoy_fecha = date.today()
    mi_usuario = usuario_actual.get('username', '')
    mi_nombre = usuario_actual.get('nombre', mi_usuario)

    # Filtrar ventas de este cajero hoy
    if 'usuario' not in df_db.columns:
        df_db['usuario'] = 'sistema'

    df_mis_ventas_hoy = df_db[
        (df_db['tipo'] == 'venta') & 
        (df_db['fecha'] == hoy_str) & 
        (df_db['usuario'] == mi_usuario)
    ].copy()

    total_mio_hoy = float(df_mis_ventas_hoy['monto'].sum()) if not df_mis_ventas_hoy.empty else 0.0
    tickets_mios_hoy = len(df_mis_ventas_hoy)
    pe_tienda = m.get('punto_equilibrio_diario', 0.0)
    ventas_global_hoy = d.get('venta_hoy', 0.0)
    avance_pct = (ventas_global_hoy / pe_tienda * 100) if pe_tienda > 0 else 100.0
    falta_vender = max(0.0, pe_tienda - ventas_global_hoy)

    # =============================================================
    # 1. BARRA LATERAL (IZQUIERDA) — RESUMEN, CORTE Y ÚLTIMO TICKET
    # =============================================================
    with st.sidebar:
        render_user_badge_sidebar()
        st.markdown("---")

        st.markdown("### 📊 Mi Jornada Hoy")
        st.metric("💵 Total Cobrado por Ti", f"${total_mio_hoy:,.2f}", delta=f"{tickets_mios_hoy} ticket(s)")
        st.metric("🎯 Meta Diaria Tienda", f"${pe_tienda:,.2f}", delta=f"{avance_pct:.1f}% cubierto")
        if falta_vender > 0:
            st.caption(f"Faltan **${falta_vender:,.2f}** globales para punto de equilibrio.")
        else:
            st.success("🎉 ¡Meta de hoy alcanzada!")

        st.markdown("---")
        st.markdown("### 📜 Mi Corte de Turno")
        if not df_mis_ventas_hoy.empty:
            res_pagos = df_mis_ventas_hoy.groupby('metodo_pago')['monto'].sum().to_dict()
            st.write(f"💵 **Efectivo:** ${res_pagos.get('💵 Efectivo', 0.0):,.2f}")
            total_tarj = float(res_pagos.get('💳 Tarjeta Débito', 0.0) + res_pagos.get('💳 Tarjeta Crédito', 0.0))
            st.write(f"💳 **Tarjetas:** ${total_tarj:,.2f}")
            st.write(f"🏦 **Transferencias:** ${res_pagos.get('🏦 Transferencia', 0.0):,.2f}")

            with st.expander(f"🧾 Ver mis {tickets_mios_hoy} cobros de hoy", expanded=False):
                st.dataframe(
                    df_mis_ventas_hoy[['hora', 'folio', 'monto', 'metodo_pago']].rename(
                        columns={'hora': 'Hora', 'folio': 'Folio', 'monto': 'Total', 'metodo_pago': 'Método'}
                    ).sort_values(by='Hora', ascending=False),
                    use_container_width=True,
                    height=180
                )
                lista_folios_turno = df_mis_ventas_hoy['folio'].dropna().unique().tolist()
                if lista_folios_turno:
                    st.markdown("---")
                    st.caption("✏️ **Rectificar método de un cobro anterior:**")
                    col_rf1, col_rf2 = st.columns([1.2, 1.8])
                    with col_rf1:
                        folio_corte_sel = st.selectbox("Ticket:", lista_folios_turno, key="sel_folio_corte_upd")
                    with col_rf2:
                        metodo_actual_corte = df_mis_ventas_hoy[df_mis_ventas_hoy['folio'] == folio_corte_sel]['metodo_pago'].values[0] if not df_mis_ventas_hoy[df_mis_ventas_hoy['folio'] == folio_corte_sel].empty else "💵 Efectivo"
                        lista_mp = ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"]
                        idx_corte = lista_mp.index(metodo_actual_corte) if metodo_actual_corte in lista_mp else 0
                        nuevo_mp_corte = st.selectbox("Nuevo método:", lista_mp, index=idx_corte, key="sel_mp_corte_upd")
                    if st.button("💾 Actualizar Registro", use_container_width=True, key="btn_act_mp_corte_upd"):
                        if nuevo_mp_corte != metodo_actual_corte:
                            actualizar_metodo_pago_ticket(folio_corte_sel, nuevo_mp_corte)
                            st.success(f"¡Ticket {folio_corte_sel} actualizado a {nuevo_mp_corte}!")
                            st.rerun()
                        else:
                            st.info("Ya tiene ese método de cobro.")
        else:
            st.info("Sin cobros registrados en tu turno aún.")

        st.markdown("---")
        st.markdown("### 🧾 Último Ticket Emitido")
        ultimo_tk = st.session_state.get('ultimo_ticket')
        if ultimo_tk:
            with st.container(border=True):
                st.markdown(f"""
                <div style="font-family: monospace; font-size: 0.85rem; background: #fafafa; padding: 10px; border-radius: 6px; border: 1px dashed #94a3b8;">
                    <div style="text-align: center; border-bottom: 1px dashed #cbd5e1; padding-bottom: 6px;">
                        <strong style="font-size: 0.95rem;">🧾 COMPROBANTE</strong><br>
                        <span style="color: #64748b;">Folio: <b>{ultimo_tk.get('folio', 'N/A')}</b></span><br>
                        <span style="color: #64748b; font-size: 0.8rem;">{ultimo_tk.get('fecha')} {ultimo_tk.get('hora')}</span><br>
                        <span style="color: #64748b; font-size: 0.8rem;">Atendido por: <b>{mi_nombre}</b></span>
                    </div>
                    <div style="margin: 8px 0;">
                """, unsafe_allow_html=True)
                for it in ultimo_tk.get('items', []):
                    st.markdown(f"<span style='font-family: monospace; font-size: 0.8rem;'>• {it['cantidad']}x {it['producto']} - ${it['subtotal']:,.2f}</span>", unsafe_allow_html=True)
                st.markdown(f"""
                    </div>
                    <div style="border-top: 1px dashed #cbd5e1; padding-top: 6px; text-align: right;">
                        <span style="font-size: 1.05rem; font-weight: bold;">TOTAL: ${ultimo_tk.get('monto', 0.0):,.2f}</span><br>
                        <span style="font-size: 0.8rem; color: #0284c7; font-weight: 600;">{ultimo_tk.get('metodo_pago', 'Efectivo')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("💳 Cambiar Método de Pago", expanded=False):
                    st.caption("¿El cliente decidió cambiar su forma de pago? Modifícalo aquí:")
                    lista_mp = ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"]
                    mp_actual = ultimo_tk.get('metodo_pago', '💵 Efectivo')
                    idx_mp = lista_mp.index(mp_actual) if mp_actual in lista_mp else 0
                    nuevo_mp_sb = st.selectbox("Forma de pago correcta:", lista_mp, index=idx_mp, key=f"sb_upd_mp_{ultimo_tk.get('folio')}")
                    if st.button("💾 Actualizar Ticket", use_container_width=True, key=f"btn_sb_upd_mp_{ultimo_tk.get('folio')}"):
                        if nuevo_mp_sb != mp_actual:
                            actualizar_metodo_pago_ticket(ultimo_tk.get('folio'), nuevo_mp_sb)
                            st.session_state.ultimo_ticket['metodo_pago'] = nuevo_mp_sb
                            st.success(f"¡Ticket {ultimo_tk.get('folio')} actualizado a {nuevo_mp_sb}!")
                            st.rerun()
                        else:
                            st.info("El ticket ya tiene asignado ese método.")

                if st.button("🖨️ Imprimir Ticket (150mm)", use_container_width=True, key="btn_print_tk_cajero"):
                    mostrar_dialogo_ticket(ultimo_tk, st.session_state.get('config_negocio', {}))
                if st.button("🔄 Listo / Siguiente Venta", use_container_width=True, key="btn_sig_tk_sb"):
                    st.session_state.ultimo_ticket = None
                    st.rerun()
        else:
            st.caption("Al cobrar una venta, aquí aparecerá el ticket para consulta rápida.")

    # =============================================================
    # 2. ÁREA CENTRAL (CENTRO) — TERMINAL PUNTO DE VENTA (POS)
    # =============================================================
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown("## 🖥️ Terminal Punto de Venta & Caja")
        st.caption(f"👋 **Cajero:** {mi_nombre} (`@{mi_usuario}`) | 📅 **Fecha del Sistema:** `{hoy_str}`")
    with col_t2:
        st.markdown("""
        <div style="text-align: right; padding-top: 8px;">
            <span style="background: #22c55e; color: #064e3b; padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;">● Caja Operativa</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Banner destacado cuando se acaba de cobrar un ticket con opción de cambio inmediato de método de pago
    if ultimo_tk:
        with st.container(border=True):
            col_nt1, col_nt2, col_nt3 = st.columns([2.5, 1.5, 1])
            with col_nt1:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 2.2rem;">🧾</span>
                    <div>
                        <strong style="font-size: 1.05rem; color: #0f172a;">Ticket Cobrado: <code>{ultimo_tk.get('folio')}</code></strong><br>
                        <span style="font-size: 0.9rem; color: #475569;">Total: <b>${ultimo_tk.get('monto', 0.0):,.2f}</b> | Método Registrado: <b style="color: #0284c7; background: #e0f2fe; padding: 2px 8px; border-radius: 4px;">{ultimo_tk.get('metodo_pago')}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_nt2:
                with st.popover("💳 Cambiar Método de Pago", use_container_width=True):
                    st.markdown("##### ✏️ Rectificar Método de Pago")
                    st.caption("¿El cliente decidió cambiar su forma de pago? Actualízala aquí:")
                    lista_mp = ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"]
                    mp_act = ultimo_tk.get('metodo_pago', '💵 Efectivo')
                    idx_mp = lista_mp.index(mp_act) if mp_act in lista_mp else 0
                    nuevo_mp_center = st.selectbox("Forma de pago correcta:", lista_mp, index=idx_mp, key=f"cnt_sel_mp_{ultimo_tk.get('folio')}")
                    if st.button("💾 Guardar y Actualizar Ticket", type="primary", use_container_width=True, key=f"btn_cnt_upd_mp_{ultimo_tk.get('folio')}"):
                        if nuevo_mp_center != mp_act:
                            actualizar_metodo_pago_ticket(ultimo_tk.get('folio'), nuevo_mp_center)
                            st.session_state.ultimo_ticket['metodo_pago'] = nuevo_mp_center
                            st.success(f"✅ ¡Ticket {ultimo_tk.get('folio')} actualizado a {nuevo_mp_center}!")
                            st.rerun()
                        else:
                            st.info("El ticket ya tiene ese método de pago.")
            with col_nt3:
                if st.button("🖨️ Imprimir Ticket", use_container_width=True, key="btn_center_print_pos_tk"):
                    mostrar_dialogo_ticket(ultimo_tk, st.session_state.get('config_negocio', {}))


    # Inicializar estado de compras y widget versioning
    if "carrito_compras" not in st.session_state:
        st.session_state.carrito_compras = []
    if "prod_sel_prev" not in st.session_state:
        st.session_state.prod_sel_prev = None
    if "cant_key_ver" not in st.session_state:
        st.session_state.cant_key_ver = 0

    # Cargar inventario de productos
    df_inv = None
    if os.path.exists(archivo_productos):
        df_inv = asegurar_columnas_productos(pd.read_csv(archivo_productos, dtype={"codigo_barras": str}), tc_usd=float(st.session_state.get("tc_usd", 19.85)), tc_eur=float(st.session_state.get("tc_eur", 21.40)))
        if 'inventario' not in df_inv.columns:
            df_inv['inventario'] = 50

    if df_inv is None or df_inv.empty:
        st.warning("⚠️ No hay productos disponibles en el inventario. Comunícate con el Gerente para cargar productos.")
        return

    # Dos columnas del Punto de Venta en el Centro
    col_pos1, col_pos2 = st.columns([1.1, 1.3], gap="large")

    with col_pos1:
        with st.container(border=True):
            st.markdown("#### 1️⃣ Seleccionar Producto & Cobro")
            
            lista_prods = df_inv['producto'].tolist()
            producto_sel = st.selectbox("📦 Selecciona un producto del catálogo:", lista_prods, key="sel_prod_empleado_pos")

            # Reset key si cambió el producto seleccionado
            if st.session_state.prod_sel_prev != producto_sel:
                st.session_state.prod_sel_prev = producto_sel
                st.session_state.cant_key_ver += 1
                st.rerun()

            # Cantidad actual en carrito de este producto
            cant_actual_en_carr = 0
            for it in st.session_state.carrito_compras:
                if it['producto'] == producto_sel:
                    cant_actual_en_carr = it['cantidad']
                    break

            p_idx = df_inv.index[df_inv['producto'] == producto_sel].tolist()[0]
            precio_unitario = float(df_inv.at[p_idx, 'precio_venta'])
            inv_disp = int(df_inv.at[p_idx, 'inventario'])

            # Indicadores de stock y precio
            color_stock = '#16a34a' if inv_disp > 5 else ('#ea580c' if inv_disp > 0 else '#dc2626')
            cat_emp_p = str(df_inv.at[p_idx, 'categoria']) if 'categoria' in df_inv.columns else ''
            foto_emp_p = str(df_inv.at[p_idx, 'foto_url']) if ('foto_url' in df_inv.columns and pd.notna(df_inv.at[p_idx, 'foto_url']) and str(df_inv.at[p_idx, 'foto_url']).strip() != '') else generar_svg_producto(producto_sel, cat_emp_p)
            cod_emp_p = str(df_inv.at[p_idx, 'codigo_barras']) if ('codigo_barras' in df_inv.columns and pd.notna(df_inv.at[p_idx, 'codigo_barras'])) else f"75010553{1000 + p_idx:04d}"
            rop_emp_p = int(df_inv.at[p_idx, 'punto_reorden']) if ('punto_reorden' in df_inv.columns and pd.notna(df_inv.at[p_idx, 'punto_reorden'])) else 15
            c_eimg, c_ecard = st.columns([1, 2.5])
            with c_eimg:
                st.image(foto_emp_p, use_container_width=True)
            with c_ecard:
                st.caption(f"🏷️ Categoría: **{cat_emp_p or 'General'}** | ║▌║ Código: `{cod_emp_p}` | Punto Reorden: **{rop_emp_p} u.**")
                if inv_disp <= rop_emp_p:
                    st.warning(f"⚠️ Producto en Punto de Reorden ({inv_disp} <= {rop_emp_p} unidades). Avisar a Almacén.")
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px; margin: 8px 0 14px 0; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; font-weight: 600;">PRECIO AL PÚBLICO</span>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #0284c7;">${precio_unitario:,.2f}</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.75rem; color: #64748b; font-weight: 600;">STOCK DISPONIBLE</span>
                    <div style="font-size: 1.25rem; font-weight: 700; color: {color_stock};">{inv_disp} unidades</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            widget_cant_key = f"cant_empleado_ver_{st.session_state.cant_key_ver}"
            cantidad_input = st.number_input(
                "🔢 Cantidad a llevar:",
                min_value=0,
                max_value=max(inv_disp, 0),
                value=cant_actual_en_carr,
                step=1,
                key=widget_cant_key
            )

            # Sincronización automática de cantidad con el carrito
            if cantidad_input == 0:
                st.session_state.carrito_compras = [
                    it for it in st.session_state.carrito_compras if it['producto'] != producto_sel
                ]
            else:
                encontrado = False
                for it in st.session_state.carrito_compras:
                    if it['producto'] == producto_sel:
                        it['cantidad'] = cantidad_input
                        it['subtotal'] = cantidad_input * precio_unitario
                        it['producto_idx'] = p_idx
                        encontrado = True
                        break
                if not encontrado:
                    st.session_state.carrito_compras.append({
                        "producto": producto_sel,
                        "producto_idx": p_idx,
                        "cantidad": cantidad_input,
                        "precio_unitario": precio_unitario,
                        "subtotal": cantidad_input * precio_unitario
                    })

            st.markdown("---")
            st.markdown("##### 💳 Parámetros de Cobro & Fecha")
            metodo_pago_sel = st.selectbox(
                "💳 Método de cobro:",
                ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"],
                key="metodo_pago_empleado_pos"
            )

            # Lógica de fecha y huella biométrica
            auth_info = st.session_state.get('auth_gerente_cambio_fecha')
            es_fecha_modificada = False
            autorizador_gerente = ""
            motivo_justif = ""
            fecha_a_usar = hoy_fecha

            if auth_info and auth_info.get('autorizado'):
                fecha_a_usar = auth_info.get('fecha_autorizada', hoy_fecha)
                es_fecha_modificada = True
                autorizador_gerente = auth_info.get('gerente_usuario', '')
                motivo_justif = auth_info.get('motivo', '')

                st.success(f"🔓 **Fecha Autorizada por Huella:**\n\n📅 `{fecha_a_usar}` | 👑 Autorizó: **{auth_info.get('gerente_nombre')}**\n📝 Motivo: *{motivo_justif}*")
                col_fc1, col_fc2 = st.columns([2, 1])
                with col_fc1:
                    fecha_input = st.date_input("Fecha Especial Autorizada:", value=fecha_a_usar, max_value=hoy_fecha, key="fecha_especial_pos")
                with col_fc2:
                    st.write("")
                    if st.button("❌ Cancelar", help="Regresar a la fecha del sistema", key="btn_cancelar_auth_pos"):
                        st.session_state.auth_gerente_cambio_fecha = None
                        st.rerun()
            else:
                col_fe1, col_fe2 = st.columns([1.6, 1.4])
                with col_fe1:
                    fecha_input = st.date_input(
                        "📅 Fecha (Reloj del Sistema):",
                        value=hoy_fecha,
                        disabled=True,
                        help="🔒 Deshabilitado para empleados. Solo se permite registrar ventas en tiempo real."
                    )
                with col_fe2:
                    st.write("")
                    if st.button("👆 Huella Gerente", use_container_width=True, help="Solicitar autorización de cambio de fecha mediante huella del gerente", key="btn_huella_pos"):
                        modal_simulador_huella(hoy_fecha)

    with col_pos2:
        with st.container(border=True):
            st.markdown("#### 2️⃣ Cuenta Actual del Cliente")
            
            if len(st.session_state.carrito_compras) > 0:
                total_cuenta = 0.0
                conceptos_lista = []
                indices_a_borrar = []

                st.caption(f"Artículos agregados a la cuenta: **{len(st.session_state.carrito_compras)}**")
                
                # Lista de productos en cuenta
                for idx_item, item in enumerate(st.session_state.carrito_compras):
                    col_ci1, col_ci2 = st.columns([4, 1])
                    with col_ci1:
                        st.markdown(f"**{item['cantidad']}x** {item['producto']} — `${item['subtotal']:,.2f}` <span style='color:#64748b; font-size:0.8rem;'>(${item['precio_unitario']:,.2f} c/u)</span>", unsafe_allow_html=True)
                    with col_ci2:
                        if st.button("❌", key=f"del_item_pos_{idx_item}_{item['producto']}", help=f"Eliminar {item['producto']} de la cuenta"):
                            indices_a_borrar.append(idx_item)
                    total_cuenta += item['subtotal']
                    conceptos_lista.append(f"{item['cantidad']}x {item['producto']}")

                if indices_a_borrar:
                    for idx_b in sorted(indices_a_borrar, reverse=True):
                        st.session_state.carrito_compras.pop(idx_b)
                    st.session_state.cant_key_ver += 1
                    st.rerun()

                # Card de Total destacado
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 18px 20px; border-radius: 10px; margin: 18px 0; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <span style="font-size: 0.85rem; color: #94a3b8; letter-spacing: 1px; font-weight: 700; text-transform: uppercase;">Total a Cobrar</span>
                    <div style="font-size: 2.7rem; font-weight: 900; color: #38bdf8; margin: 4px 0;">${total_cuenta:,.2f}</div>
                    <span style="font-size: 0.85rem; color: #cbd5e1;">Método seleccionado: <b>{metodo_pago_sel}</b></span>
                </div>
                """, unsafe_allow_html=True)

                info_verif_emp = render_verificador_pago_simulado(metodo_pago_sel, total_cuenta, key_prefix="emp_pos")
                col_btn_cob1, col_btn_cob2 = st.columns([2, 1])
                with col_btn_cob1:
                    btn_cobrar_pos = st.button("💾 Cobrar y Generar Ticket", type="primary", use_container_width=True, key="btn_cobrar_pos_empleado")
                with col_btn_cob2:
                    if st.button("🗑️ Vaciar Cuenta", use_container_width=True, key="btn_vaciar_pos"):
                        st.session_state.carrito_compras = []
                        st.session_state.prod_sel_prev = None
                        st.session_state.cant_key_ver += 1
                        st.rerun()

                if btn_cobrar_pos and not info_verif_emp.get("pagado_verificado", True):
                    st.error("⚠️ No se puede emitir el ticket hasta verificar que el pago del cliente esté completo / aprobado.")
                elif btn_cobrar_pos:
                    fecha_str = fecha_input.strftime("%Y-%m-%d")
                    hora_str = datetime.now().strftime("%H:%M")
                    
                    fecha_num = date.today().strftime("%Y%m%d")
                    cant_ventas = len(df_db[df_db['tipo'] == 'venta']) + 1 if not df_db.empty else 1
                    folio_str = f"TK-{fecha_num}-{cant_ventas:04d}"

                    detalle_json = json.dumps([
                        {"producto": it['producto'], "cantidad": it['cantidad'], "precio_unitario": it['precio_unitario'], "subtotal": it['subtotal']}
                        for it in st.session_state.carrito_compras
                    ], ensure_ascii=False)

                    concepto_final = "Venta: " + ", ".join(conceptos_lista)

                    nuevo_reg = {
                        "fecha": fecha_str,
                        "hora": hora_str,
                        "tipo": "venta",
                        "monto": float(total_cuenta),
                        "concepto": concepto_final,
                        "es_costo_directo": False,
                        "metodo_pago": metodo_pago_sel,
                        "folio": folio_str,
                        "productos_detalle": detalle_json,
                        "usuario": mi_usuario,
                        "autorizado_por": autorizador_gerente if es_fecha_modificada else "",
                        "motivo_autorizacion": motivo_justif if es_fecha_modificada else ""
                    }

                    df_actualizado = pd.concat([df_db, pd.DataFrame([nuevo_reg])], ignore_index=True)
                    df_actualizado.to_csv("hermes_financial_db.csv", index=False)

                    # Descontar inventario
                    for item in st.session_state.carrito_compras:
                        p_item_idx = item['producto_idx']
                        cant = item['cantidad']
                        df_inv.at[p_item_idx, 'inventario'] = max(0, int(df_inv.at[p_item_idx, 'inventario']) - cant)
                    cols_save_emp = [c for c in ['producto', 'categoria', 'codigo_barras', 'moneda_origen', 'costo_moneda_origen', 'costo_compra', 'precio_venta', 'inventario', 'punto_reorden', 'unidades_vendidas_hoy', 'ruta_imagen'] if c in df_inv.columns]
                    df_inv[cols_save_emp].to_csv(archivo_productos, index=False)

                    # Guardar último ticket
                    st.session_state.ultimo_ticket = {
                        "folio": folio_str,
                        "fecha": fecha_str,
                        "hora": hora_str,
                        "monto": total_cuenta,
                        "metodo_pago": metodo_pago_sel,
                        "concepto": concepto_final,
                        "items": list(st.session_state.carrito_compras),
                        "verificacion_pago": info_verif_emp
                    }

                    if es_fecha_modificada:
                        st.session_state.auth_gerente_cambio_fecha = None

                    st.session_state.carrito_compras = []
                    st.session_state.prod_sel_prev = None
                    st.session_state.cant_key_ver += 1

                    st.success(f"✅ ¡Venta registrada y cobrada exitosamente! Folio: {folio_str}")
                    st.rerun()

            else:
                st.markdown("""
                <div style="text-align: center; padding: 45px 20px; color: #64748b; background: #f8fafc; border-radius: 8px; border: 2px dashed #cbd5e1; margin: 15px 0;">
                    <div style="font-size: 3.2rem; margin-bottom: 8px;">🛒</div>
                    <strong style="font-size: 1.15rem; color: #334155;">La cuenta del cliente está vacía</strong><br>
                    <span style="font-size: 0.9rem;">Selecciona un producto a la izquierda y define la cantidad para agregar artículos al ticket.</span>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # 3. CONSULTA RÁPIDA DE INVENTARIO Y PRECIOS (PARTE INFERIOR)
    # =============================================================
    st.markdown("---")
    st.markdown("### 📦 Consulta Rápida de Precios y Existencias")
    st.caption("Usa el buscador para verificar rápidamente disponibilidad o precios de venta al cliente sin salir de la caja.")

    busq_prod = st.text_input("🔍 Buscar Producto por Nombre o Categoría:", placeholder="Escribe el nombre del producto...", key="busq_prod_pos_cajero")
    df_mostrar_p = df_inv.copy()
    if busq_prod:
        df_mostrar_p = df_mostrar_p[
            df_mostrar_p['producto'].astype(str).str.contains(busq_prod, case=False, na=False) |
            df_mostrar_p['categoria'].astype(str).str.contains(busq_prod, case=False, na=False)
        ]

    df_mostrar_cajero = df_mostrar_p[['foto_url', 'producto', 'categoria', 'codigo_barras', 'precio_venta', 'inventario']].copy()
    df_mostrar_cajero.columns = ['📸 Foto', 'Producto', 'Categoría', '║▌║ Código', 'Precio al Público ($)', 'Stock Disponible']
    st.dataframe(df_mostrar_cajero, use_container_width=True, column_config={"📸 Foto": st.column_config.ImageColumn("📸 Foto")})


