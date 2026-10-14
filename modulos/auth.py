import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime, date

USUARIOS_FILE = "usuarios_db.csv"

def hash_password(password: str) -> str:
    """Retorna el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def cargar_usuarios() -> pd.DataFrame:
    """Carga la base de datos de usuarios o inicializa una por defecto."""
    if not os.path.exists(USUARIOS_FILE):
        usuarios_default = [
            {
                "username": "gerente",
                "nombre": "Gerente General",
                "password_hash": hash_password("admin123"),
                "rol": "gerente",
                "pin_biometrico": "1234",
                "activo": True,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            {
                "username": "empleado1",
                "nombre": "Juan Pérez (Cajero Turno A)",
                "password_hash": hash_password("1234"),
                "rol": "empleado",
                "pin_biometrico": "0000",
                "activo": True,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            {
                "username": "empleado2",
                "nombre": "María López (Cajera Turno B)",
                "password_hash": hash_password("1234"),
                "rol": "empleado",
                "pin_biometrico": "0000",
                "activo": True,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        ]
        df = pd.DataFrame(usuarios_default)
        df.to_csv(USUARIOS_FILE, index=False)
        return df

    df = pd.read_csv(USUARIOS_FILE)
    # Validar columnas
    columnas_requeridas = ["username", "nombre", "password_hash", "rol", "pin_biometrico", "activo", "fecha_registro"]
    modificado = False
    for col in columnas_requeridas:
        if col not in df.columns:
            if col == "activo":
                df[col] = True
            elif col == "pin_biometrico":
                df[col] = "1234"
            elif col == "rol":
                df[col] = "empleado"
            else:
                df[col] = ""
            modificado = True
    if modificado:
        df.to_csv(USUARIOS_FILE, index=False)
    return df

def guardar_usuarios(df: pd.DataFrame):
    """Guarda el DataFrame de usuarios en disco."""
    df.to_csv(USUARIOS_FILE, index=False)

def autenticar_usuario(username: str, password_plana: str):
    """Verifica si las credenciales son válidas y si el usuario está activo."""
    df = cargar_usuarios()
    u_row = df[(df['username'].str.lower() == username.strip().lower()) & (df['activo'] == True)]
    if not u_row.empty:
        pw_hash = hash_password(password_plana)
        if u_row.iloc[0]['password_hash'] == pw_hash:
            return u_row.iloc[0].to_dict()
    return None

def validar_credencial_gerente(gerente_username: str, credencial: str) -> bool:
    """Valida la contraseña o PIN biométrico de un gerente para autorizaciones."""
    df = cargar_usuarios()
    g_row = df[(df['username'].str.lower() == gerente_username.strip().lower()) & 
               (df['rol'] == 'gerente') & 
               (df['activo'] == True)]
    if not g_row.empty:
        pw_hash = hash_password(credencial)
        pin_almacenado = str(g_row.iloc[0]['pin_biometrico']).strip()
        if g_row.iloc[0]['password_hash'] == pw_hash or credencial.strip() == pin_almacenado:
            return True
    return False

def render_pantalla_login():
    """Pantalla interactiva y estética de inicio de sesión."""
    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px 10px 15px;">
            <div style="font-size: 3.5rem; margin-bottom: 5px;">🛡️</div>
            <h2 style="margin: 0; color: #1e293b; font-weight: 800;">Control de Acceso & Punto de Venta</h2>
            <p style="color: #64748b; font-size: 0.95rem;">Ingresa tus credenciales para acceder a tu estación de trabajo</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 🔐 Iniciar Sesión")
            with st.form("form_login", clear_on_submit=False):
                usuario_input = st.text_input("👤 Usuario:", placeholder="ej. empleado1 o gerente")
                password_input = st.text_input("🔑 Contraseña:", type="password", placeholder="••••••••")
                btn_ingresar = st.form_submit_button("🚀 Entrar al Sistema", use_container_width=True, type="primary")

                if btn_ingresar:
                    if not usuario_input or not password_input:
                        st.error("⚠️ Por favor ingresa tanto usuario como contraseña.")
                    else:
                        usuario_validado = autenticar_usuario(usuario_input, password_input)
                        if usuario_validado:
                            st.session_state.usuario_actual = usuario_validado
                            st.session_state.auth_gerente_cambio_fecha = None
                            st.success(f"¡Bienvenido/a {usuario_validado['nombre']}!")
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos, o cuenta inactiva.")

        st.caption("""
        💡 **Cuentas de demostración preconfiguradas:**
        - **👑 Gerente (Acceso Total):** Usuario: `gerente` | Contraseña: `admin123`
        - **👤 Empleado (Solo Ventas/Caja):** Usuario: `empleado1` | Contraseña: `1234`
        """)

def render_user_badge_sidebar():
    """Muestra el badge del usuario activo y botón de Cerrar Sesión en la barra lateral."""
    user = st.session_state.get('usuario_actual')
    if not user:
        return

    es_gerente = user.get('rol') == 'gerente'
    icono_rol = "👑" if es_gerente else "👤"
    color_fondo = "#eff6ff" if es_gerente else "#f0fdf4"
    color_borde = "#3b82f6" if es_gerente else "#22c55e"
    color_texto = "#1d4ed8" if es_gerente else "#15803d"
    rol_label = "GERENTE / ADMINISTRADOR" if es_gerente else "EMPLEADO / CAJERO"

    st.sidebar.markdown(f"""
    <div style="background-color: {color_fondo}; border-left: 4px solid {color_borde}; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.72rem; font-weight: bold; color: {color_texto}; letter-spacing: 0.5px;">
                {icono_rol} {rol_label}
            </span>
            <span style="font-size: 0.7rem; color: #64748b; background: white; padding: 2px 6px; border-radius: 10px; border: 1px solid #e2e8f0;">
                {'🔒 Total' if es_gerente else '🛡️ Caja'}
            </span>
        </div>
        <div style="font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-top: 4px;">
            {user.get('nombre', user.get('username'))}
        </div>
        <div style="font-size: 0.8rem; color: #64748b;">
            Usuario: <code>@{user.get('username')}</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout_user_sidebar"):
        st.session_state.usuario_actual = None
        st.session_state.auth_gerente_cambio_fecha = None
        st.session_state.carrito_compras = []
        st.session_state.prod_sel_prev = None
        st.rerun()

