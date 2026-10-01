import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Hermes · Marcador Financiero",
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
            {"fecha": hace6, "tipo": "venta", "monto": 2200.0, "concepto": "Ventas del día (Abarrotes)", "es_costo_directo": False, "metodo_pago": "💵 Efectivo"},
            {"fecha": hace5, "tipo": "venta", "monto": 2500.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo"},
            {"fecha": hace4, "tipo": "venta", "monto": 1900.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "🏦 Transferencia"},
            {"fecha": hace3, "tipo": "venta", "monto": 2800.0, "concepto": "Ventas del fin de semana", "es_costo_directo": False, "metodo_pago": "💳 Tarjeta Débito"},
            {"fecha": hace2, "tipo": "venta", "monto": 2100.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo"},
            {"fecha": ayer, "tipo": "venta", "monto": 2300.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💳 Tarjeta Crédito"},
            {"fecha": hoy, "tipo": "venta", "monto": 2400.0, "concepto": "Ventas del día", "es_costo_directo": False, "metodo_pago": "💵 Efectivo"},
            {"fecha": hace6, "tipo": "gasto", "monto": 1300.0, "concepto": "Compra de refrescos y botanas (Mercancía)", "es_costo_directo": True, "metodo_pago": ""},
            {"fecha": hace4, "tipo": "gasto", "monto": 1500.0, "concepto": "Compra de lácteos y embutidos (Mercancía)", "es_costo_directo": True, "metodo_pago": ""},
            {"fecha": hace2, "tipo": "gasto", "monto": 2000.0, "concepto": "Abarrotes secos y enlatados (Mercancía)", "es_costo_directo": True, "metodo_pago": ""},
            {"fecha": hoy, "tipo": "gasto", "monto": 1400.0, "concepto": "Frutas, verduras y pan (Mercancía)", "es_costo_directo": True, "metodo_pago": ""},
            {"fecha": hace5, "tipo": "gasto", "monto": 1200.0, "concepto": "Renta de local (Semanal)", "es_costo_directo": False, "metodo_pago": ""},
            {"fecha": hace3, "tipo": "gasto", "monto": 450.0, "concepto": "Luz eléctrica y refrigeración", "es_costo_directo": False, "metodo_pago": ""},
            {"fecha": ayer, "tipo": "gasto", "monto": 1400.0, "concepto": "Sueldo de ayudante (Semanal)", "es_costo_directo": False, "metodo_pago": ""},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        return df

    df = pd.read_csv(CSV_FILE)
    if 'es_costo_directo' not in df.columns:
        df['es_costo_directo'] = False
    if 'metodo_pago' not in df.columns:
        df['metodo_pago'] = ""
    df.to_csv(CSV_FILE, index=False)
    return df

def restaurar_datos_demo():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return cargar_y_validar_db()

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

st.markdown("---")

# ==========================================
# 8. BARRA LATERAL
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Registrar Dinero")
    st.caption("Apunta lo que entra y lo que sale:")

    with st.form("form_movimiento"):
        tipo_opcion = st.selectbox(
            "¿Qué movimiento vas a ingresar?",
            [
                "🟢 Venta (Dinero que cobraste)",
                "🟠 Compra de Mercancía / Insumos (Costo Variable)",
                "🔴 Gasto del Local / Negocio (Costo Fijo)"
            ]
        )

        monto_input = st.number_input("Monto en dinero ($)", min_value=1.0, step=50.0, value=150.0)

        if "Venta" in tipo_opcion:
            concepto_def = "Ventas del día"
            ayuda_concepto = "Ej: Ventas del día, pedido especial, etc."
            mostrar_pago = True
        elif "Mercancía" in tipo_opcion:
            concepto_def = "Compra de refrescos / abarrotes"
            ayuda_concepto = "Mercancía para revender o ingredientes."
            mostrar_pago = False
        else:
            concepto_def = "Renta del local"
            ayuda_concepto = "Gastos fijos: Renta, luz, sueldos fijos, internet."
            mostrar_pago = False

        concepto_input = st.text_input("¿En qué concepto o motivo?", value=concepto_def, help=ayuda_concepto)

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

        btn_guardar = st.form_submit_button("💾 Guardar Movimiento", use_container_width=True)
        if btn_guardar:
            es_venta = "Venta" in tipo_opcion
            es_costo_var = "Mercancía" in tipo_opcion
            nuevo_reg = {
                "fecha": fecha_input.strftime("%Y-%m-%d"),
                "tipo": "venta" if es_venta else "gasto",
                "monto": float(monto_input),
                "concepto": concepto_input.strip() if concepto_input.strip() else ("Venta" if es_venta else "Gasto"),
                "es_costo_directo": es_costo_var,
                "metodo_pago": metodo_pago_input if es_venta else ""
            }
            df_actualizado = pd.concat([df_db, pd.DataFrame([nuevo_reg])], ignore_index=True)
            df_actualizado.to_csv(CSV_FILE, index=False)
            st.success("✅ ¡Movimiento guardado!")
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Opciones del Negocio")

    if st.button("🔄 Cargar Datos Demo", use_container_width=True):
        restaurar_datos_demo()
        st.success("Datos demo restaurados.")
        st.rerun()

    if st.button("🗑️ Vaciar Registros (Empezar en 0)", use_container_width=True):
        df_vacio = pd.DataFrame(columns=['fecha', 'tipo', 'monto', 'concepto', 'es_costo_directo', 'metodo_pago'])
        df_vacio.to_csv(CSV_FILE, index=False)
        st.success("Base de datos limpia.")
        st.rerun()

    if st.button("✏️ Editar Parámetros y Riesgo de Zona", use_container_width=True):
        st.session_state.onboarding_complete = False
        st.rerun()

# ==========================================
# 9. SECCIÓN 1: RESUMEN DE VENTAS DEL DÍA
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

with col_v2:
    with st.container(border=True):
        st.metric(
            "💵 Ventas Totales (Período)",
            f"${m['ingresos_totales']:,.2f}",
            help="Suma total de todas las ventas registradas en la base de datos."
        )

with col_v3:
    with st.container(border=True):
        st.metric(
            "📊 Promedio Venta Diaria",
            f"${m['promedio_venta_diaria']:,.2f}",
            help="Promedio de ventas por día en los días que hay registros."
        )

with col_v4:
    ganancia_neta_color = "normal" if m['utilidad_neta'] >= 0 else "inverse"
    with st.container(border=True):
        st.metric(
            "💰 Ganancia Neta Total",
            f"${m['utilidad_neta']:,.2f}",
            delta=f"−${r['merma_estimada_pesos']:,.2f} merma",
            delta_color="inverse",
            help=f"Ventas − Costos − Gastos. La merma estimada (${r['merma_estimada_pesos']:,.2f}) es un riesgo adicional por la zona."
        )

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
tab_diag, tab_riesgo, tab_graf, tab_tabla, tab_guia = st.tabs([
    "📢 Diagnóstico y Consejos",
    "🛡️ Riesgo y Ubicación",
    "📊 Gráficas",
    "📜 Historial",
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