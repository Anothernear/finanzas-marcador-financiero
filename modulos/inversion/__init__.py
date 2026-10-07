# Sub-paquete: modulos/inversion/
# Gestión modular de inversión inicial, fichas técnicas y presupuestos comparativos.

from .render_inversion_inicial import render_inversion_inicial
from .render_cotizaciones_presupuestos import render_cotizaciones_presupuestos

__all__ = [
    "render_inversion_inicial",
    "render_cotizaciones_presupuestos",
]
