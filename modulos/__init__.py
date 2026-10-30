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
from .personal import (
    render_administracion_personal,
    render_dashboard_empleado,
    actualizar_metodo_pago_ticket
)

# Módulo de Impresión de Tickets
from .ticket_printer import (
    render_ticket_component,
    mostrar_dialogo_ticket,
    generar_html_ticket
)


# Módulo de Sistema Integral (Reorden, Fotos, Divisas, Geolocalización, CFDI y Razones Financieras)
from .sistema_integral import (
    generar_svg_producto,
    asegurar_columnas_productos,
    render_analisis_inventarios_y_galeria,
    render_sugerencias_geolocalizacion_y_mercado,
    render_modulo_facturacion_cfdi,
    render_areas_y_razones_financieras
)
