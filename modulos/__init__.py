# Package init for modules
from .inversion_inicial import render_inversion_inicial
from .cotizaciones_presupuestos import render_cotizaciones_presupuestos
from .diagrama_flujo import render_diagrama_flujo
from .balance_energetico import render_balance_energetico

# Módulos de Autenticación, Biometría y Personal
from .auth import (
    cargar_usuarios,
    guardar_usuarios,
    autenticar_usuario,
    render_pantalla_login,
    render_user_badge_sidebar
)
from .biometrico import modal_simulador_huella
from .personal import render_administracion_personal, render_dashboard_empleado
