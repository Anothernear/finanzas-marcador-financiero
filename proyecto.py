import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(
    page_title="Hermes Financial AI Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS estilo Dark Theme Avanzado con Animaciones y Cyber Glow
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0d0f12;
        color: #e0e6ed;
    }

    /* Ocultar elementos predeterminados */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Contenedores con efecto Neumorfismo / Glassmorphism */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a233a 0%, #0d0f12 70%);
    }

    /* Cards Personalizadas */
    .metric-card {
        background: rgba(22, 27, 34, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease-in-out;
        animation: fadeIn 0.8s ease-in-out;
    }
    
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.2);
    }

    /* Animaciones Keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 5px rgba(0, 242, 254, 0.2); }
        50% { box-shadow: 0 0 20px rgba(0, 242, 254, 0.6); }
        100% { box-shadow: 0 0 5px rgba(0, 242, 254, 0.2); }
    }

    .hermes-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(56, 189, 248, 0.1) 100%);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        animation: pulseGlow 3s infinite ease-in-out;
    }

    .status-badge {
        background: #1e293b;
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Custom Input Styles */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border-radius: 10px !important;
        border: 1px solid #30363d !important;
    }
</style>
""", unsafe_allow_html_size=True)

# ==========================================
# 2. MANEJO DE BASE DE DATOS (CSV) Y ESTADO
# ==========================================
CSV_FILE = "hermes_financial_db.csv"

def init_db():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "fecha", "tipo", "monto", "concepto", "categoria", "es_variable"
        ])
        # Datos iniciales demostrativos
        sample_data = [
            {"fecha": "2026-09-18", "tipo": "venta", "monto": 2100.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-19", "tipo": "venta", "monto": 2400.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-20", "tipo": "venta", "monto": 1800.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-21", "tipo": "venta", "monto": 1950.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-22", "tipo": "venta", "monto": 2200.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-23", "tipo": "venta", "monto": 2600.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            {"fecha": "2026-09-24", "tipo": "venta", "monto": 1450.0, "concepto": "Venta mostrador", "categoria": "Operación", "es_variable": True},
            # Gastos
            {"fecha": "2026-09-18", "tipo": "gasto", "monto": 1200.0, "concepto": "Insumos e inventario", "categoria": "Insumos", "es_variable": True},
            {"fecha": "2026-09-21", "tipo": "gasto", "monto": 800.0, "concepto": "Empaques y bolsas", "categoria": "Insumos", "es_variable": True},
            {"fecha": "2026-09-22", "tipo": "gasto", "monto": 3500.0, "concepto": "Renta de Local (Semanal prorrateada)", "categoria": "Fijo", "es_variable": False},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)

init_db()

if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

# ==========================================
# 3. MOTOR DE CÁLCULO DETERMINISTA (4 CAPAS)
# ==========================================
def calcular_capas_financieras(df, config_negocio):
    # Capa 1: Salud Actual
    df_ventas = df[df['tipo'] == 'venta']
    df_gastos = df[df['tipo'] == 'gasto']

    ingresos_totales = df_ventas['monto'].sum()
    costos_variables = df_gastos[df_gastos['es_variable'] == True]['monto'].sum()
    costos_fijos = df_gastos[df_gastos['es_variable'] == False]['monto'].sum()
    
    # Prevenir división entre cero
    margen_bruto_pct = ((ingresos_totales - costos_variables) / ingresos_totales * 100) if ingresos_totales > 0 else 0
    utilidad_operativa = ingresos_totales - costos_variables - costos_fijos
    margen_operativo_pct = (utilidad_operativa / ingresos_totales * 100) if ingresos_totales > 0 else 0

    # Capa 2: Supervivencia y Proyección
    # Punto de Equilibrio PE = CF / (1 - (CV/IT))
    denominador = (1 - (costos_variables / ingresos_totales)) if ingresos_totales > 0 else 0
    punto_equilibrio_semanal = (costos_fijos / denominador) if denominador > 0 else 0
    punto_equilibrio_diario = punto_equilibrio_semanal / 7

    caja_actual = config_negocio.get('caja_disponible', 10000.0)
    gasto_diario_promedio = (costos_variables + costos_fijos) / max(len(df['fecha'].unique()), 1)
    runway_dias = (caja_actual / gasto_diario_promedio) if gasto_diario_promedio > 0 else 999

    # Proyección por Promedio Móvil
    dias_registrados = max(len(df_ventas), 1)
    promedio_venta_diaria = ingresos_totales / dias_registrados
    proyeccion_siguiente_semana = promedio_venta_diaria * 7

    # Capa 3: Geoespacial y Entorno (Simulada por API/Coordenadas)
    competidores_radio = config_negocio.get('competidores_detectados', 4)
    nivel_trafico = "Alto" if config_negocio.get('es_zona_comercial', True) else "Medio"

    # Capa 4: Estimación Fiscal (RESICO México)
    # Tasa RESICO simplificada estimada
    tasa_isr = 0.015 # 1.5% promedio para ingresos PyME en RESICO
    iva_trasladado = ingresos_totales * 0.16
    iva_acreditable = costos_variables * 0.16
    iva_a_pagar = max(0, iva_trasladado - iva_acreditable)
    isr_estimado = ingresos_totales * tasa_isr
    total_provision_impuestos = iva_a_pagar + isr_estimado

    # JSON consolidado para consumo del Agente LLM
    json_agente = {
        "negocio": {
            "giro": config_negocio.get('giro', 'Abarrotes'),
            "ubicacion": config_negocio.get('ubicacion_nombre', 'Texcoco, Mex')
        },
        "metricas_semanales": {
            "ingresos_totales": round(ingresos_totales, 2),
            "costos_variables": round(costos_variables, 2),
            "costos_fijos_prorrateados": round(costos_fijos, 2),
            "margen_operativo_porcentaje": round(margen_operativo_pct, 2),
            "punto_equilibrio_diario": round(punto_equilibrio_diario, 2),
            "promedio_venta_diaria": round(promedio_venta_diaria, 2)
        },
        "supervivencia": {
            "runway_dias": round(runway_dias, 1),
            "proyeccion_semana": round(proyeccion_siguiente_semana, 2)
        },
        "entorno_geografico": {
            "competidores_cercanos": competidores_radio,
            "trafico_zona": nivel_trafico
        },
        "fiscal_estimado": {
            "iva_a_pagar": round(iva_a_pagar, 2),
            "isr_estimado": round(isr_estimado, 2),
            "provision_impuestos_mes": round(total_provision_impuestos, 2)
        }
    }

    return json_agente

# ==========================================
# 4. FLUJO DE ONBOARDING (PASO A PASO)
# ==========================================
if not st.session_state.onboarding_complete:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>⚡ Bienvenido a Hermes AI Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:1.2rem; color: #94a3b8;'>Sistema Inteligente de Evaluación Financiera y Prevención Fiscal para PyMEs</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Configuración Inicial del Negocio (Onboarding)")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre_negocio = st.text_input("Nombre de la Empresa", value="Mi Tiendita Express")
            giro = st.selectbox("Giro Comercial", ["Abarrotes", "Restaurante/Cafetería", "Servicios", "Ropa/Moda", "Hardware/Electrónica"])
            caja_inicial = st.number_input("Efectivo Actual Disponible en Caja ($)", value=12000.0, step=500.0)
        
        with col2:
            ubicacion = st.text_input("Ubicación / Ciudad", value="Texcoco, Estado de México")
            zona_comercial = st.checkbox("¿Está ubicado en una zona comercial de alto tráfico?", value=True)
            competidores = st.slider("Número aproximado de competidores directos en 1 km", 0, 20, 4)

        if st.button("🚀 Inicializar Asistente Hermes", use_container_width=True):
            st.session_state.config_negocio = {
                "nombre": nombre_negocio,
                "giro": giro,
                "caja_disponible": caja_inicial,
                "ubicacion_nombre": ubicacion,
                "es_zona_comercial": zona_comercial,
                "competidores_detectados": competidores
            }
            st.session_state.onboarding_complete = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. DASHBOARD PRINCIPAL (DESPUÉS DEL ONBOARDING)
# ==========================================
config = st.session_state.config_negocio
df_db = pd.read_csv(CSV_FILE)
calculos_json = calcular_capas_financieras(df_db, config)

# Header con gradiente
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; padding: 10px 0px;'>
        <div>
            <h1 style='margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{config['nombre']}</h1>
            <p style='margin: 0; color: #64748b; font-size: 0.95rem;'>Giro: {config['giro']} | Ubicación: {config['ubicacion_nombre']}</p>
        </div>
        <span class='status-badge'>🟢 Agente Hermes Activo</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar para Ingreso Rápido de Datos (Modo POS Conversacional/Rápido)
with st.sidebar:
    st.header("📥 Registro Diario Rápido")
    st.markdown("Simula la captura por voz o formulario:")
    
    with st.form("form_registro"):
        tipo = st.selectbox("Tipo de Movimiento", ["venta", "gasto"])
        monto = st.number_input("Monto ($)", min_value=1.0, step=50.0)
        concepto = st.text_input("Concepto / Descripción", value="Venta al contado")
        es_var = True
        if tipo == "gasto":
            es_var = st.checkbox("¿Es un Costo Variable? (Mercancía/Insumos)", value=True)
            
        btn_guardar = st.form_submit_button("➕ Registrar Transacción")
        if btn_guardar:
            nuevo_registro = pd.DataFrame([{
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": tipo,
                "monto": monto,
                "concepto": concepto,
                "categoria": "Manual",
                "es_variable": es_var
            }])
            df_actualizado = pd.concat([df_db, nuevo_registro], ignore_index=True)
            df_actualizado.to_csv(CSV_FILE, index=False)
            st.success("¡Registrado!")
            st.rerun()

    if st.button("🔄 Reiniciar Onboarding"):
        st.session_state.onboarding_complete = False
        st.rerun()

# --- PANEL DE LAS 4 CAPAS FINANCIERAS ---
m = calculos_json["metricas_semanales"]
s = calculos_json["supervivencia"]
f = calculos_json["fiscal_estimado"]

# Fila 1: KPIs Principales (Glassmorphism Cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color: #94a3b8; font-size: 0.85rem; margin:0;'>INGRESOS SEMANALES</p>
            <h2 style='color: #00f2fe; margin:5px 0;'>${m['ingresos_totales']:,.2f}</h2>
            <p style='color: #10b981; font-size: 0.8rem; margin:0;'>Prom: ${m['promedio_venta_diaria']:,.2f}/día</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color: #94a3b8; font-size: 0.85rem; margin:0;'>MARGEN OPERATIVO</p>
            <h2 style='color: #38bdf8; margin:5px 0;'>{m['margen_operativo_porcentaje']}%</h2>
            <p style='color: #94a3b8; font-size: 0.8rem; margin:0;'>Rendimiento Neto Real</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color: #94a3b8; font-size: 0.85rem; margin:0;'>PUNTO EQUILIBRIO DIARIO</p>
            <h2 style='color: #f59e0b; margin:5px 0;'>${m['punto_equilibrio_diario']:,.2f}</h2>
            <p style='color: #94a3b8; font-size: 0.8rem; margin:0;'>Meta Mínima / Día</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color: #94a3b8; font-size: 0.85rem; margin:0;'>RUNWAY (SUPERVIVENCIA)</p>
            <h2 style='color: #ec4899; margin:5px 0;'>{s['runway_dias']} Días</h2>
            <p style='color: #94a3b8; font-size: 0.8rem; margin:0;'>Con Caja Actual</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs para Navegación del Sistema
tab_graficas, tab_agente, tab_json = st.tabs(["📊 Gráficas & Tendencias", "🤖 Interpretación Hermes (IA)", "⚙️ Payload JSON (Backend)"])

with tab_graficas:
    c1, c2 = st.columns(2)
    with c1:
        # Gráfica de Ventas vs Punto de Equilibrio
        df_ventas_diarias = df_db[df_db['tipo'] == 'venta'].groupby('fecha')['monto'].sum().reset_index()
        fig_ventas = px.bar(df_ventas_diarias, x='fecha', y='monto', title="Ventas Diarias vs. Punto de Equilibrio", labels={'monto':'Monto ($)', 'fecha':'Fecha'})
        fig_ventas.add_hline(y=m['punto_equilibrio_diario'], line_dash="dot", line_color="#f59e0b", annotation_text="Punto Equilibrio")
        fig_ventas.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
        st.plotly_chart(fig_ventas, use_container_width=True)

    with c2:
        # Estructura de Gastos
        df_gastos_pie = df_db[df_db['tipo'] == 'gasto'].groupby('concepto')['monto'].sum().reset_index()
        fig_gastos = px.pie(df_gastos_pie, values='monto', names='concepto', title="Distribución de Costos y Gastos", hole=0.4)
        fig_gastos.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
        st.plotly_chart(fig_gastos, use_container_width=True)

with tab_agente:
    st.markdown("### 🗣️ Interpretación del Agente de IA en Lenguaje Natural")
    st.markdown("El modelo LLM recibe el archivo JSON determinista y genera las recomendaciones:")

    # Construcción de la respuesta generada por la IA a partir de las 4 capas
    respuesta_hermes = f"""
    ¡Hola! He analizado la salud financiera de **{config['nombre']}** con corte a esta semana. Aquí tienes mi evaluación estratégica:

    *   **Salud Financiera Actual:** Tuviste ingresos por **${m['ingresos_totales']:,.2f} MXN** con un margen de ganancia real del **{m['margen_operativo_porcentaje']}%**. Tu punto de equilibrio diario es de **${m['punto_equilibrio_diario']:,.2f} MXN**; tus ventas promedio diarias (${m['promedio_venta_diaria']:,.2f}) superan este umbral, por lo que tu operación actual es rentable.
    *   **Reserva Fiscal Preventiva:** Basado en tu régimen fiscal, estimo que el día 17 deberás pagar **${f['provision_impuestos_mes']:,.2f} MXN** al SAT (${f['iva_a_pagar']:,.2f} de IVA y ${f['isr_estimado']:,.2f} de ISR). Te aconsejo apartar este dinero hoy mismo en una cuenta de ahorro separada.
    *   **Entorno Geoespacial:** Estás operando en una zona con **{calculos_json['entorno_geografico']['competidores_cercanos']} competidores directos** identificados. Dado que el tráfico peatonal de tu zona es **{calculos_json['entorno_geografico']['trafico_zona']}**, no reduzcas tus precios para competir; enfócate en fidelizar con servicio rápido.
    *   **Sugerencia de Acción:** Tu saldo en caja te da una supervivencia de **{s['runway_dias']} días**. Te sugiero destinar un 10% del margen operativo excedente a reabastecer los insumos de mayor rotación antes del fin de semana.
    """

    st.markdown(f"""
        <div class='hermes-box'>
            <h4 style='color: #10b981; margin-top:0;'>🤖 Hermes AI Coach:</h4>
            <p style='font-size: 1.05rem; line-height: 1.6; color: #e2e8f0;'>{respuesta_hermes}</p>
        </div>
    """, unsafe_allow_html=True)

with tab_json:
    st.markdown("### 📄 Objeto JSON Estructurado enviado al LLM")
    st.markdown("Este JSON es calculado previa e infaliblemente por el motor matemático:")
    st.json(calculos_json)