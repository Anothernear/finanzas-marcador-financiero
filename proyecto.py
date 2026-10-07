import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import json
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Marcador Financiero & Control de Punto de Venta",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. BASE DE DATOS Y CONSTANTES
# ==========================================
CSV_FILE = "hermes_financial_db.csv"

PERFILES_RIESGO_ZONA = {
    "Zona Residencial / Centro Seguro": {
        "riesgo_seguridad_pct": 1.5,
        "riesgo_merma_sugerida": 2.0,
        "descripcion": "Zona con bajo índice delictivo y clientela constante. Prima de riesgo mínima."
    },
    "Zona Urbana Comercial / Afluencia Alta": {
        "riesgo_seguridad_pct": 3.5,
        "riesgo_merma_sugerida": 4.0,
        "descripcion": "Alto flujo de personas, mayor probabilidad de robo hormiga y competencia cercana."
    },
    "Zona Periférica / Conurbada": {
        "riesgo_seguridad_pct": 5.0,
        "riesgo_merma_sugerida": 4.5,
        "descripcion": "Riesgo moderado a alto por inseguridad en transporte de mercancías y fluctuación de demanda."
    },
    "Zona con Alta Incidencia Delictiva / Foco Rojo": {
        "riesgo_seguridad_pct": 8.0,
        "riesgo_merma_sugerida": 6.0,
        "descripcion": "Riesgo de extorsión, asaltos frecuentes o pérdida de mercancía. Requiere mayor tasa de descuento."
    },
    "Zona Rural / Municipio Pequeño": {
        "riesgo_seguridad_pct": 2.5,
        "riesgo_merma_sugerida": 3.0,
        "descripcion": "Bajo delito callejero, pero riesgo de merma por tiempos de transporte y cortes de energía/servicios."
    }
}

METODOS_PAGO = ["💵 Efectivo", "🏦 Transferencia", "💳 Tarjeta Débito", "💳 Tarjeta Crédito"]

def generar_folio_ticket(df):
    fecha_num = date.today().strftime("%Y%m%d")
    cant_ventas = len(df[df['tipo'] == 'venta']) + 1 if not df.empty else 1
    return f"TK-{fecha_num}-{cant_ventas:04d}"

