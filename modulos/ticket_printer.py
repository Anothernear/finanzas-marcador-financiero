"""
Módulo de Gestión, Impresión y Renderizado de Tickets Térmicos (150mm / Formato TPV).
Genera código de barras (Code128) para identificación del ticket
y código QR para facturación electrónica rápida (CFDI / SAT).
"""
import io
import base64
import html
import qrcode
import barcode
from barcode.writer import SVGWriter
import streamlit as st
import streamlit.components.v1 as components

def generar_qr_base64(url_facturacion: str) -> str:
    """Genera una imagen PNG en base64 del código QR para facturación."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=1
        )
        qr.add_data(url_facturacion)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return ""

def generar_barcode_svg(folio: str) -> str:
    """Genera un SVG limpio de código de barras Code128 para identificar el ticket."""
    try:
        clean_folio = str(folio).replace(" ", "").strip()
        if not clean_folio:
            clean_folio = "TK-00000000-0000"
        CODE128 = barcode.get_barcode_class('code128')
        bc = CODE128(clean_folio, writer=SVGWriter())
        buf = io.BytesIO()
        bc.write(buf, options={
            'write_text': True,
            'module_height': 8.0,
            'module_width': 0.22,
            'font_size': 9,
            'quiet_zone': 1.5
        })
        svg_str = buf.getvalue().decode('utf-8')
        if svg_str.startswith('<?xml'):
            svg_str = svg_str.split('?>', 1)[-1].strip()
        return svg_str
    except Exception:
        return ""

def generar_html_ticket(tk: dict, config: dict) -> str:
    """
    Construye el documento HTML listo para impresión térmica (150mm / 58-80mm responsive).
    Incluye estilos de corte térmico, botón de impresión y vista previa fiel.
    """
    # Variables de negocio configurables
    nombre_empresa = html.escape(str(config.get("nombre", "Mi Empresa")))
    rfc = html.escape(str(config.get("rfc", "XAXX010101000")))
    direccion = html.escape(str(config.get("direccion", "Av. Principal #123, Col. Centro, CP 56230, Texcoco, Edo. Méx.")))
    icono = config.get("icono", "🥖")
    tasa_iva = float(config.get("tasa_iva", 16.0))
    incluye_iva = bool(config.get("incluye_iva", True))
    notas = html.escape(str(config.get("notas_ticket", "¡Gracias por su compra! Conserve este comprobante para cualquier aclaración o facturación.")))
    url_base_fac = str(config.get("url_facturacion", "https://facturacion.empresa.mx/portal")).strip()
    telefono = html.escape(str(config.get("telefono", "")))

    # Datos del ticket
    folio = str(tk.get("folio", "TK-00000000-0000"))
    fecha = str(tk.get("fecha", ""))
    hora = str(tk.get("hora", ""))
    metodo_pago = str(tk.get("metodo_pago", "Efectivo"))
    monto_total = float(tk.get("monto", 0.0))
    items = tk.get("items", [])
    concepto_general = str(tk.get("concepto", ""))

    # URL QR para facturación
    url_qr_factura = f"{url_base_fac}?folio={folio}&monto={monto_total:.2f}&rfc={rfc}&fecha={fecha}"
    qr_b64 = generar_qr_base64(url_qr_factura)
    barcode_svg = generar_barcode_svg(folio)

    # Desglose de IVA
    if incluye_iva and tasa_iva > 0:
        base_subtotal = monto_total / (1.0 + (tasa_iva / 100.0))
        monto_iva = monto_total - base_subtotal
    else:
        base_subtotal = monto_total
        monto_iva = 0.0

    # Construcción de filas de artículos
    filas_items_html = ""
    if items and len(items) > 0:
        for it in items:
            p_nom = html.escape(str(it.get("producto", "Articulo")))
            p_cant = it.get("cantidad", 1)
            p_unit = float(it.get("precio_unitario", 0.0))
            p_sub = float(it.get("subtotal", p_cant * p_unit))
            filas_items_html += f"""
            <tr>
                <td style="text-align: left; padding: 3px 0;">{p_nom}<br><small style="color: #666;">{p_cant} x ${p_unit:,.2f}</small></td>
                <td style="text-align: right; padding: 3px 0; vertical-align: bottom;"><strong>${p_sub:,.2f}</strong></td>
            </tr>
            """
    else:
        filas_items_html = f"""
        <tr>
            <td style="text-align: left; padding: 4px 0;">{html.escape(concepto_general if concepto_general else 'Venta General')}</td>
            <td style="text-align: right; padding: 4px 0;"><strong>${monto_total:,.2f}</strong></td>
        </tr>
        """

    contacto_line = f"<div style='font-size: 11px; margin-top: 2px;'>Tel: {telefono}</div>" if telefono else ""

    html_completo = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Ticket {folio}</title>
<style>
    @page {{
        size: 150mm auto;
        margin: 0;
    }}
    * {{
        box-sizing: border-box;
    }}
    body {{
        font-family: 'Courier New', Courier, monospace, monospace;
        font-size: 12px;
        color: #000;
        background: transparent;
        margin: 0;
        padding: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .ticket-container {{
        width: 100%;
        max-width: 480px; /* ~150mm render */
        background: #fff;
        padding: 16px;
        border: 1px dashed #bbb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-radius: 6px;
    }}
    .no-print {{
        margin-bottom: 15px;
        width: 100%;
        max-width: 480px;
        display: flex;
        gap: 10px;
    }}
    .btn-print {{
        flex: 1;
        background: #0284c7;
        color: white;
        border: none;
        padding: 10px 18px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 2px 5px rgba(2, 132, 199, 0.3);
    }}
    .btn-print:hover {{
        background: #0369a1;
    }}
    .ticket-header {{
        text-align: center;
        margin-bottom: 8px;
        border-bottom: 1px dashed #444;
        padding-bottom: 8px;
    }}
    .business-icon {{
        font-size: 32px;
        line-height: 1.2;
    }}
    .business-name {{
        font-size: 18px;
        font-weight: 900;
        text-transform: uppercase;
        margin: 3px 0;
    }}
    .business-info {{
        font-size: 11px;
        color: #333;
        line-height: 1.35;
    }}
    .ticket-meta {{
        font-size: 11px;
        margin: 8px 0;
        border-bottom: 1px dashed #444;
        padding-bottom: 6px;
    }}
    .ticket-meta div {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 2px;
    }}
    table.items-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        margin-bottom: 8px;
    }}
    table.items-table th {{
        border-bottom: 1px solid #000;
        padding-bottom: 4px;
        text-transform: uppercase;
        font-size: 11px;
    }}
    .totales-box {{
        border-top: 1px dashed #444;
        padding-top: 6px;
        margin-bottom: 10px;
    }}
    .totales-row {{
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 3px;
    }}
    .totales-row.gran-total {{
        font-size: 16px;
        font-weight: 900;
        border-top: 1px solid #000;
        border-bottom: 1px solid #000;
        padding: 4px 0;
        margin-top: 4px;
    }}
    .notes-box {{
        font-size: 10.5px;
        text-align: center;
        margin: 10px 0;
        padding: 6px;
        background: #f8fafc;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        line-height: 1.3;
    }}
    .codes-section {{
        text-align: center;
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px dashed #444;
    }}
    .qr-container {{
        margin: 8px auto;
        display: inline-block;
        padding: 4px;
        background: #fff;
    }}
    .qr-container img {{
        width: 120px;
        height: 120px;
        display: block;
    }}
    .qr-caption {{
        font-size: 10px;
        font-weight: bold;
        color: #1e293b;
        margin-top: 2px;
    }}
    .barcode-container {{
        margin: 10px auto 4px auto;
        max-width: 90%;
        overflow: hidden;
    }}
    .barcode-container svg {{
        width: 100%;
        height: auto;
        max-height: 55px;
    }}
    .barcode-caption {{
        font-size: 10px;
        color: #475569;
        margin-top: 1px;
    }}
    .footer-cut {{
        text-align: center;
        font-size: 11px;
        margin-top: 12px;
        color: #888;
        letter-spacing: 2px;
    }}
    @media print {{
        body {{
            background: #fff;
            padding: 0;
        }}
        .no-print {{
            display: none !important;
        }}
        .ticket-container {{
            border: none;
            box-shadow: none;
            padding: 4px;
            max-width: 100%;
            width: 100%;
        }}
    }}
</style>
</head>
<body>

<div class="no-print">
    <button class="btn-print" onclick="window.print();">
        🖨️ Imprimir Ticket (150mm Térmico)
    </button>
</div>

<div class="ticket-container" id="printable-ticket">
    <!-- ENCABEZADO EMPRESA -->
    <div class="ticket-header">
        <div class="business-icon">{icono}</div>
        <div class="business-name">{nombre_empresa}</div>
        <div class="business-info">
            <strong>RFC:</strong> {rfc}<br>
            <strong>Dirección:</strong> {direccion}
            {contacto_line}
        </div>
    </div>

    <!-- METADATOS TICKET -->
    <div class="ticket-meta">
        <div><span><strong>Folio:</strong> {folio}</span> <span><strong>Pago:</strong> {metodo_pago}</span></div>
        <div><span><strong>Fecha:</strong> {fecha}</span> <span><strong>Hora:</strong> {hora}</span></div>
    </div>

    <!-- DETALLE PRODUCTOS -->
    <table class="items-table">
        <thead>
            <tr>
                <th style="text-align: left;">Descripción</th>
                <th style="text-align: right;">Importe</th>
            </tr>
        </thead>
        <tbody>
            {filas_items_html}
        </tbody>
    </table>

    <!-- TOTALES E IMPUESTOS (IVA) -->
    <div class="totales-box">
        <div class="totales-row">
            <span>Subtotal neto:</span>
            <span>${base_subtotal:,.2f}</span>
        </div>
        <div class="totales-row">
            <span>IVA ({tasa_iva:.1f}%):</span>
            <span>${monto_iva:,.2f}</span>
        </div>
        <div class="totales-row gran-total">
            <span>TOTAL:</span>
            <span>${monto_total:,.2f} MXN</span>
        </div>
    </div>

    <!-- NOTAS / LEYENDAS FISCALES -->
    <div class="notes-box">
        💬 <strong>Nota:</strong> {notas}
    </div>

    <!-- SECCIÓN CÓDIGOS (QR FACTURACIÓN Y BARRAS IDENTIFICACIÓN) -->
    <div class="codes-section">
        <div class="qr-container">
            <img src="data:image/png;base64,{qr_b64}" alt="QR Facturación">
            <div class="qr-caption">📲 Escanea para Facturar en Línea</div>
        </div>

        <div class="barcode-container">
            {barcode_svg}
            <div class="barcode-caption">Código de Identificación de Ticket</div>
        </div>
    </div>

    <div class="footer-cut">
        - - - - - CORTE DE TICKET - - - - -
    </div>
</div>

</body>
</html>
"""
    return html_completo

def render_ticket_component(tk: dict, config: dict, height: int = 680):
    """Renderiza el ticket interactivo con iframe para impresión directa."""
    html_code = generar_html_ticket(tk, config)
    components.html(html_code, height=height, scrolling=True)

@st.dialog("🧾 Vista e Impresión de Ticket Oficial", width="large")
def mostrar_dialogo_ticket(tk: dict, config: dict):
    """Modal emergente para visualizar e imprimir cualquier ticket del sistema."""
    st.caption(f"Folio: `{tk.get('folio', 'N/A')}` | Total: **${tk.get('monto', 0.0):,.2f}** | Pago: {tk.get('metodo_pago', 'Efectivo')}")
    render_ticket_component(tk, config, height=650)
