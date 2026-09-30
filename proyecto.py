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
    page_title="Hermes Financial Coach - Marcador Financiero",
    page_icon="💡",
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
        padding: 18px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease-in-out;
        margin-bottom: 10px;
    }
    
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.6);
        transform: translateY(-2px);
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
        background: rgba(239, 68, 68, 0.12);
        border-left: 4px solid #ef4444;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.12);
        border-left: 4px solid #f59e0b;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }

    .success-box {
        background: rgba(16, 185, 129, 0.12);
        border-left: 4px solid #10b981;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }

    .info-box {
        background: rgba(56, 189, 248, 0.1);
        border-left: 4px solid #38bdf8;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 6px;
    }

    .guide-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS Y ESTADO
# ==========================================
CSV_FILE = "hermes_financial_db.csv"

def cargar_y_validar_db():
    if not os.path.exists(CSV_FILE):
        # Datos demo realistas y educativos
        sample_data = [
            {"fecha": "2026-09-24", "tipo": "venta", "monto": 2200.0, "concepto": "Ventas del día (Abarrotes)", "es_costo_directo": False},
            {"fecha": "2026-09-25", "tipo": "venta", "monto": 2500.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-26", "tipo": "venta", "monto": 1900.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-27", "tipo": "venta", "monto": 2800.0, "concepto": "Ventas del fin de semana", "es_costo_directo": False},
            {"fecha": "2026-09-28", "tipo": "venta", "monto": 2100.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-29", "tipo": "venta", "monto": 2300.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-30", "tipo": "venta", "monto": 2400.0, "concepto": "Ventas del día", "es_costo_directo": False},
            # Costos variables (mercancía vendida ~60% de venta)
            {"fecha": "2026-09-24", "tipo": "gasto", "monto": 1300.0, "concepto": "Compra de refrescos y botanas (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-26", "tipo": "gasto", "monto": 1500.0, "concepto": "Compra de lácteos y embutidos (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-28", "tipo": "gasto", "monto": 2000.0, "concepto": "Abarrotes secos y enlatados (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-30", "tipo": "gasto", "monto": 1400.0, "concepto": "Frutas, verduras y pan (Mercancía)", "es_costo_directo": True},
            # Costos fijos (semanales)
            {"fecha": "2026-09-25", "tipo": "gasto", "monto": 1200.0, "concepto": "Renta de local (Semanal)", "es_costo_directo": False},
            {"fecha": "2026-09-27", "tipo": "gasto", "monto": 450.0, "concepto": "Luz eléctrica y refrigeración", "es_costo_directo": False},
            {"fecha": "2026-09-29", "tipo": "gasto", "monto": 1400.0, "concepto": "Sueldo de ayudante (Semanal)", "es_costo_directo": False},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        return df
    
    df = pd.read_csv(CSV_FILE)
    if 'es_costo_directo' not in df.columns:
        df['es_costo_directo'] = False
        df.to_csv(CSV_FILE, index=False)
        
    return df

def restaurar_datos_demo():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return cargar_y_validar_db()

if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

if 'config_negocio' not in st.session_state:
    st.session_state.config_negocio = {
        "nombre": "Abarrotes El Pinguino",
        "giro": "Abarrotes / Tiendita",
        "caja_disponible": 10000.0,
        "inversion_inicial": 25000.0,
        "tasa_descuento": 0.10
    }

# ==========================================
# 3. CÁLCULO DE MÉTRICAS FINANCIERAS ROBUSTAS
# ==========================================
def calcular_tir_anual(inversion, flujo_mensual, meses=12):
    """Calcula la TIR mensual y anual con método numérico bisección/Newton sin librerías deprecadas."""
    if inversion <= 0 or flujo_mensual <= 0:
        return 0.0
    
    # Ecuación: -Inversión + sum(Flujo / (1 + r)^t) = 0
    # Si suma de flujos <= inversión, TIR es <= 0
    if (flujo_mensual * meses) <= inversion:
        return 0.0

    # Función objetivo para r (tasa mensual)
    def npv_rate(r):
        if r <= -1.0:
            return float('inf')
        return -inversion + sum([flujo_mensual / ((1 + r) ** t) for t in range(1, meses + 1)])

    # Búsqueda de raíz por bisección robusta entre 0% y 500% mensual
    low = 0.00001
    high = 5.0
    for _ in range(100):
        mid = (low + high) / 2.0
        val = npv_rate(mid)
        if abs(val) < 0.01:
            break
        if val > 0:
            low = mid
        else:
            high = mid
            
    tir_mensual = mid
    tir_anual_pct = ((1 + tir_mensual) ** 12 - 1) * 100 # Tasa efectiva anual
    return round(tir_anual_pct, 2)

def calcular_capas_financieras(df, config):
    df_ventas = df[df['tipo'] == 'venta']
    df_gastos = df[df['tipo'] == 'gasto']

    # Días activos con registros
    dias_registrados = max(df['fecha'].nunique(), 1) if not df.empty else 1
    
    ingresos_totales = float(df_ventas['monto'].sum()) if not df_ventas.empty else 0.0
    promedio_venta_diaria = ingresos_totales / dias_registrados if ingresos_totales > 0 else 0.0

    costos_variables = float(df_gastos[df_gastos['es_costo_directo'] == True]['monto'].sum()) if not df_gastos.empty else 0.0
    costos_fijos = float(df_gastos[df_gastos['es_costo_directo'] == False]['monto'].sum()) if not df_gastos.empty else 0.0

    utilidad_bruta = ingresos_totales - costos_variables
    margen_bruto_pct = (utilidad_bruta / ingresos_totales * 100) if ingresos_totales > 0 else 0.0
    
    utilidad_operativa = ingresos_totales - costos_variables - costos_fijos
    margen_operativo_pct = (utilidad_operativa / ingresos_totales * 100) if ingresos_totales > 0 else 0.0

    # Ratio de costo variable por peso vendido
    ratio_costo_variable = (costos_variables / ingresos_totales) if ingresos_totales > 0 else 0.0
    margen_contribucion_ratio = 1.0 - ratio_costo_variable

    # Punto de equilibrio del periodo y diario
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
    
    # Flujo de efectivo actual estimado = Caja inicial + Ventas - Gastos totales
    gastos_totales = costos_variables + costos_fijos
    caja_actual = max(0.0, caja_inicial + ingresos_totales - gastos_totales)
    
    gasto_diario_promedio = gastos_totales / dias_registrados if gastos_totales > 0 else 0.0
    dias_cobertura_gastos = (caja_actual / gasto_diario_promedio) if gasto_diario_promedio > 0 else 999.0

    # Proyección realista a 30 días basada en la media diaria registrada
    utilidad_diaria_promedio = utilidad_operativa / dias_registrados
    utilidad_mensual_est = max(0.0, utilidad_diaria_promedio * 30.0)

    # ROI acumulado del periodo = (Utilidad neta periodo / Inversión Inicial) * 100
    roi_pct = (utilidad_operativa / inversion_inicial * 100) if inversion_inicial > 0 else 0.0
    
    # ROI Anualizado proyectado
    roi_anual_pct = ((utilidad_diaria_promedio * 365.0) / inversion_inicial * 100) if inversion_inicial > 0 else 0.0

    # Payback (Meses necesarios para recuperar la inversión inicial con la ganancia mensual)
    if utilidad_mensual_est > 0:
        payback_meses = inversion_inicial / utilidad_mensual_est
    else:
        payback_meses = 999.0

    # VPN (VAN) a 12 meses: Descuenta las ganancias futuras mensuales al valor del dinero de hoy
    tasa_descuento_anual = config.get('tasa_descuento', 0.10)
    tasa_mensual = (1 + tasa_descuento_anual) ** (1/12) - 1 # Tasa efectiva mensual
    
    flujos_mensuales = [utilidad_mensual_est] * 12
    valor_presente_flujos = sum([f / ((1 + tasa_mensual) ** t) for t, f in enumerate(flujos_mensuales, start=1)])
    vpn = -inversion_inicial + valor_presente_flujos

    # TIR (Tasa Interna de Retorno anualizada)
    tir_anual = calcular_tir_anual(inversion_inicial, utilidad_mensual_est, meses=12)

    return {
        "negocio": {
            "nombre": config.get('nombre', 'Mi Negocio'),
            "giro": config.get('giro', 'Abarrotes / Tiendita')
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
            "dias_registrados": dias_registrados
        },
        "evaluacion_economica": {
            "inversion_inicial": round(inversion_inicial, 2),
            "roi_pct": round(roi_pct, 1),
            "roi_anual_pct": round(roi_anual_pct, 1),
            "vpn": round(vpn, 2),
            "tir_anual_pct": round(tir_anual, 1),
            "payback_meses": round(payback_meses, 1)
        },
        "caja": {
            "caja_disponible": round(caja_actual, 2),
            "caja_inicial": round(caja_inicial, 2),
            "dias_cobertura": round(dias_cobertura_gastos, 1) if dias_cobertura_gastos < 999 else 999
        }
    }

# ==========================================
# 4. DIAGNÓSTICO EN LENGUAJE SENCILLO
# ==========================================
def generar_diagnostico_determinista(m):
    met = m["metricas"]
    caja = m["caja"]
    econ = m["evaluacion_economica"]

    diagnostico = []

    # 1. Punto de equilibrio
    if met["costos_fijos"] == 0 and met["costos_variables"] == 0:
        diagnostico.append({
            "tipo": "advertencia",
            "titulo": "⚠️ Sin registros de gastos todavía",
            "texto": "Para que el marcador calcule tu punto de equilibrio y rentabilidad real, registra tus compras de mercancía y gastos fijos (renta, luz, etc.) en el panel lateral."
        })
    elif met["promedio_venta_diaria"] < met["punto_equilibrio_diario"]:
        dif = met["punto_equilibrio_diario"] - met["promedio_venta_diaria"]
        diagnostico.append({
            "tipo": "alerta",
            "titulo": "🔴 Alerta: Estás vendiendo por debajo de tus gastos mínimos",
            "texto": f"Estás vendiendo en promedio **${met['promedio_venta_diaria']:,.2f}/día**, pero necesitas vender al menos **${met['punto_equilibrio_diario']:,.2f}/día** solo para no perder dinero. Te faltan **${dif:,.2f} al día** para salir 'a mano'."
        })
    else:
        colchon = met["promedio_venta_diaria"] - met["punto_equilibrio_diario"]
        diagnostico.append({
            "tipo": "exito",
            "titulo": "🟢 ¡Excelente! Tu negocio genera ganancias operativas",
            "texto": f"Vendes un promedio de **${met['promedio_venta_diaria']:,.2f}/día**, superando tu meta mínima de **${met['punto_equilibrio_diario']:,.2f}/día**. Tienes un colchón de ganancia de **${colchon:,.2f} diarios**."
        })

    # 2. Diagnóstico de Rentabilidad / VPN
    if met["gastos_totales"] > 0:
        if econ["vpn"] > 0:
            diagnostico.append({
                "tipo": "exito",
                "titulo": "📈 Tu inversión vale la pena (VPN Positivo)",
                "texto": f"Con el ritmo actual de ganancias (**${met['utilidad_mensual_est']:,.2f}/mes**), recuperarás tu inversión de **${econ['inversion_inicial']:,.2f}** y generarás un valor extra equivalente a **${econ['vpn']:,.2f}** en un año."
            })
        else:
            diagnostico.append({
                "tipo": "advertencia",
                "titulo": "📉 Recuperación lenta de la inversión (VPN Negativo)",
                "texto": f"Con las ganancias actuales (**${met['utilidad_mensual_est']:,.2f}/mes**), el negocio tardará más de un año en devolverte los **${econ['inversion_inicial']:,.2f}** invertidos con el rendimiento mínimo esperado."
            })

    # 3. Diagnóstico de Salud de Caja
    if caja["dias_cobertura"] < 15 and met["gastos_totales"] > 0:
        diagnostico.append({
            "tipo": "alerta",
            "titulo": "⚠️ Precaución con la liquidez",
            "texto": f"Tu dinero disponible en caja te alcanza para **{caja['dias_cobertura']} días** de gastos promedio. Procura mantener siempre un fondo de emergencia de al menos 30 días."
        })
    elif caja["dias_cobertura"] >= 30 and met["gastos_totales"] > 0:
        diagnostico.append({
            "tipo": "exito",
            "titulo": "🛡️ Buena salud de efectivo",
            "texto": f"Tu dinero en caja te da una tranquilidad de **{caja['dias_cobertura']} días** de operación continua sin depender de ventas inmediatas."
        })

    return diagnostico

# ==========================================
# 5. ASISTENTE DE ONBOARDING (PASO A PASO)
# ==========================================
if not st.session_state.onboarding_complete:
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>⚡ Configuración Rápida de Tu Negocio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>No necesitas saber de finanzas. Solo cuéntanos un poco sobre tu negocio para calibrar tus indicadores.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_onboarding"):
        col_on1, col_on2 = st.columns(2)
        
        with col_on1:
            st.markdown("#### 🏪 1. Identidad de tu Negocio")
            nombre = st.text_input("¿Cómo se llama tu negocio o proyecto?", value="Abarrotes El Pinguino", help="El nombre visible de tu tiendita, taller, restaurante o comercio.")
            giro = st.selectbox(
                "¿Qué tipo de negocio tienes?", 
                ["Abarrotes / Tiendita", "Restaurante / Cafetería / Comida", "Ropa / Calzado / Novedades", "Servicios / Taller / Oficio", "Farmacia / Salud", "Otro comercio"]
            )
            caja = st.number_input(
                "💵 ¿Cuánto dinero en efectivo/cuenta tienes disponible hoy? ($)", 
                value=10000.0, 
                step=500.0,
                help="El dinero líquido con el que cuentas hoy en caja o en el banco para hacer frente a los gastos diarios."
            )
        
        with col_on2:
            st.markdown("#### 💰 2. Tu Inversión y Expectativas")
            inversion_inicial = st.number_input(
                "🏦 ¿Cuánto invertiste para arrancar el negocio? ($)", 
                value=25000.0, 
                step=1000.0,
                help="Suma lo que gastaste en refrigeradores, anaqueles, inventario inicial, depósitos y remodelación."
            )
            tasa_descuento_pct = st.number_input(
                "🎯 Ganancia mínima anual esperada sobre tu dinero (%)", 
                value=10.0, 
                step=1.0,
                help="Por ejemplo, 10% anual es lo que te daría una inversión segura en CETES o banco. Si tu negocio rinde más que esto, ¡es un éxito!"
            )
            st.caption("💡 *Nota: Usamos esta tasa para calcular si el negocio es más rentable que tener tu dinero guardado en el banco (VPN).*")

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Iniciar y Ver Mi Marcador Financiero", use_container_width=True)
        if submit:
            st.session_state.config_negocio = {
                "nombre": nombre if nombre.strip() else "Mi Negocio",
                "giro": giro,
                "caja_disponible": float(caja),
                "inversion_inicial": float(inversion_inicial) if inversion_inicial > 0 else 1000.0,
                "tasa_descuento": float(tasa_descuento_pct) / 100.0
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
m = calculos["metricas"]
e = calculos["evaluacion_economica"]
c = calculos["caja"]

# Encabezado
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"""
        <div>
            <h1 style='margin:0; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{config['nombre']}</h1>
            <p style='margin:0; color: #94a3b8; font-size: 1.05rem;'>📂 <b>Giro:</b> {config['giro']} | 📅 <b>Días analizados:</b> {m['dias_registrados']} días con operaciones</p>
        </div>
    """, unsafe_allow_html=True)

with col_head2:
    badge_color = "#10b981" if len(df_db) > 0 else "#f59e0b"
    badge_txt = f"🟢 {len(df_db)} Movimientos Registrados" if len(df_db) > 0 else "🟡 Sin Movimientos"
    st.markdown(f"<div style='text-align:right; margin-top:10px;'><span class='badge-status' style='color:{badge_color};'>{badge_txt}</span></div>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 7. BARRA LATERAL (ENTRADAS DE MOVIMIENTOS INTUITIVAS)
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Registrar Dinero")
    st.caption("Apunta lo que entra y lo que sale cada día:")
    
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
        
        # Sugerencias según tipo seleccionado
        if "Venta" in tipo_opcion:
            concepto_def = "Ventas del día"
            ayuda_concepto = "Ejemplo: Ventas del día, pedido especial, servicio a domicilio."
        elif "Mercancía" in tipo_opcion:
            concepto_def = "Compra de refrescos / abarrotes"
            ayuda_concepto = "Lo que compras para volver a vender o materia prima que se gasta con cada venta."
        else:
            concepto_def = "Renta del local"
            ayuda_concepto = "Gastos que pagas vendas o no vendas: Renta, luz, sueldos fijos, internet."

        concepto_input = st.text_input("¿En qué concepto o motivo?", value=concepto_def, help=ayuda_concepto)
        
        btn_guardar = st.form_submit_button("💾 Guardar Movimiento", use_container_width=True)
        if btn_guardar:
            es_venta = "Venta" in tipo_opcion
            es_costo_var = "Mercancía" in tipo_opcion
            
            nuevo_reg = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "venta" if es_venta else "gasto",
                "monto": float(monto_input),
                "concepto": concepto_input.strip() if concepto_input.strip() else ("Venta" if es_venta else "Gasto"),
                "es_costo_directo": es_costo_var
            }
            df_actualizado = pd.concat([df_db, pd.DataFrame([nuevo_reg])], ignore_index=True)
            df_actualizado.to_csv(CSV_FILE, index=False)
            st.success("✅ ¡Movimiento guardado exitosamente!")
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Opciones y Datos")
    
    if st.button("🔄 Cargar Datos de Ejemplo (Demo)", use_container_width=True):
        restaurar_datos_demo()
        st.success("Datos demo restaurados para explorar el sistema.")
        st.rerun()

    if st.button("🗑️ Vaciar Todos los Registros (Empezar en 0)", use_container_width=True):
        df_vacio = pd.DataFrame(columns=['fecha', 'tipo', 'monto', 'concepto', 'es_costo_directo'])
        df_vacio.to_csv(CSV_FILE, index=False)
        st.success("Base de datos limpia. Lista para tus datos 100% reales.")
        st.rerun()

    if st.button("✏️ Editar Parámetros del Negocio", use_container_width=True):
        st.session_state.onboarding_complete = False
        st.rerun()

# ==========================================
# 8. SECCIÓN 1: SALUD DIARIA DEL NEGOCIO (TARJETAS)
# ==========================================
st.markdown("### 📊 1. ¿Cómo va tu Operación del Día a Día?")
st.caption("Monitorea cuánto entra, cuánto te queda libre y cuál es tu meta mínima para no perder dinero.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>💵 Ventas Totales Cobradas</p>
            <h2 style='color:#00f2fe;margin:6px 0;'>${m['ingresos_totales']:,.2f}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Promedio: <b>${m['promedio_venta_diaria']:,.2f} / día</b></p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    color_ganancia = "#10b981" if m['utilidad_neta'] >= 0 else "#ef4444"
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>💰 Ganancia Neta Libre</p>
            <h2 style='color:{color_ganancia};margin:6px 0;'>${m['utilidad_neta']:,.2f}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Margen libre: <b>{m['margen_operativo_pct']}%</b> de tus ventas</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>🎯 Meta Mínima Diaria (P.E.)</p>
            <h2 style='color:#f59e0b;margin:6px 0;'>${m['punto_equilibrio_diario']:,.2f}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Venta al día para no ganar ni perder</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    color_caja = "#10b981" if c['dias_cobertura'] > 20 else ("#f59e0b" if c['dias_cobertura'] > 7 else "#ef4444")
    dias_txt = f"{c['dias_cobertura']} Días" if c['dias_cobertura'] < 900 else "Sin gastos reg."
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>🛡️ Autonomía de Caja</p>
            <h2 style='color:{color_caja};margin:6px 0;'>{dias_txt}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Dinero en caja: <b>${c['caja_disponible']:,.2f}</b></p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 9. SECCIÓN 2: EVALUACIÓN ECONÓMICA DE TU INVERSIÓN
# ==========================================
st.markdown("### 📈 2. Rentabilidad de tu Inversión (¿Conviene este Negocio?)")
st.caption("Indicadores financieros explicados para evaluar si el capital que metiste está rindiendo frutos.")

col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
    color_roi = "#10b981" if e['roi_anual_pct'] > 0 else "#ef4444"
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>⚡ ROI (Rendimiento Anual)</p>
            <h2 style='color:{color_roi};margin:6px 0;'>{e['roi_anual_pct']}% / año</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Capital invertido: <b>${e['inversion_inicial']:,.2f}</b></p>
        </div>
    """, unsafe_allow_html=True)

with col_e2:
    color_vpn = "#10b981" if e['vpn'] >= 0 else "#ef4444"
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>💎 Valor Presente Neto (VPN)</p>
            <h2 style='color:{color_vpn};margin:6px 0;'>${e['vpn']:,.2f}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Ganancia neta descontando inflación (1 año)</p>
        </div>
    """, unsafe_allow_html=True)

with col_e3:
    color_tir = "#10b981" if e['tir_anual_pct'] > (config['tasa_descuento']*100) else "#f59e0b"
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>🔥 TIR (Tasa Real de Retorno)</p>
            <h2 style='color:{color_tir};margin:6px 0;'>{e['tir_anual_pct']}%</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Rendimiento anual del dinero invertido</p>
        </div>
    """, unsafe_allow_html=True)

with col_e4:
    payback_display = f"{e['payback_meses']} Meses" if e['payback_meses'] < 100 else "Indefinido"
    st.markdown(f"""
        <div class='metric-card'>
            <p style='color:#94a3b8;font-size:0.85rem;margin:0;font-weight:600;'>⏱️ Tiempo de Recuperación</p>
            <h2 style='color:#06b6d4;margin:6px 0;'>{payback_display}</h2>
            <p style='color:#64748b;font-size:0.75rem;margin:0;'>Para recuperar tu inversión inicial</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 10. PESTAÑAS DE ANÁLISIS, GRÁFICAS Y GUÍA
# ==========================================
tab_diag, tab_graf, tab_tabla, tab_guia = st.tabs([
    "📢 Diagnóstico y Consejos", 
    "📊 Gráficas Visuales", 
    "📜 Historial de Registros",
    "🎓 Guía Financiera Fácil"
])

with tab_diag:
    st.markdown("#### 🧭 ¿Qué significa lo que ves en pantalla?")
    diagnosticos = generar_diagnostico_determinista(calculos)
    for item in diagnosticos:
        css = "alert-box" if item["tipo"] == "alerta" else ("warning-box" if item["tipo"] == "advertencia" else "success-box")
        st.markdown(f"<div class='{css}'><h4 style='margin:0 0 5px 0;'>{item['titulo']}</h4><p style='margin:0;'>{item['texto']}</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 💡 Consejos Prácticos para tu Negocio:")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info("""
        **Para subir tus ganancias:**
        1. **Registra todos los costos de mercancía:** Si compras 10 cajas de leche, anótalas como *Compra de Mercancía* para saber exactamente cuánto le ganas a cada producto.
        2. **Controla tus costos fijos:** La renta y la luz se pagan vendas o no. Entre más bajos sean, menor será tu meta mínima diaria.
        """)
    with col_c2:
        st.info("""
        **Para cuidar tu dinero:**
        1. **Separa tu dinero personal del negocio:** No tomes dinero de la caja para gastos personales sin anotarlo.
        2. **Mantén tu fondo de caja:** Busca tener guardado lo equivalente a por lo menos 1 mes de renta y sueldos.
        """)

with tab_graf:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if not df_db.empty and 'venta' in df_db['tipo'].values:
            df_diario = df_db[df_db['tipo'] == 'venta'].groupby('fecha')['monto'].sum().reset_index()
            fig_bar = px.bar(
                df_diario, 
                x='fecha', 
                y='monto', 
                title="Ventas Diarias vs Meta Mínima de Equilibrio",
                labels={'fecha': 'Fecha', 'monto': 'Ventas ($)'},
                color_discrete_sequence=['#00f2fe']
            )
            if m['punto_equilibrio_diario'] > 0:
                fig_bar.add_hline(
                    y=m['punto_equilibrio_diario'], 
                    line_dash="dash", 
                    line_color="#f59e0b", 
                    annotation_text=f"Meta mínima (${m['punto_equilibrio_diario']:,.0f}/día)",
                    annotation_position="top right"
                )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún para graficar.")

    with col_g2:
        if not df_db.empty and 'gasto' in df_db['tipo'].values:
            df_gastos_pie = df_db[df_db['tipo'] == 'gasto'].groupby('concepto')['monto'].sum().reset_index()
            fig_pie = px.pie(
                df_gastos_pie, 
                values='monto', 
                names='concepto', 
                title="¿En qué se está yendo el dinero? (Estructura de Gastos)",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay gastos registrados aún para graficar.")

with tab_tabla:
    st.markdown("### 📋 Historial de Transacciones Registradas")
    if not df_db.empty:
        df_mostrar = df_db.copy()
        df_mostrar['tipo_legible'] = df_mostrar.apply(
            lambda row: "🟢 Venta" if row['tipo'] == 'venta' else ("🟠 Mercancía (Variable)" if row.get('es_costo_directo', False) else "🔴 Gasto Fijo"),
            axis=1
        )
        df_mostrar = df_mostrar[['fecha', 'tipo_legible', 'concepto', 'monto']]
        df_mostrar.columns = ['Fecha', 'Tipo de Movimiento', 'Concepto / Motivo', 'Monto ($)']
        st.dataframe(df_mostrar.sort_values(by='Fecha', ascending=False), use_container_width=True)
    else:
        st.info("Aún no tienes movimientos registrados.")

with tab_guia:
    st.markdown("### 🎓 Diccionario Financiero para no Financieros")
    st.markdown("Aquí te explicamos de manera simple qué significa cada número:")
    
    col_g_a, col_g_b = st.columns(2)
    with col_g_a:
        st.markdown("""
        <div class='guide-card'>
            <h4 style='color:#00f2fe; margin-top:0;'>🎯 Punto de Equilibrio</h4>
            <p>Es la <b>meta mínima de venta</b> que necesitas alcanzar para cubrir todos tus gastos y compras. Si vendes justo esa cantidad, no ganas ni pierdes ($0 pesos de ganancia). Todo lo que vendas por encima de esta meta ya es tu ganancia neta.</p>
        </div>
        
        <div class='guide-card'>
            <h4 style='color:#38bdf8; margin-top:0;'>💰 Ganancia Neta y Margen</h4>
            <p>Es el dinero real que te queda en el bolsillo después de pagar a proveedores de mercancía, renta, luz y ayudantes. El porcentaje indica cuántos centavos de ganancia te quedan limpios por cada peso que vendes.</p>
        </div>
        
        <div class='guide-card'>
            <h4 style='color:#ec4899; margin-top:0;'>🛡️ Autonomía de Caja</h4>
            <p>Indica <b>cuántos días podrías sobrevivir pagando tus gastos</b> con el dinero que tienes en la caja si hoy mismo dejaras de vender. Te ayuda a saber si tienes suficiente colchón ante emergencias.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_g_b:
        st.markdown("""
        <div class='guide-card'>
            <h4 style='color:#10b981; margin-top:0;'>⚡ ROI (Retorno sobre Inversión)</h4>
            <p>Te dice qué porcentaje de la inversión original estás recuperando al año gracias a las ganancias del negocio. Si invertiste $25,000 y ganas $10,000 al año, tu ROI es del 40% anual.</p>
        </div>
        
        <div class='guide-card'>
            <h4 style='color:#10b981; margin-top:0;'>💎 VPN (Valor Presente Neto)</h4>
            <p>Compara si ganarás más dinero con este negocio que si hubieras metido tu capital al banco o en CETES. Si el <b>VPN es positivo ($)</b>, el negocio sí conviene económicamente.</p>
        </div>

        <div class='guide-card'>
            <h4 style='color:#06b6d4; margin-top:0;'>⏱️ Tiempo de Recuperación (Payback)</h4>
            <p>El número estimado de <b>meses que tardarás en recuperar toda la inversión inicial</b> que hiciste para montar tu negocio.</p>
        </div>
        """, unsafe_allow_html=True)