def cargar_y_validar_db():
    hoy = date.today().strftime("%Y-%m-%d")
    ayer = (date.today() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    hace2 = (date.today() - pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    hace3 = (date.today() - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
    hace4 = (date.today() - pd.Timedelta(days=4)).strftime("%Y-%m-%d")
    hace5 = (date.today() - pd.Timedelta(days=5)).strftime("%Y-%m-%d")
    hace6 = (date.today() - pd.Timedelta(days=6)).strftime("%Y-%m-%d")

    if not os.path.exists(CSV_FILE):
        sample_data = [
            {"fecha": hace6, "hora": "09:30", "tipo": "venta", "monto": 2200.0, "concepto": "Ventas del día (Abarrotes)", "es_costo_directo": False, "metodo_pago": "💵 Efectivo", "folio": "TK-20260926-0001", "productos_detalle": ""},
            {"fecha": hace5, "hora": "11:15", "tipo": "venta", "monto": 2500.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo", "folio": "TK-20260927-0001", "productos_detalle": ""},
            {"fecha": hace4, "hora": "14:20", "tipo": "venta", "monto": 1900.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "🏦 Transferencia", "folio": "TK-20260928-0001", "productos_detalle": ""},
            {"fecha": hace3, "hora": "17:45", "tipo": "venta", "monto": 2800.0, "concepto": "Ventas del fin de semana", "es_costo_directo": False, "metodo_pago": "💳 Tarjeta Débito", "folio": "TK-20260929-0001", "productos_detalle": ""},
            {"fecha": hace2, "hora": "10:00", "tipo": "venta", "monto": 2100.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo", "folio": "TK-20260930-0001", "productos_detalle": ""},
            {"fecha": ayer, "hora": "18:30", "tipo": "venta", "monto": 2300.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💳 Tarjeta Crédito", "folio": "TK-20261001-0001", "productos_detalle": ""},
            {"fecha": hoy, "hora": "12:00", "tipo": "venta", "monto": 2400.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo", "folio": "TK-20261002-0001", "productos_detalle": ""},
            {"fecha": hace6, "hora": "10:00", "tipo": "gasto", "monto": 1300.0, "concepto": "Compra de refrescos y botanas (Mercancía)", "es_costo_directo": True, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": hace4, "hora": "12:00", "tipo": "gasto", "monto": 1500.0, "concepto": "Compra de lácteos y embutidos (Mercancía)", "es_costo_directo": True, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": hace2, "hora": "15:00", "tipo": "gasto", "monto": 2000.0, "concepto": "Abarrotes secos y enlatados (Mercancía)", "es_costo_directo": True, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": hoy, "hora": "09:00", "tipo": "gasto", "monto": 1400.0, "concepto": "Frutas, verduras y pan (Mercancía)", "es_costo_directo": True, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": hace5, "hora": "10:00", "tipo": "gasto", "monto": 1200.0, "concepto": "Renta de local (Semanal)", "es_costo_directo": False, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": hace3, "hora": "11:00", "tipo": "gasto", "monto": 450.0, "concepto": "Luz eléctrica y refrigeración", "es_costo_directo": False, "metodo_pago": "", "folio": "", "productos_detalle": ""},
            {"fecha": ayer, "hora": "19:00", "tipo": "gasto", "monto": 1400.0, "concepto": "Sueldo de ayudante (Semanal)", "es_costo_directo": False, "metodo_pago": "", "folio": "", "productos_detalle": ""},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        return df

    df = pd.read_csv(CSV_FILE)
    if 'es_costo_directo' not in df.columns:
        df['es_costo_directo'] = False
    if 'metodo_pago' not in df.columns:
        df['metodo_pago'] = ""
    if 'hora' not in df.columns:
        df['hora'] = "12:00"
    if 'folio' not in df.columns:
        df['folio'] = ""
    if 'productos_detalle' not in df.columns:
        df['productos_detalle'] = ""
    df.to_csv(CSV_FILE, index=False)
    return df

def restaurar_datos_demo():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return cargar_y_validar_db()

# ==========================================
# MODALES / DIÁLOGOS INTERACTIVOS DE RESUMEN
# ==========================================
@st.dialog("☀️ Detalle de Ventas Registradas Hoy")
def mostrar_modal_ventas_hoy(df_db, d):
    hoy_str = date.today().strftime("%Y-%m-%d")
    df_hoy = df_db[(df_db['tipo'] == 'venta') & (df_db['fecha'] == hoy_str)]
    st.metric("Venta Total Registrada Hoy", f"${d['venta_hoy']:,.2f}", delta=f"{len(df_hoy)} ticket(s) hoy")
    st.markdown("---")
    if not df_hoy.empty:
        df_disp = df_hoy[['folio', 'hora', 'concepto', 'monto', 'metodo_pago']].copy()
        df_disp.columns = ['Folio Ticket', 'Hora', 'Concepto / Productos', 'Monto ($)', 'Método de Cobro']
        st.dataframe(df_disp, use_container_width=True)
    else:
        st.info("No hay ventas registradas con la fecha de hoy.")

@st.dialog("📜 Historial Completo de Ventas Estratificado")
def mostrar_modal_ventas_totales(df_db, m):
    df_ventas = df_db[df_db['tipo'] == 'venta'].copy()
    st.metric("Ingresos Totales Históricos", f"${m['ingresos_totales']:,.2f}", delta=f"{len(df_ventas)} transacciones registradas")
    st.markdown("---")
    if not df_ventas.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            busqueda = st.text_input("🔍 Buscar por Folio o Producto:")
        with col_f2:
            metodo_f = st.selectbox("Filtrar por Método de Cobro:", ["Todos"] + METODOS_PAGO)
        
        df_filtrado = df_ventas.copy()
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado['folio'].astype(str).str.contains(busqueda, case=False, na=False) |
                df_filtrado['concepto'].astype(str).str.contains(busqueda, case=False, na=False)
            ]
        if metodo_f != "Todos":
            df_filtrado = df_filtrado[df_filtrado['metodo_pago'] == metodo_f]
            
        df_disp = df_filtrado[['fecha', 'hora', 'folio', 'concepto', 'monto', 'metodo_pago']].copy()
        df_disp.columns = ['Fecha', 'Hora', 'Folio Ticket', 'Concepto / Productos', 'Monto ($)', 'Método de Cobro']
        st.dataframe(df_disp.sort_values(by=['Fecha', 'Hora'], ascending=False), use_container_width=True)
    else:
        st.info("No se han registrado ventas aún.")

def agrupar_ventas_por_intervalo_hora(df_ventas, opcion_intervalo):
    df = df_ventas.copy()
    
    def extraer_hora(h_str):
        try:
            return int(str(h_str).split(":")[0])
        except Exception:
            return 12
            
    df['hora_int'] = df['hora'].apply(extraer_hora)
    
    if opcion_intervalo == "Franjas Comerciales":
        def rango_franja(h):
            if 6 <= h < 11:
                return "1. 🌅 Mañana (06:00 - 11:00)"
            elif 11 <= h < 15:
                return "2. ☀️ Medio día (11:00 - 15:00)"
            elif 15 <= h < 19:
                return "3. 🌆 Tarde (15:00 - 19:00)"
            else:
                return "4. 🌙 Noche (19:00 - 23:00)"
        df['intervalo_lbl'] = df['hora_int'].apply(rango_franja)
        df_group = df.groupby('intervalo_lbl', as_index=False)['monto'].sum()
        df_group = df_group.sort_values(by='intervalo_lbl')
    else:
        horas_num = int(opcion_intervalo.split()[0])
        def rango_bin(h):
            start = (h // horas_num) * horas_num
            end = min(24, start + horas_num)
            return f"{start:02d}:00 - {end:02d}:00"
            
        df['intervalo_lbl'] = df['hora_int'].apply(rango_bin)
        df_group = df.groupby('intervalo_lbl', as_index=False)['monto'].sum()
        df_group = df_group.sort_values(by='intervalo_lbl')
        
    return df_group

@st.dialog("📊 Análisis de Días Récord y Horarios Pico")
def mostrar_modal_horarios_y_dias(df_db):
    df_ventas = df_db[df_db['tipo'] == 'venta'].copy()
    if df_ventas.empty:
        st.info("Registra ventas para ver el análisis de días y horarios pico.")
        return
        
    df_diario = df_ventas.groupby('fecha')['monto'].sum().reset_index()
    dia_max = df_diario.loc[df_diario['monto'].idxmax()]
    
    fecha_dt = pd.to_datetime(dia_max['fecha'])
    dias_semana_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    nombre_dia = dias_semana_es[fecha_dt.weekday()]
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.success(f"🏆 **Día con Mayor Venta Registrada:**\n\n**{nombre_dia} ({dia_max['fecha']})**\n\n💰 Venta: **${dia_max['monto']:,.2f}**")
    
    with col_d2:
        df_ventas['dia_nombre'] = pd.to_datetime(df_ventas['fecha']).apply(lambda x: dias_semana_es[x.weekday()])
        dia_prom = df_ventas.groupby('dia_nombre')['monto'].mean().reset_index()
        dia_top_prom = dia_prom.loc[dia_prom['monto'].idxmax()]
        st.info(f"📅 **Día más Fuerte en Promedio:**\n\n**{dia_top_prom['dia_nombre']}**\n\nPromedio: **${dia_top_prom['monto']:,.2f} / día**")

    st.markdown("---")
    st.markdown("### ⏰ Histograma de Ventas por Intervalo Horario")
    
    col_int1, col_int2 = st.columns([2, 1])
    with col_int1:
        opcion_intervalo = st.selectbox(
            "⏱️ Modificar intervalo de tiempo por hora:",
            ["1 hora", "2 horas", "3 horas", "4 horas", "6 horas", "Franjas Comerciales"],
            index=0,
            key="modal_sel_intervalo"
        )
    with col_int2:
        st.caption("Ajusta las barras del histograma para analizar tus ventas en franjas más detalladas o amplias.")
        
    df_horario = agrupar_ventas_por_intervalo_hora(df_ventas, opcion_intervalo)
    
    fig_h = px.bar(
        df_horario, x='intervalo_lbl', y='monto',
        title=f"Histograma de Ventas por Intervalo ({opcion_intervalo})",
        labels={'intervalo_lbl': 'Intervalo de Horas', 'monto': 'Venta Acumulada ($)'},
        color='monto',
        color_continuous_scale=['#38bdf8', '#0ea5e9', '#0284c7']
    )
    fig_h.update_layout(xaxis_title="Intervalos por Hora", yaxis_title="Venta Total ($)")
    st.plotly_chart(fig_h, use_container_width=True)

@st.dialog("💰 Desglose Financiero de Ganancia Neta")
def mostrar_modal_ganancia_neta(m, r):
    st.markdown("### 📊 Cascada de Ganancia Real")
    st.write(f"➕ **Ventas Totales Cobradas:** ${m['ingresos_totales']:,.2f}")
    st.write(f"➖ **Costos Variables (Mercancía):** -${m['costos_variables']:,.2f}")
    st.write(f"➖ **Costos Fijos (Renta, Luz, etc.):** -${m['costos_fijos']:,.2f}")
    st.markdown("---")
    st.markdown(f"🟢 **Utilidad Operativa Neta:** **${m['utilidad_neta']:,.2f}**")
    st.write(f"🛡️ *Merma Estimada por Riesgo de Zona ({r['riesgo_merma_pct']}%):* -${r['merma_estimada_pesos']:,.2f}")
    st.markdown(f"💎 **Ganancia Ajustada por Riesgo:** **${r['utilidad_ajustada_riesgo']:,.2f}**")

# ==========================================
# 3. ESTADO DE SESIÓN
# ==========================================
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

if 'config_negocio' not in st.session_state:
    st.session_state.config_negocio = {
        "nombre": "Abarrotes El Güero",
        "giro": "Abarrotes / Tiendita",
        "caja_disponible": 10000.0,
        "inversion_inicial": 25000.0,
        "tasa_descuento_base": 0.10,
        "ubicacion_estado": "Estado de México / CDMX",
        "tipo_zona": "Zona Urbana Comercial / Afluencia Alta",
        "riesgo_merma_pct": 4.0,
        "riesgo_seguridad_pct": 3.5
    }

if 'slider_riesgo_seg' not in st.session_state:
    zona_default = st.session_state.config_negocio.get("tipo_zona", "Zona Urbana Comercial / Afluencia Alta")
    st.session_state.slider_riesgo_seg = float(PERFILES_RIESGO_ZONA[zona_default]["riesgo_seguridad_pct"])

if 'slider_riesgo_merma' not in st.session_state:
    zona_default = st.session_state.config_negocio.get("tipo_zona", "Zona Urbana Comercial / Afluencia Alta")
    st.session_state.slider_riesgo_merma = float(PERFILES_RIESGO_ZONA[zona_default]["riesgo_merma_sugerida"])

# ==========================================
# 4. CÁLCULO FINANCIERO
# ==========================================
def calcular_tir_anual_real(inversion, flujo_anual):
    """TIR calculada con bisección sobre horizonte de 3 años. Más realista."""
    if inversion <= 0 or flujo_anual <= 0:
        return 0.0
    if flujo_anual * 3 <= inversion:
        return 0.0

    def npv(r):
        if r <= -1.0:
            return float('inf')
        return -inversion + sum(flujo_anual / ((1 + r) ** t) for t in range(1, 4))

    low, high = 0.00001, 20.0
    for _ in range(150):
        mid = (low + high) / 2.0
        val = npv(mid)
        if abs(val) < 0.5:
            break
        if val > 0:
            low = mid
        else:
            high = mid
    return round(mid * 100, 2)

def calcular_capas_financieras(df, config):
    hoy_str = date.today().strftime("%Y-%m-%d")

    df_ventas = df[df['tipo'] == 'venta']
    df_gastos = df[df['tipo'] == 'gasto']

    dias_registrados = max(df['fecha'].nunique(), 1) if not df.empty else 1

    ingresos_totales = float(df_ventas['monto'].sum()) if not df_ventas.empty else 0.0
    promedio_venta_diaria = ingresos_totales / dias_registrados if ingresos_totales > 0 else 0.0

    # Venta de hoy específicamente
    venta_hoy = float(df_ventas[df_ventas['fecha'] == hoy_str]['monto'].sum())

    costos_variables = float(df_gastos[df_gastos['es_costo_directo'] == True]['monto'].sum()) if not df_gastos.empty else 0.0
    costos_fijos = float(df_gastos[df_gastos['es_costo_directo'] == False]['monto'].sum()) if not df_gastos.empty else 0.0
    gastos_totales = costos_variables + costos_fijos

    riesgo_merma_pct = config.get('riesgo_merma_pct', 3.0)
    riesgo_seguridad_pct = config.get('riesgo_seguridad_pct', 2.0)

    merma_estimada = ingresos_totales * (riesgo_merma_pct / 100.0)

    utilidad_bruta = ingresos_totales - costos_variables
    margen_bruto_pct = (utilidad_bruta / ingresos_totales * 100) if ingresos_totales > 0 else 0.0

    utilidad_operativa = ingresos_totales - costos_variables - costos_fijos
    utilidad_ajustada_riesgo = max(0.0, utilidad_operativa - merma_estimada)

    margen_operativo_pct = (utilidad_operativa / ingresos_totales * 100) if ingresos_totales > 0 else 0.0

    ratio_costo_variable = (costos_variables / ingresos_totales) if ingresos_totales > 0 else 0.0
    margen_contribucion_ratio = 1.0 - ratio_costo_variable

    if margen_contribucion_ratio > 0 and costos_fijos > 0:
        punto_equilibrio_periodo = costos_fijos / margen_contribucion_ratio
        punto_equilibrio_diario = punto_equilibrio_periodo / dias_registrados
    elif costos_fijos == 0:
        punto_equilibrio_periodo = 0.0
        punto_equilibrio_diario = 0.0
    else:
        punto_equilibrio_periodo = float('inf')
        punto_equilibrio_diario = float('inf')

    caja_inicial = config.get('caja_disponible', 10000.0)
    inversion_inicial = config.get('inversion_inicial', 25000.0)

    caja_actual = max(0.0, caja_inicial + ingresos_totales - gastos_totales)
    gasto_diario_promedio = gastos_totales / dias_registrados if gastos_totales > 0 else 0.0
    dias_cobertura_gastos = (caja_actual / gasto_diario_promedio) if gasto_diario_promedio > 0 else 999.0

    # Proyecciones
    utilidad_diaria_promedio = utilidad_operativa / dias_registrados
    utilidad_diaria_ajustada = utilidad_ajustada_riesgo / dias_registrados
    utilidad_mensual_est = max(0.0, utilidad_diaria_promedio * 30.0)
    utilidad_mensual_ajustada = max(0.0, utilidad_diaria_ajustada * 30.0)
    utilidad_anual_est = max(0.0, utilidad_diaria_promedio * 365.0)
    utilidad_anual_ajustada = max(0.0, utilidad_diaria_ajustada * 365.0)

    roi_anual_pct = ((utilidad_diaria_promedio * 365.0) / inversion_inicial * 100) if inversion_inicial > 0 else 0.0
    payback_meses = (inversion_inicial / utilidad_mensual_est) if utilidad_mensual_est > 0 else 999.0

    # Tasa de descuento ajustada por riesgo
    tasa_base = config.get('tasa_descuento_base', 0.10)
    prima_zona = riesgo_seguridad_pct / 100.0
    tasa_descuento_ajustada = tasa_base + prima_zona

    tasa_mensual_ajustada = (1 + tasa_descuento_ajustada) ** (1 / 12) - 1
    tasa_diaria_ajustada = (1 + tasa_descuento_ajustada) ** (1 / 365) - 1

    # VAN (Valor Actual Neto) diario, mensual y anual — ajustados por riesgo
    # VAN diario: 30 días de flujo diario
    van_diario = -inversion_inicial + sum(
        utilidad_diaria_ajustada / ((1 + tasa_diaria_ajustada) ** t) for t in range(1, 31)
    ) if inversion_inicial > 0 else 0.0

    # VAN mensual: 12 meses de flujo mensual
    van_mensual = -inversion_inicial + sum(
        utilidad_mensual_ajustada / ((1 + tasa_mensual_ajustada) ** t) for t in range(1, 13)
    ) if inversion_inicial > 0 else 0.0

    # VAN anual: 3 años de flujo anual
    van_anual = -inversion_inicial + sum(
        utilidad_anual_ajustada / ((1 + tasa_descuento_ajustada) ** t) for t in range(1, 4)
    ) if inversion_inicial > 0 else 0.0

    # TIR real (horizonte 3 años)
    tir_anual = calcular_tir_anual_real(inversion_inicial, utilidad_anual_est)

    # Métodos de pago (sólo ventas)
    mp_counts = {}
    if not df_ventas.empty and 'metodo_pago' in df_ventas.columns:
        for mp in METODOS_PAGO:
            mp_counts[mp] = float(df_ventas[df_ventas['metodo_pago'] == mp]['monto'].sum())
    else:
        for mp in METODOS_PAGO:
            mp_counts[mp] = 0.0

    return {
        "negocio": {
            "nombre": config.get('nombre', 'Mi Negocio'),
            "giro": config.get('giro', 'Abarrotes / Tiendita'),
            "ubicacion_estado": config.get('ubicacion_estado', 'Estado de México / CDMX'),
            "tipo_zona": config.get('tipo_zona', 'Zona Urbana Comercial')
        },
        "metricas": {
            "ingresos_totales": round(ingresos_totales, 2),
            "costos_variables": round(costos_variables, 2),
            "costos_fijos": round(costos_fijos, 2),
            "gastos_totales": round(gastos_totales, 2),
            "margen_bruto_pct": round(margen_bruto_pct, 1),
            "margen_operativo_pct": round(margen_operativo_pct, 1),
            "punto_equilibrio_diario": round(punto_equilibrio_diario, 2) if punto_equilibrio_diario != float('inf') else 0.0,
            "promedio_venta_diaria": round(promedio_venta_diaria, 2),
            "utilidad_neta": round(utilidad_operativa, 2),
            "utilidad_mensual_est": round(utilidad_mensual_est, 2),
            "utilidad_anual_est": round(utilidad_anual_est, 2),
            "utilidad_diaria": round(utilidad_diaria_promedio, 2),
            "dias_registrados": dias_registrados
        },
        "riesgos": {
            "riesgo_merma_pct": riesgo_merma_pct,
            "riesgo_seguridad_pct": riesgo_seguridad_pct,
            "merma_estimada_pesos": round(merma_estimada, 2),
            "tasa_descuento_total_pct": round(tasa_descuento_ajustada * 100, 1),
            "utilidad_ajustada_riesgo": round(utilidad_ajustada_riesgo, 2),
            "utilidad_mensual_ajustada": round(utilidad_mensual_ajustada, 2),
        },
        "evaluacion_economica": {
            "inversion_inicial": round(inversion_inicial, 2),
            "roi_anual_pct": round(roi_anual_pct, 1),
            "van_diario": round(van_diario, 2),
            "van_mensual": round(van_mensual, 2),
            "van_anual": round(van_anual, 2),
            "tir_anual_pct": round(tir_anual, 1),
            "payback_meses": round(payback_meses, 1)
        },
        "caja": {
            "caja_disponible": round(caja_actual, 2),
            "caja_inicial": round(caja_inicial, 2),
            "dias_cobertura": round(dias_cobertura_gastos, 1) if dias_cobertura_gastos < 999 else 999
        },
        "diario": {
            "venta_hoy": round(venta_hoy, 2),
            "utilidad_diaria": round(utilidad_diaria_promedio, 2)
        },
        "metodos_pago": mp_counts
    }

# ==========================================
# 5. DIAGNÓSTICO EN LENGUAJE SENCILLO
# ==========================================
def generar_diagnostico(m):
    met = m["metricas"]
    caja = m["caja"]
    econ = m["evaluacion_economica"]
    rsk = m["riesgos"]
    neg = m["negocio"]
    diagnostico = []

    if met["costos_fijos"] == 0 and met["costos_variables"] == 0:
        diagnostico.append({
            "tipo": "advertencia",
            "titulo": "⚠️ Sin registros de gastos todavía",
            "texto": "Para calcular tu punto de equilibrio y rentabilidad real, registra tus compras de mercancía y gastos fijos (renta, luz, etc.) en el panel lateral."
        })
    elif met["promedio_venta_diaria"] < met["punto_equilibrio_diario"]:
        dif = met["punto_equilibrio_diario"] - met["promedio_venta_diaria"]
        diagnostico.append({
            "tipo": "alerta",
            "titulo": "🔴 Alerta: Ventas por debajo del Punto de Equilibrio",
            "texto": f"Estás vendiendo **${met['promedio_venta_diaria']:,.2f}/día** y requieres **${met['punto_equilibrio_diario']:,.2f}/día** para cubrir costos. Te faltan **${dif:,.2f}/día**."
        })
    else:
        colchon = met["promedio_venta_diaria"] - met["punto_equilibrio_diario"]
        diagnostico.append({
            "tipo": "exito",
            "titulo": "🟢 ¡Tu negocio genera ganancias operativas!",
            "texto": f"Ventas promedio de **${met['promedio_venta_diaria']:,.2f}/día**, con colchón de ganancia de **${colchon:,.2f} diarios** sobre tu meta mínima."
        })

    if rsk["riesgo_seguridad_pct"] >= 5.0:
        diagnostico.append({
            "tipo": "alerta",
            "titulo": f"🛡️ Alerta de Riesgo Alto en {neg['tipo_zona']}",
            "texto": f"La zona tiene una prima de riesgo de **{rsk['riesgo_seguridad_pct']}%** y merma estimada de **${rsk['merma_estimada_pesos']:,.2f}**. El negocio debe generar mayor ganancia para compensar los imprevistos del lugar."
        })
    else:
        diagnostico.append({
            "tipo": "info",
            "titulo": f"📍 Perfil de Ubicación: {neg['tipo_zona']}",
            "texto": f"Riesgo de zona moderado (+{rsk['riesgo_seguridad_pct']}%). Rendimiento mínimo exigido al negocio: **{rsk['tasa_descuento_total_pct']}% anual**."
        })

    if met["gastos_totales"] > 0:
        van = econ["van_anual"]
        if van > 0:
            diagnostico.append({
                "tipo": "exito",
                "titulo": "📈 Proyecto Financieramente Viable (Aún con Riesgo de Zona)",
                "texto": f"Incluso descontando los riesgos de tu localidad, el VAN anual es positivo (**${van:,.2f}**), superando la tasa exigida del {rsk['tasa_descuento_total_pct']}%."
            })
        else:
            diagnostico.append({
                "tipo": "advertencia",
                "titulo": "📉 Rentabilidad insuficiente frente al riesgo del lugar",
                "texto": f"El VAN anual actual es de **${van:,.2f}**. Con los riesgos de la zona, la ganancia actual no compensa suficientemente el capital invertido."
            })

    return diagnostico

# ==========================================
# 6. ONBOARDING — SIN st.form PARA REACTIVIDAD
# ==========================================
def on_change_zona():
    zona_sel = st.session_state.get("_sel_zona_onboarding", "Zona Urbana Comercial / Afluencia Alta")
    datos = PERFILES_RIESGO_ZONA.get(zona_sel, {})
    st.session_state.slider_riesgo_seg = float(datos.get("riesgo_seguridad_pct", 3.5))
    st.session_state.slider_riesgo_merma = float(datos.get("riesgo_merma_sugerida", 4.0))

if not st.session_state.onboarding_complete:
    st.title("⚡ Configuración del Negocio & Análisis de Riesgo")
    st.caption("Personaliza los datos de tu negocio y calibra los riesgos según el lugar donde operas.")
    st.markdown("---")

    col_on1, col_on2 = st.columns(2)

    with col_on1:
        st.markdown("#### 🏪 1. Identidad y Capital")
        nombre = st.text_input("¿Cómo se llama tu negocio?", value="Abarrotes El Güero")
        giro = st.selectbox(
            "Giro comercial:",
            ["Abarrotes / Tiendita", "Restaurante / Cafetería / Comida", "Ropa / Calzado / Novedades",
             "Servicios / Taller / Oficio", "Farmacia / Salud", "Otro comercio"]
        )
        caja = st.number_input("💵 Dinero actual disponible en caja/banco ($):", value=10000.0, step=500.0)
        inversion_inicial = st.number_input("🏦 Inversión total para arrancar el negocio ($):", value=25000.0, step=1000.0)
        tasa_base = st.number_input(
            "🎯 Ganancia mínima aceptable sin riesgo — ej. CETES/Banco (%):",
            value=10.0, step=0.5,
            help="Es el rendimiento que ganarías poniendo tu dinero en algo seguro como CETES. Tu negocio debe ganar MÁS que eso."
        ) / 100.0

    with col_on2:
        st.markdown("#### 📍 2. Ubicación y Riesgo del Entorno")
        ubicacion_estado = st.text_input("Estado o Municipio donde operas:", value="Estado de México / CDMX")

        tipo_zona = st.selectbox(
            "¿Cómo es la zona de tu negocio?",
            list(PERFILES_RIESGO_ZONA.keys()),
            index=1,
            key="_sel_zona_onboarding",
            on_change=on_change_zona
        )

        datos_zona = PERFILES_RIESGO_ZONA[tipo_zona]
        st.info(f"ℹ️ {datos_zona['descripcion']}")

        st.markdown("**🚨 Prima de riesgo por entorno / inseguridad (%)**")
        st.caption("Porcentaje extra que debe ganar el negocio para justificar operar en esta zona. Se suma automáticamente a tu tasa mínima.")
        riesgo_seguridad_val = st.slider(
            "Prima de riesgo del entorno",
            min_value=0.0, max_value=15.0,
            value=st.session_state.slider_riesgo_seg,
            step=0.5, key="slider_riesgo_seg",
            label_visibility="collapsed"
        )

        st.markdown("**📦 Merma o pérdidas estimadas (%)**")
        st.caption("Porcentaje de ventas/mercancía que se pierde por robo hormiga, caducidad, roturas o descompostura según la zona.")
        riesgo_merma_val = st.slider(
            "Merma estimada",
            min_value=0.0, max_value=10.0,
            value=st.session_state.slider_riesgo_merma,
            step=0.5, key="slider_riesgo_merma",
            label_visibility="collapsed"
        )

    st.markdown("")
    if st.button("🚀 Guardar y Ver mi Marcador Financiero", use_container_width=True, type="primary"):
        st.session_state.config_negocio = {
            "nombre": nombre.strip() if nombre.strip() else "Mi Negocio",
            "giro": giro,
            "caja_disponible": float(caja),
            "inversion_inicial": float(inversion_inicial) if inversion_inicial > 0 else 1000.0,
            "tasa_descuento_base": float(tasa_base),
            "ubicacion_estado": ubicacion_estado,
            "tipo_zona": tipo_zona,
            "riesgo_seguridad_pct": float(riesgo_seguridad_val),
            "riesgo_merma_pct": float(riesgo_merma_val)
        }
        st.session_state.onboarding_complete = True
        st.rerun()
    st.stop()

# ==========================================
# 7. DASHBOARD PRINCIPAL
# ==========================================
config = st.session_state.config_negocio
df_db = cargar_y_validar_db()
calculos = calcular_capas_financieras(df_db, config)
m = calculos["metricas"]
e = calculos["evaluacion_economica"]
c = calculos["caja"]
r = calculos["riesgos"]
n = calculos["negocio"]
d = calculos["diario"]
mp = calculos["metodos_pago"]

# Encabezado
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"# 🛡️ {config['nombre']}")
    st.caption(f"📂 **Giro:** {config['giro']} | 📍 **Ubicación:** {n['ubicacion_estado']} ({n['tipo_zona']}) | 📅 **Días analizados:** {m['dias_registrados']}")
with col_head2:
    st.metric("Riesgo de Zona", f"+{r['riesgo_seguridad_pct']}%", help="Prima de riesgo adicional por la ubicación del negocio")
    st.metric("Registros totales", len(df_db))

# Mostrar Ticket si se acaba de generar una venta
if st.session_state.get("ultimo_ticket"):
    tk = st.session_state.ultimo_ticket
    with st.container(border=True):
        col_tk1, col_tk2 = st.columns([3, 1])
        with col_tk1:
            st.markdown(f"### 🧾 Ticket de Venta Generado — Folio: `{tk['folio']}`")
            st.caption(f"📅 **Fecha:** {tk['fecha']} | ⏰ **Hora:** {tk['hora']} | 💳 **Pago:** {tk['metodo_pago']}")
            if tk.get("items"):
                st.markdown("**Detalle de la cuenta:**")
                for item_t in tk["items"]:
                    st.write(f"• **{item_t['cantidad']}x {item_t['producto']}** @ ${item_t['precio_unitario']:,.2f} c/u = **${item_t['subtotal']:,.2f}**")
            st.markdown(f"#### **Total Cobrado: ${tk['monto']:,.2f}**")
        with col_tk2:
            if st.button("❌ Cerrar Ticket", use_container_width=True):
                del st.session_state.ultimo_ticket
                st.rerun()

st.markdown("---")

# ==========================================
# 8. BARRA LATERAL (PUNTO DE VENTA AUTOMÁTICO)
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Registrar Dinero")
    st.caption("Apunta lo que entra y lo que sale:")

    tipo_opcion = st.selectbox(
        "¿Qué movimiento vas a ingresar?",
        [
            "🟢 Venta (Dinero que cobraste)",
            "🟠 Compra de Mercancía / Insumos (Costo Variable)",
            "🔴 Gasto del Local / Negocio (Costo Fijo)"
        ]
    )
    
    es_venta = "Venta" in tipo_opcion
    es_costo_var = "Mercancía" in tipo_opcion

    # Variables de captura
    monto_final = 0.0
    concepto_final = ""
    df_inv = None
    archivo_productos = "productos_template.csv"

    # Estado del carrito y control de versión de llaves para evitar errores de widget
    if "carrito_compras" not in st.session_state:
        st.session_state.carrito_compras = []
    if "prod_sel_prev" not in st.session_state:
        st.session_state.prod_sel_prev = None
    if "cant_key_ver" not in st.session_state:
        st.session_state.cant_key_ver = 0

    if es_venta:
        # Cargar inventario
        if os.path.exists(archivo_productos):
            df_inv = pd.read_csv(archivo_productos)
            if 'inventario' not in df_inv.columns:
                df_inv['inventario'] = 50
        
        tipo_venta = st.radio("Tipo de venta:", ["General (Libre)", "Producto del Inventario (Cuenta)"], horizontal=True)
        
        if tipo_venta == "Producto del Inventario (Cuenta)" and df_inv is not None and not df_inv.empty:
            lista_prods = df_inv['producto'].tolist()
            
            producto_sel = st.selectbox("Selecciona un producto:", lista_prods, key="sel_prod_sidebar")
            
            # Si cambió el producto seleccionado en el dropdown, incrementar versión de llave y refrescar
            if st.session_state.prod_sel_prev != producto_sel:
                st.session_state.prod_sel_prev = producto_sel
                st.session_state.cant_key_ver += 1
                st.rerun()

            # Obtener cuántas unidades de producto_sel hay actualmente en el carrito
            cant_actual_en_carr = 0
            for item_c in st.session_state.carrito_compras:
                if item_c['producto'] == producto_sel:
                    cant_actual_en_carr = item_c['cantidad']
                    break
                
            producto_idx = df_inv.index[df_inv['producto'] == producto_sel].tolist()[0]
            precio_unitario = float(df_inv.at[producto_idx, 'precio_venta'])
            inv_disponible = int(df_inv.at[producto_idx, 'inventario'])
            
            st.caption(f"Stock disponible: {inv_disponible} unidades | Precio: ${precio_unitario:,.2f}")
            
            # Widget key dinámico por versión de llave (solución infalible para reiniciar widgets en Streamlit)
            widget_key = f"cant_input_ver_{st.session_state.cant_key_ver}"
            
            cantidad_input = st.number_input(
                "Cantidad a llevar",
                min_value=0,
                max_value=max(inv_disponible, 0),
                value=cant_actual_en_carr,
                step=1,
                key=widget_key
            )

            # ACTUALIZACIÓN DEL CARRITO SEGÚN LA CANTIDAD ELEGIDA (Si es 0, no se agrega / se quita)
            if cantidad_input == 0:
                st.session_state.carrito_compras = [
                    item for item in st.session_state.carrito_compras if item['producto'] != producto_sel
                ]
            else:
                encontrado = False
                for item in st.session_state.carrito_compras:
                    if item['producto'] == producto_sel:
                        item['cantidad'] = cantidad_input
                        item['subtotal'] = cantidad_input * precio_unitario
                        item['producto_idx'] = producto_idx
                        encontrado = True
                        break
                if not encontrado:
                    st.session_state.carrito_compras.append({
                        "producto": producto_sel,
                        "producto_idx": producto_idx,
                        "cantidad": cantidad_input,
                        "precio_unitario": precio_unitario,
                        "subtotal": cantidad_input * precio_unitario
                    })

            # Mostrar resumen de la cuenta
            if len(st.session_state.carrito_compras) > 0:
                st.markdown("---")
                st.markdown("🛒 **Cuenta Actual del Cliente:**")
                total_cuenta = 0.0
                conceptos_lista = []
                
                indices_a_borrar = []
                for idx_item, item in enumerate(st.session_state.carrito_compras):
                    col_ci1, col_ci2 = st.columns([3, 1])
                    with col_ci1:
                        st.write(f"• **{item['cantidad']}x {item['producto']}** (${item['subtotal']:,.2f})")
                    with col_ci2:
                        if st.button("❌", key=f"del_cart_{idx_item}_{item['producto']}"):
                            indices_a_borrar.append(idx_item)
                            
                    total_cuenta += item['subtotal']
                    conceptos_lista.append(f"{item['cantidad']}x {item['producto']}")

                if indices_a_borrar:
                    for idx_b in sorted(indices_a_borrar, reverse=True):
                        st.session_state.carrito_compras.pop(idx_b)
                    st.session_state.cant_key_ver += 1
                    st.rerun()
                
                st.markdown(f"#### **Total Cuenta: ${total_cuenta:,.2f}**")
                
                monto_final = total_cuenta
                concepto_final = "Venta: " + ", ".join(conceptos_lista)
                
                if st.button("🗑️ Eliminar Cuenta", use_container_width=True):
                    st.session_state.carrito_compras = []
                    st.session_state.prod_sel_prev = None
                    st.session_state.cant_key_ver += 1
                    st.rerun()
            else:
                monto_final = 0.0
                concepto_final = ""
                st.caption("La cuenta del cliente está vacía (0 productos).")

            mostrar_pago = True
        else:
            monto_final = st.number_input("Monto en dinero ($)", min_value=1.0, step=50.0, value=150.0)
            concepto_final = st.text_input("¿En qué concepto o motivo?", value="Ventas del día", help="Ej: Ventas del día, pedido especial, etc.")
            mostrar_pago = True
    else:
        monto_final = st.number_input("Monto en dinero ($)", min_value=1.0, step=50.0, value=150.0)
        if es_costo_var:
            concepto_def = "Compra de refrescos / abarrotes"
            ayuda_concepto = "Mercancía para revender o ingredientes."
        else:
            concepto_def = "Renta del local"
            ayuda_concepto = "Gastos fijos: Renta, luz, sueldos fijos, internet."
            
        concepto_final = st.text_input("¿En qué concepto o motivo?", value=concepto_def, help=ayuda_concepto)
        mostrar_pago = False

    hoy_fecha = date.today()
    fecha_input = st.date_input(
        "📅 Fecha del movimiento:",
        value=hoy_fecha,
        max_value=hoy_fecha,
        help="No se permiten fechas futuras. Puedes registrar movimientos de días anteriores."
    )

    if mostrar_pago:
        metodo_pago_input = st.selectbox("💳 Método de cobro:", METODOS_PAGO)
    else:
        metodo_pago_input = ""

    btn_guardar = st.button("💾 Cobrar y Generar Ticket", use_container_width=True, type="primary")
    if btn_guardar:
        if es_venta and tipo_venta == "Producto del Inventario (Cuenta)" and len(st.session_state.carrito_compras) == 0:
            st.error("⚠️ La cuenta está vacía (0 productos). Asigna cantidad a al menos un producto antes de cobrar.")
        else:
            fecha_str = fecha_input.strftime("%Y-%m-%d")
            hora_str = datetime.now().strftime("%H:%M")
            folio_str = generar_folio_ticket(df_db) if es_venta else ""

            detalle_json = ""
            if es_venta and tipo_venta == "Producto del Inventario (Cuenta)" and st.session_state.carrito_compras:
                detalle_json = json.dumps([
                    {"producto": it['producto'], "cantidad": it['cantidad'], "precio_unitario": it['precio_unitario'], "subtotal": it['subtotal']}
                    for it in st.session_state.carrito_compras
                ], ensure_ascii=False)

            nuevo_reg = {
                "fecha": fecha_str,
                "hora": hora_str,
                "tipo": "venta" if es_venta else "gasto",
                "monto": float(monto_final),
                "concepto": concepto_final.strip() if concepto_final.strip() else ("Venta" if es_venta else "Gasto"),
                "es_costo_directo": es_costo_var,
                "metodo_pago": metodo_pago_input if es_venta else "",
                "folio": folio_str,
                "productos_detalle": detalle_json
            }
            df_actualizado = pd.concat([df_db, pd.DataFrame([nuevo_reg])], ignore_index=True)
            df_actualizado.to_csv(CSV_FILE, index=False)
            
            # Descontar inventario de todos los productos en la cuenta
            if es_venta and tipo_venta == "Producto del Inventario (Cuenta)" and df_inv is not None:
                for item in st.session_state.carrito_compras:
                    p_idx = item['producto_idx']
                    cant = item['cantidad']
                    df_inv.at[p_idx, 'inventario'] = max(0, int(df_inv.at[p_idx, 'inventario']) - cant)
                df_inv.to_csv(archivo_productos, index=False)

                # Guardar último ticket generado para mostrar en pantalla
                st.session_state.ultimo_ticket = {
                    "folio": folio_str,
                    "fecha": fecha_str,
                    "hora": hora_str,
                    "monto": monto_final,
                    "metodo_pago": metodo_pago_input,
                    "concepto": concepto_final,
                    "items": list(st.session_state.carrito_compras)
                }
                st.session_state.carrito_compras = []
                st.session_state.prod_sel_prev = None
                st.session_state.cant_key_ver += 1
                
            st.success(f"✅ ¡Venta cobrada con éxito! Folio: {folio_str if folio_str else 'N/A'}")
            st.rerun()
        
    st.markdown("---")
    
    # === ALERTA DE META DIARIA ===
    ventas_hoy = d.get('venta_hoy', 0.0)
    pe_diario = m['punto_equilibrio_diario']
    falta_vender = max(0, pe_diario - ventas_hoy)
    
    if falta_vender > 0:
        st.markdown(f"""
        <div class='warning-box' style='padding:12px; margin-bottom:10px;'>
            <strong style='font-size:0.95rem; color:#b45309;'>🎯 Meta del día:</strong><br>
            Aún necesitas vender <b style='color:#b45309;'>${falta_vender:,.2f}</b> hoy para salir rentable (cubrir costos fijos).
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='success-box' style='padding:12px; margin-bottom:10px;'>
            <strong style='font-size:0.95rem; color:#065f46;'>🎉 ¡Meta alcanzada!</strong><br>
            Ya cubriste los costos del día. Todo lo demás es ganancia libre.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Opciones del Negocio")

    if st.button("🔄 Cargar Datos Demo", use_container_width=True):
        restaurar_datos_demo()
        st.success("Datos demo restaurados.")
        st.rerun()

    if st.button("🗑️ Vaciar Registros (Empezar en 0)", use_container_width=True):
        df_vacio = pd.DataFrame(columns=['fecha', 'hora', 'tipo', 'monto', 'concepto', 'es_costo_directo', 'metodo_pago', 'folio', 'productos_detalle'])
        df_vacio.to_csv(CSV_FILE, index=False)
        st.success("Base de datos limpia.")
        st.rerun()

    if st.button("✏️ Editar Parámetros y Riesgo de Zona", use_container_width=True):
        st.session_state.onboarding_complete = False
        st.rerun()

# ==========================================
# 9. SECCIÓN 1: RESUMEN DE VENTAS CON BOTONES INTERACTIVOS
# ==========================================
st.markdown("### ☀️ Resumen de Ventas")

col_v1, col_v2, col_v3, col_v4 = st.columns(4)

with col_v1:
    with st.container(border=True):
        st.metric(
            "☀️ Venta Registrada Hoy",
            f"${d['venta_hoy']:,.2f}",
            help="Suma de todas las ventas registradas con fecha de hoy."
        )
        if st.button("🔍 Ver Ventas de Hoy", use_container_width=True):
            mostrar_modal_ventas_hoy(df_db, d)

with col_v2:
    with st.container(border=True):
        st.metric(
            "💵 Ventas Totales (Período)",
            f"${m['ingresos_totales']:,.2f}",
            help="Suma total de todas las ventas registradas en la base de datos."
        )
        if st.button("📜 Historial de Ventas", use_container_width=True):
            mostrar_modal_ventas_totales(df_db, m)

with col_v3:
    with st.container(border=True):
        st.metric(
            "📊 Promedio Venta Diaria",
            f"${m['promedio_venta_diaria']:,.2f}",
            help="Promedio de ventas por día en los días que hay registros."
        )
        if st.button("⏰ Horarios y Días Pico", use_container_width=True):
            mostrar_modal_horarios_y_dias(df_db)

with col_v4:
    ganancia_neta_color = "normal" if m['utilidad_neta'] >= 0 else "inverse"
    with st.container(border=True):
        st.metric(
            "💰 Ganancia Neta Total",
            f"${m['utilidad_neta']:,.2f}",
            delta=f"−${r['merma_estimada_pesos']:,.2f} merma",
            delta_color="inverse",
            help=f"Ventas − Costos − Gastos."
        )
        if st.button("💡 Desglose de Ganancia", use_container_width=True):
            mostrar_modal_ganancia_neta(m, r)

st.markdown("---")

# ==========================================
# 10. SECCIÓN 2: OPERACIÓN DÍA A DÍA
# ==========================================
st.markdown("### 📊 Operación del Negocio")
st.caption("Meta mínima, caja y estado general.")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric(
            "🎯 Meta Mínima Diaria (Punto de Equilibrio)",
            f"${m['punto_equilibrio_diario']:,.2f}",
            help="Cuánto debes vender al día mínimo para no perder dinero."
        )

with col2:
    dias_txt = f"{c['dias_cobertura']} días" if c['dias_cobertura'] < 900 else "Sin gastos registrados"
    with st.container(border=True):
        st.metric(
            "🛡️ Autonomía de Caja",
            dias_txt,
            help="Cuántos días sobrevive el negocio pagando gastos con el dinero actual en caja."
        )

with col3:
    with st.container(border=True):
        st.metric(
            "💵 Dinero en Caja",
            f"${c['caja_disponible']:,.2f}",
            help="Estimado de caja considerando tu saldo inicial más ventas menos gastos."
        )

st.markdown("---")

# ==========================================
# 11. SECCIÓN 3: MÉTRICAS MULTI-HORIZONTE
# ==========================================
st.markdown("### 📈 Rentabilidad e Inversión")
st.caption(f"Tasa de rendimiento exigida: **{r['tasa_descuento_total_pct']}% anual** (Tasa libre de riesgo + Prima por zona).")

horizonte = st.radio(
    "Selecciona el horizonte de análisis:",
    ["📅 Vista Diaria", "🗓️ Vista Mensual", "📈 Vista Anual"],
    horizontal=True
)

if horizonte == "📅 Vista Diaria":
    van_val = e['van_diario']
    gan_val = m['utilidad_diaria']
    lbl = "día (próx. 30 días)"
elif horizonte == "🗓️ Vista Mensual":
    van_val = e['van_mensual']
    gan_val = m['utilidad_mensual_est']
    lbl = "mes (próx. 12 meses)"
else:
    van_val = e['van_anual']
    gan_val = m['utilidad_anual_est']
    lbl = "año (próx. 3 años)"

col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
    with st.container(border=True):
        st.metric(
            f"💰 Ganancia Proyectada / {lbl.split()[0].capitalize()}",
            f"${gan_val:,.2f}",
            help=f"Estimado de ganancia operativa por {lbl}."
        )

with col_e2:
    van_delta = "✅ Viable" if van_val >= 0 else "⚠️ Insuficiente"
    with st.container(border=True):
        st.metric(
            f"💎 VAN ({lbl.split()[0].capitalize()})",
            f"${van_val:,.2f}",
            delta=van_delta,
            delta_color="normal" if van_val >= 0 else "inverse",
            help=f"Valor Actual Neto proyectado a {lbl}. Si es positivo, el negocio rinde más que el banco incluso con riesgo de zona."
        )

with col_e3:
    tir_vs_tasa = "✅ Supera meta" if e['tir_anual_pct'] > r['tasa_descuento_total_pct'] else "⚠️ Bajo la meta"
    with st.container(border=True):
        st.metric(
            "🔥 TIR (Tasa de Retorno Anual)",
            f"{e['tir_anual_pct']}%",
            delta=tir_vs_tasa,
            delta_color="normal" if e['tir_anual_pct'] > r['tasa_descuento_total_pct'] else "inverse",
            help=f"Tasa interna de retorno. Tu meta a superar es {r['tasa_descuento_total_pct']}% anual."
        )

with col_e4:
    payback_display = f"{e['payback_meses']} meses" if e['payback_meses'] < 100 else "Indefinido"
    with st.container(border=True):
        st.metric(
            "⏱️ Tiempo de Retorno",
            payback_display,
            help="Tiempo estimado para recuperar toda tu inversión inicial."
        )

with st.container(border=True):
    col_roi1, col_roi2, col_roi3 = st.columns(3)
    with col_roi1:
        st.metric("⚡ ROI Anual", f"{e['roi_anual_pct']}%", help=f"Rendimiento anual sobre la inversión inicial de ${e['inversion_inicial']:,.2f}")
    with col_roi2:
        st.metric("🏦 Inversión Inicial", f"${e['inversion_inicial']:,.2f}")
    with col_roi3:
        st.metric("📋 Merma Estimada (Riesgo Zona)", f"${r['merma_estimada_pesos']:,.2f}",
                  help=f"Pérdidas estimadas al {r['riesgo_merma_pct']}% de tus ventas por la zona.")

st.markdown("---")

# ==========================================
# 12. MÉTODOS DE PAGO
# ==========================================
if m['ingresos_totales'] > 0:
    st.markdown("### 💳 Ventas por Método de Pago")
    mp_col1, mp_col2, mp_col3, mp_col4 = st.columns(4)
    for i, (metodo, cols) in enumerate(zip(METODOS_PAGO, [mp_col1, mp_col2, mp_col3, mp_col4])):
        monto_mp = mp.get(metodo, 0.0)
        pct = (monto_mp / m['ingresos_totales'] * 100) if m['ingresos_totales'] > 0 else 0.0
        with cols:
            with st.container(border=True):
                st.metric(metodo, f"${monto_mp:,.2f}", delta=f"{pct:.1f}% del total")

st.markdown("---")

# ==========================================
# 13. PESTAÑAS
# ==========================================
tab_diag, tab_riesgo, tab_graf, tab_tabla, tab_prod, tab_guia = st.tabs([
    "📢 Diagnóstico y Consejos",
    "🛡️ Riesgo y Ubicación",
    "📊 Gráficas",
    "📜 Historial",
    "📦 Productos y Rentabilidad",
    "🎓 Guía Financiera"
])

with tab_diag:
    st.markdown("#### 🧭 ¿Qué significa lo que ves en pantalla?")
    diagnosticos = generar_diagnostico(calculos)
    for item in diagnosticos:
        if item["tipo"] == "alerta":
            st.error(f"**{item['titulo']}**\n\n{item['texto']}")
        elif item["tipo"] == "advertencia":
            st.warning(f"**{item['titulo']}**\n\n{item['texto']}")
        elif item["tipo"] == "info":
            st.info(f"**{item['titulo']}**\n\n{item['texto']}")
        else:
            st.success(f"**{item['titulo']}**\n\n{item['texto']}")

    st.markdown("")
    st.markdown("#### 💡 Consejos Prácticos")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info("""
        **Para mitigar el riesgo del lugar:**
        1. **Fondo de contingencia:** Mantén un colchón de efectivo en caja para emergencias de luz, desabasto o eventualidades de la zona.
        2. **Control de mermas:** Anota productos rotos o caducados para saber qué proveedores te generan más pérdidas.
        """)
    with col_c2:
        st.info("""
        **Para maximizar ganancias:**
        1. **Supera tu meta diaria:** Cada peso que vendes arriba del Punto de Equilibrio es ganancia líquida.
        2. **Monitorea tu TIR:** Si supera el rendimiento exigido del lugar, el negocio justifica plenamente el esfuerzo.
        """)

with tab_riesgo:
    st.markdown(f"### 🛡️ Análisis de Riesgo — {n['ubicacion_estado']}")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        with st.container(border=True):
            st.markdown(f"#### 🚨 Prima de Riesgo por Entorno")
            st.metric("Sobretasa exigida", f"+{r['riesgo_seguridad_pct']}%")
            st.caption(f"Factores de seguridad, competencia y volatilidad de **{n['tipo_zona']}**.")

    with col_r2:
        with st.container(border=True):
            st.markdown(f"#### 📦 Merma Estimada")
            st.metric("Pérdida estimada", f"${r['merma_estimada_pesos']:,.2f}")
            st.caption(f"({r['riesgo_merma_pct']}% de ventas) por descomposturas, caducidad o robo hormiga según el entorno.")

    with col_r3:
        with st.container(border=True):
            st.markdown(f"#### 🎯 Tasa de Retorno Exigida")
            st.metric("Meta de rentabilidad", f"{r['tasa_descuento_total_pct']}% anual")
            st.caption(f"Tasa Base ({config.get('tasa_descuento_base', 0.10)*100:.1f}%) + Prima del Lugar ({r['riesgo_seguridad_pct']}%).")

    st.markdown("#### 🗺️ Tabla de Riesgo por Tipo de Zona en México")
    df_zonas = pd.DataFrame([
        {"Tipo de Zona": k, "Prima de Riesgo": f"+{v['riesgo_seguridad_pct']}%", "Merma Promedio": f"{v['riesgo_merma_sugerida']}%", "Características": v['descripcion']}
        for k, v in PERFILES_RIESGO_ZONA.items()
    ])
    tu_zona_idx = list(PERFILES_RIESGO_ZONA.keys()).index(n['tipo_zona']) if n['tipo_zona'] in PERFILES_RIESGO_ZONA else None
    st.dataframe(df_zonas, use_container_width=True)
    if tu_zona_idx is not None:
        st.caption(f"📍 Tu zona actual: **{n['tipo_zona']}** (fila {tu_zona_idx + 1})")

with tab_graf:
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        df_ventas_graf = df_db[df_db['tipo'] == 'venta']
        if not df_ventas_graf.empty:
            df_diario = df_ventas_graf.groupby('fecha')['monto'].sum().reset_index()
            fig_bar = px.bar(
                df_diario, x='fecha', y='monto',
                title="📅 Ventas Diarias vs Meta Mínima",
                labels={'fecha': 'Fecha', 'monto': 'Ventas ($)'},
                color_discrete_sequence=['#0284c7']
            )
            if m['punto_equilibrio_diario'] > 0:
                fig_bar.add_hline(
                    y=m['punto_equilibrio_diario'],
                    line_dash="dash", line_color="#f59e0b",
                    annotation_text=f"Meta mínima (${m['punto_equilibrio_diario']:,.0f}/día)",
                    annotation_position="top right"
                )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún para graficar.")

    with col_g2:
        # Gráfica de métodos de pago
        mp_data = {k: v for k, v in mp.items() if v > 0}
        if mp_data:
            df_mp = pd.DataFrame(list(mp_data.items()), columns=['Método de Pago', 'Monto'])
            fig_mp = px.pie(
                df_mp, values='Monto', names='Método de Pago',
                title="💳 Distribución por Método de Pago",
                hole=0.4,
                color_discrete_sequence=['#0284c7', '#10b981', '#f59e0b', '#ec4899']
            )
            st.plotly_chart(fig_mp, use_container_width=True)
        else:
            st.info("Registra ventas con método de pago para ver la gráfica.")

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        df_gastos_pie = df_db[df_db['tipo'] == 'gasto']
        if not df_gastos_pie.empty:
            df_gp = df_gastos_pie.groupby('concepto')['monto'].sum().reset_index()
            fig_pie = px.pie(
                df_gp, values='monto', names='concepto',
                title="🔴 ¿En qué se va el dinero? (Estructura de Gastos)",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay gastos registrados aún para graficar.")

    with col_g4:
        # VAN comparativo por horizonte
        van_data = pd.DataFrame({
            'Horizonte': ['30 Días', '12 Meses', '3 Años'],
            'VAN ($)': [e['van_diario'], e['van_mensual'], e['van_anual']]
        })
        fig_van = px.bar(
            van_data, x='Horizonte', y='VAN ($)',
            title="💎 VAN por Horizonte de Tiempo (Ajustado por Riesgo)",
            color='VAN ($)',
            color_continuous_scale=['#ef4444', '#f59e0b', '#10b981']
        )
        fig_van.add_hline(y=0, line_dash="dash", line_color="#64748b", annotation_text="Punto de viabilidad ($0)")
        st.plotly_chart(fig_van, use_container_width=True)

    # Histograma de Ventas con Intervalo Configurable por Hora
    st.markdown("---")
    st.markdown("### ⏱️ Histograma Configurable de Ventas por Intervalos de Hora")
    if not df_ventas_graf.empty:
        col_hg1, col_hg2 = st.columns([2, 1])
        with col_hg1:
            intervalo_tab_sel = st.selectbox(
                "Modificar intervalo por hora:",
                ["1 hora", "2 horas", "3 horas", "4 horas", "6 horas", "Franjas Comerciales"],
                index=1,
                key="tab_graf_sel_intervalo"
            )
        with col_hg2:
            st.info("💡 **Análisis de Horarios:** Selecciona **1 hora** para detectar la hora pico exacta de cobro o **4 horas** para analizar turnos de trabajo.")
            
        df_hist_tab = agrupar_ventas_por_intervalo_hora(df_ventas_graf, intervalo_tab_sel)
        fig_hist_tab = px.bar(
            df_hist_tab, x='intervalo_lbl', y='monto',
            title=f"Histograma de Ventas por Intervalo ({intervalo_tab_sel})",
            labels={'intervalo_lbl': 'Intervalo de Tiempo', 'monto': 'Venta Acumulada ($)'},
            color='monto',
            color_continuous_scale=['#f59e0b', '#0ea5e9', '#10b981']
        )
        fig_hist_tab.update_layout(xaxis_title="Intervalos por Hora", yaxis_title="Monto ($)")
        st.plotly_chart(fig_hist_tab, use_container_width=True)
    else:
        st.info("Registra ventas para activar el histograma de intervalos por hora.")

with tab_tabla:
    st.markdown("### 📋 Historial de Transacciones")

    col_fil1, col_fil2 = st.columns(2)
    with col_fil1:
        filtro_tipo = st.selectbox("Filtrar por tipo:", ["Todos", "Solo Ventas", "Solo Gastos"])
    with col_fil2:
        st.metric("Total de registros", len(df_db))

    if not df_db.empty:
        df_mostrar = df_db.copy()
        if filtro_tipo == "Solo Ventas":
            df_mostrar = df_mostrar[df_mostrar['tipo'] == 'venta']
        elif filtro_tipo == "Solo Gastos":
            df_mostrar = df_mostrar[df_mostrar['tipo'] == 'gasto']

        df_mostrar['Tipo'] = df_mostrar.apply(
            lambda row: "🟢 Venta" if row['tipo'] == 'venta'
            else ("🟠 Mercancía" if row.get('es_costo_directo', False) else "🔴 Gasto Fijo"),
            axis=1
        )
        df_mostrar['Método de Pago'] = df_mostrar.get('metodo_pago', '').fillna('')
        df_mostrar['Método de Pago'] = df_mostrar['Método de Pago'].replace('', '—')

        cols_mostrar = ['fecha', 'Tipo', 'concepto', 'monto', 'Método de Pago']
        df_final = df_mostrar[cols_mostrar].copy()
        df_final.columns = ['Fecha', 'Tipo', 'Concepto / Motivo', 'Monto ($)', 'Método de Pago']
        st.dataframe(df_final.sort_values(by='Fecha', ascending=False), use_container_width=True)
    else:
        st.info("Aún no tienes movimientos registrados.")

with tab_prod:
    st.markdown("### 📦 Análisis de Rentabilidad e Inventario")
    st.markdown("Edita tu inventario directamente en la tabla haciendo doble clic en las celdas. Registra tus **Ventas de Hoy** y presiona el botón para descontarlas automáticamente.")
    
    archivo_productos = "productos_template.csv"
    
    # Crea el archivo automáticamente con Inventario y Ventas si no existe
    if not os.path.exists(archivo_productos):
        default_data = "producto,categoria,costo_compra,precio_venta,inventario,unidades_vendidas_hoy\nCoca-Cola 600ml,Bebidas,13.00,18.00,50,0\nGansito Marinela,Snacks,14.00,18.00,30,0\nLeche Alpura 1L,Lácteos,21.00,26.00,20,0\nFrijol Pinto 1kg,Abarrotes,30.00,42.00,15,0\nHuevos (Docena),Abarrotes,28.00,38.00,10,0\nPan Bimbo Blanco,Panadería,35.00,45.00,12,0\nSabritas Sal 42g,Snacks,12.00,16.00,40,0\nTortillas 1kg,Alimentos,18.00,22.00,20,0\nAtún Dolores en Agua,Abarrotes,16.00,21.00,25,0\nCerveza Corona 355ml,Bebidas,15.00,22.00,60,0"
        with open(archivo_productos, "w", encoding="utf-8") as f:
            f.write(default_data)
            
    df_prod = pd.read_csv(archivo_productos)
    
    # Compatibilidad si el archivo viejo no tenía estas columnas
    if 'inventario' not in df_prod.columns:
        df_prod['inventario'] = 50
    if 'unidades_vendidas_hoy' not in df_prod.columns:
        df_prod['unidades_vendidas_hoy'] = 0

    # Calcular rentabilidad (Estas no se pueden editar manualmente)
    df_prod['Ganancia Neta ($)'] = df_prod['precio_venta'] - df_prod['costo_compra']
    df_prod['Rentabilidad (Margen %)'] = (df_prod['Ganancia Neta ($)'] / df_prod['precio_venta']) * 100
    
    pe_diario = m['punto_equilibrio_diario']
    df_prod['Unidades para sacar el día'] = (pe_diario / df_prod['Ganancia Neta ($)']).replace([float('inf'), -float('inf')], 0).clip(lower=0).apply(np.ceil)
    df_prod.loc[df_prod['Ganancia Neta ($)'] <= 0, 'Unidades para sacar el día'] = np.nan
    
    # --- TABLA EDITABLE (El usuario puede cambiar valores directo en la interfaz) ---
    edited_df = st.data_editor(
        df_prod,
        use_container_width=True,
        num_rows="dynamic", # Permite añadir nuevas filas (productos)
        disabled=["Ganancia Neta ($)", "Rentabilidad (Margen %)", "Unidades para sacar el día"],
        column_config={
            "producto": st.column_config.TextColumn("Producto", required=True),
            "categoria": st.column_config.TextColumn("Categoría"),
            "costo_compra": st.column_config.NumberColumn("Costo Compra ($)", format="$%.2f", min_value=0),
            "precio_venta": st.column_config.NumberColumn("Precio Venta ($)", format="$%.2f", min_value=0),
            "inventario": st.column_config.NumberColumn("Inventario Actual", min_value=0, step=1),
            "unidades_vendidas_hoy": st.column_config.NumberColumn("Ventas de Hoy", min_value=0, step=1),
            "Ganancia Neta ($)": st.column_config.NumberColumn("Ganancia Neta", format="$%.2f"),
            "Rentabilidad (Margen %)": st.column_config.NumberColumn("Margen", format="%.1f%%"),
            "Unidades para sacar el día": st.column_config.NumberColumn("Meta Diaria (Unid.)", format="%d")
        },
        key="editor_productos"
    )
    
    # --- BOTONES DE ACCIÓN ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar Cambios Manuales", use_container_width=True):
            cols_to_save = ['producto', 'categoria', 'costo_compra', 'precio_venta', 'inventario', 'unidades_vendidas_hoy']
            edited_df[cols_to_save].to_csv(archivo_productos, index=False)
            st.success("¡Datos e inventario guardados!")
            st.rerun()

    with col2:
        if st.button("🛒 Procesar Ventas y Descontar Inventario", use_container_width=True):
            # Restar ventas del inventario y evitar números negativos
            edited_df['inventario'] = edited_df['inventario'] - edited_df['unidades_vendidas_hoy']
            edited_df['inventario'] = edited_df['inventario'].clip(lower=0) 
            
            # Reiniciar la columna de ventas de hoy a 0
            edited_df['unidades_vendidas_hoy'] = 0 
            
            # Guardar el archivo
            cols_to_save = ['producto', 'categoria', 'costo_compra', 'precio_venta', 'inventario', 'unidades_vendidas_hoy']
            edited_df[cols_to_save].to_csv(archivo_productos, index=False)
            
            st.success("¡Ventas procesadas exitosamente! El inventario se ha actualizado.")
            st.rerun()

    # --- ALERTAS E INTERPRETACIONES ---
    if len(edited_df) > 0 and 'Rentabilidad (Margen %)' in edited_df.columns:
        try:
            producto_top = edited_df.loc[edited_df['Rentabilidad (Margen %)'].idxmax()]
            producto_vol = edited_df.dropna(subset=['Unidades para sacar el día']).loc[edited_df.dropna(subset=['Unidades para sacar el día'])['Unidades para sacar el día'].idxmin()]
            
            st.markdown(f"""
            <div class='warning-box'>
                <strong style='color:#b45309;'>🚨 Alerta de Ventas Diarias:</strong><br>
                Para recuperar tu inversión y sacar el día (cubriendo tus <b>${pe_diario:,.2f}</b> de costos operativos diarios), tendrías que vender, por ejemplo, <b>{producto_vol['Unidades para sacar el día']:.0f} unidades de {producto_vol['producto']}</b>.<br><br>
                💡 <em>Sugerencia estratégica:</em> Concéntrate en impulsar los productos de mayor margen como el <b>{producto_top['producto']}</b> ({producto_top['Rentabilidad (Margen %)']:.1f}% de ganancia).
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    # --- PRODUCTO MÁS Y MENOS VENDIDO ---
    st.markdown("---")
    st.markdown("### 🏆 Ranking de Ventas por Producto (Más y Menos Vendidos)")
    
    prod_counts = {}
    if os.path.exists(archivo_productos):
        df_p_all = pd.read_csv(archivo_productos)
        for _, row_p in df_p_all.iterrows():
            p_n = str(row_p['producto']).strip()
            prod_counts[p_n] = {"unidades": 0, "ingresos": 0.0, "precio": float(row_p['precio_venta'])}
            
    # Process json details from historical sales
    df_v_all = df_db[df_db['tipo'] == 'venta']
    for _, row_v in df_v_all.iterrows():
        p_det = row_v.get('productos_detalle', '')
        if p_det and isinstance(p_det, str) and p_det.startswith("["):
            try:
                items_det = json.loads(p_det)
                for it_d in items_det:
                    pname = str(it_d.get('producto')).strip()
                    u_cant = int(it_d.get('cantidad', 1))
                    u_subt = float(it_d.get('subtotal', 0.0))
                    if pname not in prod_counts:
                        prod_counts[pname] = {"unidades": 0, "ingresos": 0.0, "precio": float(it_d.get('precio_unitario', 0.0))}
                    prod_counts[pname]["unidades"] += u_cant
                    prod_counts[pname]["ingresos"] += u_subt
            except Exception:
                pass

    if prod_counts:
        df_rank = pd.DataFrame([
            {"producto": k, "unidades": v["unidades"], "ingresos": v["ingresos"]}
            for k, v in prod_counts.items()
        ])
        
        has_sales = df_rank['unidades'].max() > 0
        top_seller = df_rank.loc[df_rank['unidades'].idxmax()] if has_sales else None
        worst_seller = df_rank.loc[df_rank['unidades'].idxmin()] if not df_rank.empty else None
        
        col_rank1, col_rank2 = st.columns(2)
        with col_rank1:
            if top_seller is not None and top_seller['unidades'] > 0:
                st.success(f"🏆 **Producto Más Vendido:**\n\n### **{top_seller['producto']}**\n\n📦 **{top_seller['unidades']} unidades vendidas** | 💵 **${top_seller['ingresos']:,.2f} recaudados**")
            else:
                st.info("🏆 **Producto Más Vendido:**\n\nRegistra ventas desde el Punto de Venta en la barra lateral para generar métricas en tiempo real.")
                
        with col_rank2:
            if worst_seller is not None:
                st.warning(f"⚠️ **Producto Menos Vendido:**\n\n### **{worst_seller['producto']}**\n\n📦 **{worst_seller['unidades']} unidades vendidas** | 💡 *Sugerencia: Promociónalo o ajusta su precio.*")

        if has_sales:
            fig_rank = px.bar(
                df_rank.sort_values(by='unidades', ascending=True),
                y='producto', x='unidades', orientation='h',
                title="📊 Comparativa de Unidades Vendidas por Producto",
                labels={'unidades': 'Unidades Vendidas', 'producto': 'Producto'},
                color='unidades',
                color_continuous_scale=['#f59e0b', '#0ea5e9', '#10b981']
            )
            st.plotly_chart(fig_rank, use_container_width=True)

with tab_guia:
    st.markdown("### 🎓 Guía Financiera para no Financieros")
    st.caption("Todos los conceptos explicados en lenguaje del día a día:")

    col_ga, col_gb = st.columns(2)

    with col_ga:
        with st.container(border=True):
            st.markdown("#### 🎯 Punto de Equilibrio")
            st.markdown("Es la **meta mínima de venta** para cubrir tus compras y gastos. Si vendes justo esa cantidad, no ganas ni pierdes. Todo lo que vendas **por encima es ganancia líquida**.")

        with st.container(border=True):
            st.markdown("#### 💰 Ganancia Neta y Margen")
            st.markdown("El dinero que te queda limpio **después de pagar proveedores, renta, luz y sueldos**. El porcentaje te dice cuántos centavos de cada peso cobrado son tuya ganancia.")

        with st.container(border=True):
            st.markdown("#### 🛡️ Autonomía de Caja")
            st.markdown("Indica **cuántos días aguanta tu negocio pagando sus gastos** con el dinero de caja si dejas de vender hoy. Sirve para prever contingencias.")

        with st.container(border=True):
            st.markdown("#### 💎 VAN (Valor Actual Neto con Riesgo)")
            st.markdown("Calcula si el negocio te deja más dinero que el banco, **incluso descontando inflación y el riesgo de tu colonia/municipio**. Si es positivo, el negocio es viable.")

    with col_gb:
        with st.container(border=True):
            st.markdown("#### 📍 Prima de Riesgo por Ubicación")
            st.markdown("Poner un negocio en zona con delincuencia es más riesgoso que invertir en el banco. Por eso se exige un **porcentaje extra (%) de ganancia** para que valga el esfuerzo y el riesgo.")

        with st.container(border=True):
            st.markdown("#### 📦 Merma Estimada")
            st.markdown("Es el porcentaje de tus ventas o mercancía que **se pierde sin que lo notes**: frutas que se echan a perder, productos rotos, robo hormiga, errores de conteo. Se descuenta de tu ganancia para que el cálculo sea realista.")

        with st.container(border=True):
            st.markdown("#### 🔥 TIR (Tasa Interna de Retorno)")
            st.markdown("Es el **rendimiento real anual** que está generando tu negocio sobre lo que invertiste. Si supera tu meta (CETES + prima de riesgo), el negocio está funcionando mejor que tus alternativas.")

        with st.container(border=True):
            st.markdown("#### ⏱️ Tiempo de Recuperación (Payback)")
            st.markdown("El número estimado de **meses para recuperar toda la inversión** que pusiste al abrir tu negocio. Entre menos meses, más rápido recuperas tu dinero.")