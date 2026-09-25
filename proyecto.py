import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(
    page_title="Hermes Financial Coach",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0d0f12;
        color: #e0e6ed;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a233a 0%, #0d0f12 70%);
    }

    .metric-card {
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease-in-out;
    }
    
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.6);
        transform: translateY(-3px);
    }

    .badge-status {
        background: #1e293b;
        color: #10b981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .alert-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }

    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INICIALIZACIÓN DE BASE DE DATOS
# ==========================================
CSV_FILE = "hermes_financial_db.csv"

def cargar_y_validar_db():
    if not os.path.exists(CSV_FILE):
        # Generar datos demo iniciales solo si el archivo no existe en absoluto
        sample_data = [
            {"fecha": "2026-09-18", "tipo": "venta", "monto": 2100.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-19", "tipo": "venta", "monto": 2400.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-20", "tipo": "venta", "monto": 1800.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-21", "tipo": "venta", "monto": 1950.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-22", "tipo": "venta", "monto": 2200.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-23", "tipo": "venta", "monto": 2600.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-24", "tipo": "venta", "monto": 1450.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-18", "tipo": "gasto", "monto": 1200.0, "concepto": "Insumos y materia prima", "es_costo_directo": True},
            {"fecha": "2026-09-21", "tipo": "gasto", "monto": 800.0, "concepto": "Bolsas y empaques", "es_costo_directo": True},
            {"fecha": "2026-09-22", "tipo": "gasto", "monto": 875.0, "concepto": "Renta (Semanal)", "es_costo_directo": False},
            {"fecha": "2026-09-22", "tipo": "gasto", "monto": 300.0, "concepto": "Luz e Internet (Semanal)", "es_costo_directo": False},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        return df
    
    df = pd.read_csv(CSV_FILE)
    if 'es_costo_directo' not in df.columns:
        df['es_costo_directo'] = False
        df.to_csv(CSV_FILE, index=False)
        
    return df

if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

# ==========================================
# 3. CÁLCULO DE MÉTRICAS OPERATIVAS Y EVALUACIÓN DE INVERSIÓN (VPN, TIR, ROI)
# ==========================================
def calcular_capas_financieras(df, config):
    df_ventas = df[df['tipo'] == 'venta']
    df_gastos = df[df['tipo'] == 'gasto']

    dias_registrados = max(df['fecha'].nunique(), 1)
    
    ingresos_totales = df_ventas['monto'].sum()
    promedio_venta_diaria = ingresos_totales / dias_registrados if df_ventas['fecha'].nunique() > 0 else 0.0

    costos_variables = df_gastos[df_gastos['es_costo_directo'] == True]['monto'].sum()
    costos_fijos = df_gastos[df_gastos['es_costo_directo'] == False]['monto'].sum()

    margen_bruto_pct = ((ingresos_totales - costos_variables) / ingresos_totales * 100) if ingresos_totales > 0 else 0
    utilidad_operativa = ingresos_totales - costos_variables - costos_fijos
    margen_operativo_pct = (utilidad_operativa / ingresos_totales * 100) if ingresos_totales > 0 else 0

    denominador = (1 - (costos_variables / ingresos_totales)) if ingresos_totales > 0 else 0
    punto_equilibrio_semanal = (costos_fijos / denominador) if denominador > 0 else 0
    punto_equilibrio_diario = punto_equilibrio_semanal / max(dias_registrados, 1)

    caja_actual = config.get('caja_disponible', 10000.0)
    inversion_inicial = config.get('inversion_inicial', 10000.0)
    
    gasto_diario_promedio = (costos_variables + costos_fijos) / dias_registrados
    dias_cobertura_gastos = (caja_actual / gasto_diario_promedio) if gasto_diario_promedio > 0 else 999

    # --- MÉTRICAS DE EVALUACIÓN ECONÓMICA (VPN, TIR, ROI, PAYBACK) ---
    # ROI = (Utilidad Neta / Inversión Inicial) * 100
    roi = (utilidad_operativa / inversion_inicial * 100) if inversion_inicial > 0 else 0.0

    # Proyección mensual estimada basada en la utilidad media diaria registrada
    utilidad_diaria_promedio = utilidad_operativa / dias_registrados
    utilidad_mensual_est = utilidad_diaria_promedio * 30.0

    # Payback (Meses para recuperar la inversión inicial)
    payback_meses = (inversion_inicial / utilidad_mensual_est) if utilidad_mensual_est > 0 else 999.0

    # Flujo de caja proyectado a 12 meses para calcular VPN y TIR
    tasa_descuento_anual = config.get('tasa_descuento', 0.10) # 10% anual
    tasa_mensual = tasa_descuento_anual / 12.0
    
    flujos_mensuales = [utilidad_mensual_est] * 12
    
    # Cálculo de VPN (VAN)
    vpn = -inversion_inicial + sum([f / ((1 + tasa_mensual) ** t) for t, f in enumerate(flujos_mensuales, start=1)])

    # Cálculo de TIR anualizada
    flujos_totales = [-inversion_inicial] + flujos_mensuales
    try:
        tir_mensual = np.irr(flujos_totales) if hasattr(np, 'irr') else np.fsolve(lambda r: sum([f / ((1 + r)**i) for i, f in enumerate(flujos_totales)]), 0.1)[0]
        tir_anual = tir_mensual * 12 * 100 if not np.isnan(tir_mensual) else 0.0
    except:
        tir_anual = 0.0

    # Impuestos
    tasa_iva = config.get('tasa_iva', 0.16)
    tasa_isr = 0.015
    iva_a_pagar = max(0, (ingresos_totales * tasa_iva) - (costos_variables * tasa_iva))
    isr_estimado = ingresos_totales * tasa_isr

    return {
        "negocio": {
            "nombre": config.get('nombre', 'Mi Negocio'),
            "giro": config.get('giro', 'Abarrotes')
        },
        "metricas": {
            "ingresos_totales": round(ingresos_totales, 2),
            "costos_variables": round(costos_variables, 2),
            "costos_fijos": round(costos_fijos, 2),
            "margen_bruto_pct": round(margen_bruto_pct, 2),
            "margen_operativo_pct": round(margen_operativo_pct, 2),
            "punto_equilibrio_diario": round(punto_equilibrio_diario, 2),
            "promedio_venta_diaria": round(promedio_venta_diaria, 2),
            "utilidad_neta": round(utilidad_operativa, 2)
        },
        "evaluacion_economica": {
            "inversion_inicial": round(inversion_inicial, 2),
            "roi_pct": round(roi, 2),
            "vpn": round(vpn, 2),
            "tir_anual_pct": round(tir_anual, 2),
            "payback_meses": round(payback_meses, 1)
        },
        "caja": {
            "caja_disponible": round(caja_actual, 2),
            "dias_cobertura": round(dias_cobertura_gastos, 1)
        },
        "impuestos": {
            "total_apartado": round(iva_a_pagar + isr_estimado, 2)
        }
    }

# ==========================================
# 4. DIAGNÓSTICO DETERMINISTA
# ==========================================
def generar_diagnostico_determinista(m):
    met = m["metricas"]
    caja = m["caja"]
    econ = m["evaluacion_economica"]

    diagnostico = []
    acciones = []

    if met["promedio_venta_diaria"] < met["punto_equilibrio_diario"]:
        dif = met["punto_equilibrio_diario"] - met["promedio_venta_diaria"]
        diagnostico.append({
            "tipo": "alerta",
            "titulo": "🔴 Ventas por debajo del Punto de Equilibrio",
            "texto": f"Promedio actual: **${met['promedio_venta_diaria']:,.2f}/día**. Meta diaria mínima: **${met['punto_equilibrio_diario']:,.2f}**. Déficit diario: **${dif:,.2f}**."
        })
        acciones.append(f"⚡ Elevar ventas diarias en **${dif:,.2f}** para evitar pérdida operativa.")
    else:
        diagnostico.append({
            "tipo": "exito",
            "titulo": "🟢 Operación por Encima del Punto de Equilibrio",
            "texto": f"Las ventas promedio (**${met['promedio_venta_diaria']:,.2f}**) superan la meta diaria necesaria para cubrir costos (**${met['punto_equilibrio_diario']:,.2f}**)."
        })

    # Diagnóstico VPN
    if econ["vpn"] > 0:
        diagnostico.append({
            "tipo": "exito",
            "titulo": "📈 Proyecto Financieramente Viable (VPN Positivo)",
            "texto": f"El Valor Presente Neto (VPN) proyectado a 1 año es de **${econ['vpn']:,.2f}**, superando la tasa de descuento de referencia."
        })
    else:
        diagnostico.append({
            "tipo": "advertencia",
            "titulo": "📉 Valor Presente Neto (VPN) Negativo",
            "texto": f"El VPN actual es **${econ['vpn']:,.2f}**. El flujo de caja generado no alcanza a cubrir la rentabilidad esperada respecto a la inversión inicial."
        })

    return diagnostico, acciones

# ==========================================
# 5. FORMULARIO DE ONBOARDING
# ==========================================
if not st.session_state.onboarding_complete:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>⚡ Configuración del Negocio</h1>", unsafe_allow_html=True)

    with st.form("form_onboarding"):
        st.markdown("### 🏢 Datos Iniciales")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("1. Nombre comercial", value="Abarrotes El Güero")
            giro = st.selectbox("2. Giro comercial", ["Abarrotes / Tiendita", "Restaurante / Comida", "Ropa / Novedades", "Servicios / Taller", "Otro"])
            caja = st.number_input("3. Dinero actual en caja/cuenta ($)", value=10000.0, step=500.0)
        
        with col2:
            inversion_inicial = st.number_input("4. Inversión Inicial Total / Capital invertido ($)", value=25000.0, step=1000.0)
            tasa_descuento = st.number_input("5. Tasa de descuento / Rendimiento mínimo esperado anual (%)", value=10.0, step=0.5) / 100.0
            tasa_iva_input = st.selectbox("6. Tasa de IVA", options=[0.16, 0.08, 0.0])

        submit = st.form_submit_button("🚀 Iniciar Dashboard", use_container_width=True)
        if submit:
            st.session_state.config_negocio = {
                "nombre": nombre,
                "giro": giro,
                "caja_disponible": caja,
                "inversion_inicial": inversion_inicial,
                "tasa_descuento": tasa_descuento,
                "tasa_iva": tasa_iva_input
            }
            st.session_state.onboarding_complete = True
            st.rerun()
    st.stop()

# ==========================================
# 6. DASHBOARD PRINCIPAL
# ==========================================
config = st.session_state.config_negocio
df_db = cargar_y_validar_db()
calculos = calcular_capas_financieras(df_db, config)

st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h1 style='margin:0; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{config['nombre']}</h1>
            <p style='margin:0; color: #64748b;'>{config['giro']}</p>
        </div>
        <span class='badge-status'>🟢 Datos {'Reales' if len(df_db) > 0 else 'Vacíos'}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Lateral: Captura + Limpieza de datos
with st.sidebar:
    st.header("📥 Captura de Movimiento")
    with st.form("form_movimiento"):
        tipo_mov = st.selectbox("Tipo", ["Venta (Ingreso)", "Gasto (Salida)"])
        monto_input = st.number_input("Monto ($)", min_value=1.0, step=50.0)
        concepto_input = st.text_input("Concepto", value="Ventas del día")
        
        es_costo_dir = False
        if "Gasto" in tipo_mov:
            tipo_gasto_radio = st.radio("Clasificación:", ["Insumos / Mercancía (Variable)", "Renta, Servicios, Sueldos (Fijo)"])
            es_costo_dir = "Insumos" in tipo_gasto_radio

        btn_guardar = st.form_submit_button("➕ Guardar Registro")
        if btn_guardar:
            nuevo_reg = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "venta" if "Venta" in tipo_mov else "gasto",
                "monto": monto_input,
                "concepto": concepto_input,
                "es_costo_directo": es_costo_dir
            }
            df_actualizado = pd.concat([df_db, pd.DataFrame([nuevo_reg])], ignore_index=True)
            df_actualizado.to_csv(CSV_FILE, index=False)
            st.success("¡Registrado!")
            st.rerun()

    st.markdown("---")
    st.header("🧹 Datos e Iniciar de Cero")
    if st.button("🗑️ Vaciar todos los datos de prueba (CSV)"):
        # Vaciar el archivo CSV dejando solo el encabezado
        df_vacio = pd.DataFrame(columns=['fecha', 'tipo', 'monto', 'concepto', 'es_costo_directo'])
        df_vacio.to_csv(CSV_FILE, index=False)
        st.success("Base de datos limpiada. Ahora puedes ingresar transacciones reales.")
        st.rerun()

    if st.button("⚙️ Cambiar Parámetros de Inversión"):
        st.session_state.onboarding_complete = False
        st.rerun()

# --- MÉTRICAS OPERATIVAS ---
m = calculos["metricas"]
e = calculos["evaluacion_economica"]

st.subheader("📊 Operación Diaria")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Ventas Totales</p><h2 style='color:#00f2fe;margin:5px 0;'>${m['ingresos_totales']:,.2f}</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Promedio: ${m['promedio_venta_diaria']:,.2f}/día</p></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Ganancia Neta (%)</p><h2 style='color:#38bdf8;margin:5px 0;'>{m['margen_operativo_pct']}%</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Utilidad: ${m['utilidad_neta']:,.2f}</p></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Punto Equilibrio Diario</p><h2 style='color:#f59e0b;margin:5px 0;'>${m['punto_equilibrio_diario']:,.2f}</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Meta Mínima Diaria</p></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Cobertura de Caja</p><h2 style='color:#ec4899;margin:5px 0;'>{calculos['caja']['dias_cobertura']} Días</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Autonomía en caja</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MÉTRICAS ECONÓMICAS ---
st.subheader("📈 Evaluación Financiera y Rentabilidad (VPN, TIR, ROI)")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>ROI (Retorno sobre Inversión)</p><h2 style='color:#10b981;margin:5px 0;'>{e['roi_pct']}%</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Sobre Capital de ${e['inversion_inicial']:,.2f}</p></div>", unsafe_allow_html=True)

with col_e2:
    color_vpn = "#10b981" if e['vpn'] >= 0 else "#ef4444"
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Valor Presente Neto (VPN)</p><h2 style='color:{color_vpn};margin:5px 0;'>${e['vpn']:,.2f}</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Proyección 1 año (Tasa: {config['tasa_descuento']*100}%)</p></div>", unsafe_allow_html=True)

with col_e3:
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>TIR Anual Estimada</p><h2 style='color:#a855f7;margin:5px 0;'>{e['tir_anual_pct']}%</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Tasa Interna de Retorno</p></div>", unsafe_allow_html=True)

with col_e4:
    payback_text = f"{e['payback_meses']} Meses" if e['payback_meses'] < 100 else "N/A"
    st.markdown(f"<div class='metric-card'><p style='color:#94a3b8;font-size:0.8rem;margin:0;'>Recuperación (Payback)</p><h2 style='color:#06b6d4;margin:5px 0;'>{payback_text}</h2><p style='color:#64748b;font-size:0.75rem;margin:0;'>Tiempo retorno capital</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Pestañas
tab_diag, tab_graf, tab_tabla = st.tabs(["📢 Diagnóstico", "📊 Gráficas", "📜 Registros"])

with tab_diag:
    diagnosticos, acciones = generar_diagnostico_determinista(calculos)
    for item in diagnosticos:
        css = "alert-box" if item["tipo"] == "alerta" else ("warning-box" if item["tipo"] == "advertencia" else "success-box")
        st.markdown(f"<div class='{css}'><h4 style='margin:0;'>{item['titulo']}</h4><p style='margin:0;'>{item['texto']}</p></div>", unsafe_allow_html=True)

with tab_graf:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if not df_db.empty and 'venta' in df_db['tipo'].values:
            df_diario = df_db[df_db['tipo'] == 'venta'].groupby('fecha')['monto'].sum().reset_index()
            fig_bar = px.bar(df_diario, x='fecha', y='monto', title="Ventas Diarias vs Punto de Equilibrio")
            fig_bar.add_hline(y=m['punto_equilibrio_diario'], line_dash="dash", line_color="#f59e0b", annotation_text="Meta Mínima")
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún para graficar.")

    with col_g2:
        if not df_db.empty and 'gasto' in df_db['tipo'].values:
            df_gastos_pie = df_db[df_db['tipo'] == 'gasto'].groupby('concepto')['monto'].sum().reset_index()
            fig_pie = px.pie(df_gastos_pie, values='monto', names='concepto', title="Estructura de Costos", hole=0.4)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay gastos registrados aún para graficar.")

with tab_tabla:
    st.markdown("### 📋 Historial de Transacciones Registradas")
    st.dataframe(df_db, use_container_width=True)