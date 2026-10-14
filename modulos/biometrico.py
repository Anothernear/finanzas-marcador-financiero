import streamlit as st
import pandas as pd
import time
from datetime import datetime, date
from modulos.auth import cargar_usuarios, validar_credencial_gerente

def render_animacion_huella(estado="esperando"):
    """Renderiza el componente visual estilizado del sensor biométrico de huella dactilar."""
    if estado == "esperando":
        color_sensor = "#3b82f6"
        color_fondo = "#eff6ff"
        texto_estado = "Coloca el pulgar sobre el sensor óptico"
        animacion = "border: 2px dashed #3b82f6;"
    elif estado == "escaneando":
        color_sensor = "#f59e0b"
        color_fondo = "#fffbeb"
        texto_estado = "Analizando minucias y patrones biométricos..."
        animacion = "border: 2px solid #f59e0b; box-shadow: 0 0 15px rgba(245, 158, 11, 0.5);"
    else:  # exito
        color_sensor = "#10b981"
        color_fondo = "#ecfdf5"
        texto_estado = "¡Huella dactilar reconocida exitosamente!"
        animacion = "border: 2px solid #10b981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);"

    html_svg = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 15px; margin-bottom: 10px;">
        <div style="width: 110px; height: 110px; border-radius: 50%; background: {color_fondo}; {animacion} display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="{color_sensor}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a10 10 0 0 0-10 10c0 4.1 2.5 7.6 6 9.1"></path>
                <path d="M12 6a6 6 0 0 0-6 6c0 2.2 1.2 4.1 3 5.2"></path>
                <path d="M12 10a2 2 0 0 0-2 2c0 .9.6 1.7 1.4 1.9"></path>
                <path d="M14 13.1c.6-.5 1-1.2 1-2.1a3 3 0 0 0-3-3"></path>
                <path d="M17 16.5c1.2-1.2 2-2.8 2-4.5a7 7 0 0 0-7-7"></path>
                <path d="M20 18.5c1.3-1.8 2-4 2-6.5a10 10 0 0 0-3.5-7.5"></path>
                <path d="M12 18v4"></path>
                <path d="M8 22h8"></path>
            </svg>
        </div>
        <span style="font-size: 0.85rem; font-weight: 600; color: {color_sensor}; margin-top: 8px;">
            {texto_estado}
        </span>
    </div>
    """
    st.markdown(html_svg, unsafe_allow_html=True)

@st.dialog("👆 Lector Biométrico — Autorización de Gerencia")
def modal_simulador_huella(fecha_actual_sistema):
    """
    Diálogo modal interactivo para simular el escaneo de huella dactilar del Gerente
    y registrar la justificación obligatoria del cambio de fecha.
    """
    st.caption("🔒 **Operación Restringida:** Los empleados solo pueden registrar ventas con la fecha actual del sistema. Para asignar una fecha distinta, se requiere la validación biométrica del Gerente.")

    render_animacion_huella(estado="esperando")

    df_usuarios = cargar_usuarios()
    df_gerentes = df_usuarios[(df_usuarios['rol'] == 'gerente') & (df_usuarios['activo'] == True)]

    if df_gerentes.empty:
        st.error("⚠️ No hay gerentes registrados o activos en el sistema para autorizar.")
        return

    lista_gerentes = df_gerentes['username'].tolist()
    nombres_dict = dict(zip(df_gerentes['username'], df_gerentes['nombre']))

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        gerente_sel = st.selectbox(
            "👑 Gerente Autorizador:",
            lista_gerentes,
            format_func=lambda u: f"{nombres_dict.get(u, u)} (@{u})"
        )
    with col_g2:
        nueva_fecha_deseada = st.date_input(
            "📅 Fecha Especial a Autorizar:",
            value=date.today(),
            max_value=date.today(),
            help="Selecciona la fecha retroactiva o especial que se habilitará."
        )

    credencial_input = st.text_input(
        "🔑 Clave de Confirmación o PIN Biométrico del Gerente:",
        type="password",
        placeholder="PIN o contraseña del gerente",
        help="Clave por defecto: admin123 o PIN 1234"
    )

    motivo_input = st.text_area(
        "📝 Justificación / Motivo del Cambio de Fecha (Obligatorio):",
        placeholder="Ej: Falla en suministro eléctrico ayer a las 19:00 hrs. Captura pendiente de ticket físico.",
        help="Este motivo quedará asentado en la bitácora de auditoría fiscal y operativa."
    )

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        btn_escanear = st.button("👆 Escanear Huella y Autorizar", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

    if btn_escanear:
        if not credencial_input:
            st.error("⚠️ Ingresa el PIN o contraseña del gerente para validar la identidad de la huella.")
        elif not motivo_input.strip() or len(motivo_input.strip()) < 8:
            st.error("⚠️ Debes proporcionar un motivo detallado (mínimo 8 caracteres) para auditoría.")
        else:
            es_valido = validar_credencial_gerente(gerente_sel, credencial_input)
            if es_valido:
                # Simulación de lectura biométrica exitosa
                codigo_bio = f"BIO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                st.session_state.auth_gerente_cambio_fecha = {
                    "autorizado": True,
                    "gerente_usuario": gerente_sel,
                    "gerente_nombre": nombres_dict.get(gerente_sel, gerente_sel),
                    "motivo": motivo_input.strip(),
                    "fecha_autorizada": nueva_fecha_deseada,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "codigo_biometrico": codigo_bio
                }
                st.success(f"✅ **¡Huella Biometríca Validada con Éxito!**\n\nAutorizado por: **{nombres_dict.get(gerente_sel)}** | Código: `{codigo_bio}`")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("❌ Credencial biométrica o PIN inválido. Huella dactilar no reconocida.")
