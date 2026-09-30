import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Hermes Financial Coach - Marcador Financiero & Riesgo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. BASE DE DATOS Y ESTADO
# ==========================================
CSV_FILE = "hermes_financial_db.csv"

# Catálogo de Riesgos por Ubicación / Entorno
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
        "descripcion": "Riesgo de extorsión, asaltos frecuentes o pérdida de mercancía. Requiere mayor tasa de descuento (exigencia de rentabilidad)."
    },
    "Zona Rural / Municipio Pequeño": {
        "riesgo_seguridad_pct": 2.5,
        "riesgo_merma_sugerida": 3.0,
        "descripcion": "Bajo delito callejero, pero riesgo de merma por tiempos de transporte y cortes de energía/servicios."
    }
}

def cargar_y_validar_db():
    if not os.path.exists(CSV_FILE):
        # Datos demo realistas
        sample_data = [
            {"fecha": "2026-09-24", "tipo": "venta", "monto": 2200.0, "concepto": "Ventas del día (Abarrotes)", "es_costo_directo": False},
            {"fecha": "2026-09-25", "tipo": "venta", "monto": 2500.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-26", "tipo": "venta", "monto": 1900.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-27", "tipo": "venta", "monto": 2800.0, "concepto": "Ventas del fin de semana", "es_costo_directo": False},
            {"fecha": "2026-09-28", "tipo": "venta", "monto": 2100.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-29", "tipo": "venta", "monto": 2300.0, "concepto": "Ventas del día", "es_costo_directo": False},
            {"fecha": "2026-09-30", "tipo": "venta", "monto": 2400.0, "concepto": "Ventas del día", "es_costo_directo": False},
            # Costos variables
            {"fecha": "2026-09-24", "tipo": "gasto", "monto": 1300.0, "concepto": "Compra de refrescos y botanas (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-26", "tipo": "gasto", "monto": 1500.0, "concepto": "Compra de lácteos y embutidos (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-28", "tipo": "gasto", "monto": 2000.0, "concepto": "Abarrotes secos y enlatados (Mercancía)", "es_costo_directo": True},
            {"fecha": "2026-09-30", "tipo": "gasto", "monto": 1400.0, "concepto": "Frutas, verduras y pan (Mercancía)", "es_costo_directo": True},
            # Costos fijos
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
        "nombre": "Abarrotes El Güero",
        "giro": "Abarrotes / Tiendita",
        "caja_disponible": 10000.0,
        "inversion_inicial": 25000.0,
        "tasa_descuento_base": 0.10,
        "ubicacion_estado": "Estado de México / Nezahualcóyotl",
        "tipo_zona": "Zona Urbana Comercial / Afluencia Alta",
        "riesgo_merma_pct": 3.5,
        "riesgo_seguridad_pct": 3.5
    }

# ==========================================
# 3. CÁLCULO FINANCIERO ROBUSTO (TIR REALISTA Y COMPARATIVA)
# ==========================================
def calcular_tir_anual_real(inversion, flujos_anuales_estimados):
    """Calcula la Tasa Interna de Retorno ANUAL REAL basada en flujos anuales."""
    if inversion <= 0 or flujos_anuales_estimados <= 0:
        return 0.0
    
    if (flujos_anuales_estimados * 3) <= inversion:
        return 0.0

    def npv_anual(r):
        if r <= -0.99:
            return float('inf')
        return -inversion + sum([flujos_anuales_estimados / ((1 + r) ** t) for t in range(1, 4)])

    low = 0.0001
    high = 20.0
    for _ in range(80):
        mid = (low + high) / 2.0
        val = npv_anual(mid)
        if abs(val) < 0.1:
            break
        if val > 0:
            low = mid
        else:
            high = mid
            
    return round(mid * 100, 1)

def calcular_capas_financieras(df, config):
    df_ventas = df[df['tipo'] == 'venta']
    df_gastos = df[df['tipo'] == 'gasto']

    dias_registrados = max(df['fecha'].nunique(), 1) if not df.empty else 1
    
    ingresos_totales = float(df_ventas['monto'].sum()) if not df_ventas.empty else 0.0
    promedio_venta_diaria = ingresos_totales / dias_registrados if ingresos_totales > 0 else 0.0

    costos_variables = float(df_gastos[df_gastos['es_costo_directo'] == True]['monto'].sum()) if not df_gastos.empty else 0.0
    costos_fijos = float(df_gastos[df_gastos['es_costo_directo'] == False]['monto'].sum()) if not df_gastos.empty else 0.0

    # Factores de Riesgo
    riesgo_merma_pct = config.get('riesgo_merma_pct', 3.5)
    riesgo_seguridad_pct = config.get('riesgo_seguridad_pct', 3.5)
    
    merma_estimada = ingresos_totales * (riesgo_merma_pct / 100.0)

    # 1. Utilidad sin riesgo
    utilidad_bruta_bruta = ingresos_totales - costos_variables
    margen_bruto_pct = (utilidad_bruta_bruta / ingresos_totales * 100) if ingresos_totales > 0 else 0.0
    
    utilidad_operativa_sin_riesgo = ingresos_totales - costos_variables - costos_fijos
    margen_operativo_sin_riesgo_pct = (utilidad_operativa_sin_riesgo / ingresos_totales * 100) if ingresos_totales > 0 else 0.0

    # 2. Utilidad LIMPIA DESCONTANDO RIESGO DE MERMA DEL LUGAR
    utilidad_neta_con_riesgo = max(0.0, utilidad_operativa_sin_riesgo - merma_estimada)
    margen_neto_con_riesgo_pct = (utilidad_neta_con_riesgo / ingresos_totales * 100) if ingresos_totales > 0 else 0.0

    # Punto de equilibrio
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
    
    gastos_totales = costos_variables + costos_fijos
    caja_actual = max(0.0, caja_inicial + ingresos_totales - gastos_totales)
    
    gasto_diario_promedio = gastos_totales / dias_registrados if gastos_totales > 0 else 0.0
    dias_cobertura_gastos = (caja_actual / gasto_diario_promedio) if gasto_diario_promedio > 0 else 999.0

    # Proyecciones Anuales con y sin Riesgo
    utilidad_diaria_con_riesgo = utilidad_neta_con_riesgo / dias_registrados
    utilidad_anual_con_riesgo = utilidad_diaria_con_riesgo * 365.0
    utilidad_mensual_con_riesgo = utilidad_diaria_con_riesgo * 30.0

    utilidad_diaria_sin_riesgo = utilidad_operativa_sin_riesgo / dias_registrados
    utilidad_anual_sin_riesgo = utilidad_diaria_sin_riesgo * 365.0
    utilidad_mensual_sin_riesgo = utilidad_diaria_sin_riesgo * 30.0

    # ROI Anualizado Realista
    roi_anual_pct = (utilidad_anual_con_riesgo / inversion_inicial * 100) if inversion_inicial > 0 else 0.0

    # Payback en Meses
    payback_meses = (inversion_inicial / utilidad_mensual_con_riesgo) if utilidad_mensual_con_riesgo > 0 else 999.0

    # TASA DE DESCUENTO
    tasa_base = config.get('tasa_descuento_base', 0.10)
    prima_zona = riesgo_seguridad_pct / 100.0
    tasa_descuento_total = tasa_base + prima_zona
    
    # VPN
    vpn_sin_riesgo = -inversion_inicial + sum([utilidad_mensual_sin_riesgo / ((1 + (tasa_base/12)) ** t) for t in range(1, 13)])
    vpn_ajustado_riesgo = -inversion_inicial + sum([utilidad_mensual_con_riesgo / ((1 + (tasa_descuento_total/12)) ** t) for t in range(1, 13)])
    
    impacto_riesgo_vpn = vpn_sin_riesgo - vpn_ajustado_riesgo

    # TIR Anualizada Realista
    tir_anual_pct = calcular_tir_anual_real(inversion_inicial, utilidad_anual_con_riesgo)
    tir_sin_riesgo_pct = calcular_tir_anual_real(inversion_inicial, utilidad_anual_sin_riesgo)

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
            "margen_operativo_pct": round(margen_neto_con_riesgo_pct, 1),
            "margen_sin_riesgo_pct": round(margen_operativo_sin_riesgo_pct, 1),
            "punto_equilibrio_diario": round(punto_equilibrio_diario, 2) if punto_equilibrio_diario != float('inf') else 0.0,
            "promedio_venta_diaria": round(promedio_venta_diaria, 2),
            "utilidad_neta": round(utilidad_neta_con_riesgo, 2),
            "utilidad_sin_riesgo": round(utilidad_operativa_sin_riesgo, 2),
            "utilidad_mensual_est": round(utilidad_mensual_con_riesgo, 2),
            "dias_registrados": dias_registrados
        },
        "riesgos": {
            "riesgo_merma_pct": riesgo_merma_pct,
            "riesgo_seguridad_pct": riesgo_seguridad_pct,
            "merma_estimada_pesos": round(merma_estimada, 2),
            "tasa_descuento_base_pct": round(tasa_base * 100, 1),
            "tasa_descuento_total_pct": round(tasa_descuento_total * 100, 1),
            "vpn_sin_riesgo": round(vpn_sin_riesgo, 2),
            "vpn_ajustado_riesgo": round(vpn_ajustado_riesgo, 2),
            "impacto_riesgo_vpn": round(impacto_riesgo_vpn, 2),
            "tir_sin_riesgo_pct": tir_sin_riesgo_pct
        },
        "evaluacion_economica": {
            "inversion_inicial": round(inversion_inicial, 2),
            "roi_anual_pct": round(roi_anual_pct, 1),
            "vpn": round(vpn_ajustado_riesgo, 2),
            "tir_anual_pct": tir_anual_pct,
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
    rsk = m["riesgos"]
    neg = m["negocio"]

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
            "titulo": "🔴 Alerta: Ventas por debajo del Punto de Equilibrio",
            "texto": f"Estás vendiendo **${met['promedio_venta_diaria']:,.2f}/día** y requieres **${met['punto_equilibrio_diario']:,.2f}/día** para cubrir costos. Te faltan **${dif:,.2f}/día**."
        })
    else:
        colchon = met["promedio_venta_diaria"] - met["punto_equilibrio_diario"]
        diagnostico.append({
            "tipo": "exito",
            "titulo": "🟢 ¡Excelente! Tu negocio genera ganancias operativas",
            "texto": f"Ventas promedio de **${met['promedio_venta_diaria']:,.2f}/día**, con colchón de ganancia de **${colchon:,.2f} diarios** sobre tu meta mínima."
        })

    # 2. Análisis de Riesgo por Ubicación
    if rsk["riesgo_seguridad_pct"] >= 5.0:
        diagnostico.append({
            "tipo": "alerta",
            "titulo": f"🛡️ Impacto de Ubicación: {neg['tipo_zona']}",
            "texto": f"Los riesgos del lugar le restan **${rsk['merma_estimada_pesos']:,.2f}** a tus ganancias por mermas y elevan la tasa exigida a **{rsk['tasa_descuento_total_pct']}% anual**. El valor de tu negocio se reduce en **${rsk['impacto_riesgo_vpn']:,.2f}** por el riesgo de la zona."
        })
    else:
        diagnostico.append({
            "tipo": "info",
            "titulo": f"📍 Perfil de Ubicación: {neg['tipo_zona']}",
            "texto": f"Riesgo de zona moderado (+{rsk['riesgo_seguridad_pct']}%). Rendimiento mínimo exigido al negocio: **{rsk['tasa_descuento_total_pct']}% anual**."
        })

    # 3. Viabilidad VPN
    if met["gastos_totales"] > 0:
        if econ["vpn"] > 0:
            diagnostico.append({
                "tipo": "exito",
                "titulo": "📈 Proyecto Financieramente Viable (Aún con Riesgo de Zona)",
                "texto": f"Incluso descontando los riesgos de tu localidad, el VPN es positivo (**${econ['vpn']:,.2f}**), superando con creces la tasa exigida del {rsk['tasa_descuento_total_pct']}%."
            })
        else:
            diagnostico.append({
                "tipo": "advertencia",
                "titulo": "📉 Rentabilidad insuficiente frente al riesgo del lugar",
                "texto": f"El VPN actual es de **${econ['vpn']:,.2f}**. Con los riesgos de la zona, la ganancia actual no compensa suficientemente el capital invertido."
            })

    return diagnostico

# ==========================================
# 5. ASISTENTE DE ONBOARDING CON CONFIGURACIÓN DE RIESGO
# ==========================================
if not st.session_state.onboarding_complete:
    st.title("⚡ Configuración del Negocio & Análisis de Riesgo")
    st.caption("Personaliza los datos de tu negocio y calibra los riesgos según el lugar donde operas.")
    st.write("")

    col_on1, col_on2 = st.columns(2)
    
    with col_on1:
        st.subheader("🏪 1. Identidad y Capital")
        nombre = st.text_input("¿Cómo se llama tu negocio?", value=st.session_state.config_negocio.get("nombre", "Abarrotes El Güero"))
        giro = st.selectbox(
            "Giro comercial:", 
            ["Abarrotes / Tiendita", "Restaurante / Cafetería / Comida", "Ropa / Calzado / Novedades", "Servicios / Taller / Oficio", "Farmacia / Salud", "Otro comercio"],
            index=0
        )
        caja = st.number_input("💵 Dinero actual disponible en caja/banco ($):", value=float(st.session_state.config_negocio.get("caja_disponible", 10000.0)), step=500.0)
        inversion_inicial = st.number_input("🏦 Inversión total realizada para arrancar ($):", value=float(st.session_state.config_negocio.get("inversion_inicial", 25000.0)), step=1000.0)
        tasa_base = st.number_input("🎯 Ganancia mínima esperada sin riesgo (CETES / Banco) (%):", value=float(st.session_state.config_negocio.get("tasa_descuento_base", 0.10) * 100), step=0.5) / 100.0

    with col_on2:
        st.subheader("📍 2. Ubicación y Factores de Riesgo del Entorno")
        ubicacion_estado = st.text_input("Estado o Municipio donde operas:", value=st.session_state.config_negocio.get("ubicacion_estado", "Estado de México / Nezahualcóyotl"))
        
        zonas_keys = list(PERFILES_RIESGO_ZONA.keys())
        current_zona = st.session_state.config_negocio.get("tipo_zona", zonas_keys[1])
        idx_zona = zonas_keys.index(current_zona) if current_zona in zonas_keys else 1
        
        def on_change_zona():
            sel_zona = st.session_state.sel_tipo_zona
            perfil = PERFILES_RIESGO_ZONA[sel_zona]
            st.session_state.slider_riesgo_seg = float(perfil["riesgo_seguridad_pct"])
            st.session_state.slider_riesgo_merma = float(perfil["riesgo_merma_sugerida"])

        tipo_zona = st.selectbox(
            "¿Cómo clasificarías la zona de tu local?",
            zonas_keys,
            index=idx_zona,
            key="sel_tipo_zona",
            on_change=on_change_zona
        )
        
        datos_zona = PERFILES_RIESGO_ZONA[tipo_zona]
        st.info(f"ℹ️ {datos_zona['descripcion']}")
        
        if "slider_riesgo_seg" not in st.session_state:
            st.session_state.slider_riesgo_seg = float(datos_zona["riesgo_seguridad_pct"])
        if "slider_riesgo_merma" not in st.session_state:
            st.session_state.slider_riesgo_merma = float(datos_zona["riesgo_merma_sugerida"])

        riesgo_seguridad_val = st.slider(
            "🚨 Prima de riesgo por inseguridad / entorno (% extra)",
            min_value=0.0, max_value=15.0, step=0.5,
            key="slider_riesgo_seg",
            help="Porcentaje extra de rendimiento que debe dar el negocio para justificar operar en esta zona."
        )
        
        riesgo_merma_val = st.slider(
            "📦 Estimación de merma o pérdidas (caducidad, robo hormiga, descompostura) (%)",
            min_value=0.0, max_value=10.0, step=0.5,
            key="slider_riesgo_merma",
            help="Porcentaje de tus ventas o mercancía que se pierde por robo hormiga, fruta echada a perder, etc."
        )

    st.write("")
    if st.button("🚀 Guardar y Ver Marcador Financiero", type="primary", use_container_width=True):
        st.session_state.config_negocio = {
            "nombre": nombre if nombre.strip() else "Mi Negocio",
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
# 6. DASHBOARD PRINCIPAL
# ==========================================
config = st.session_state.config_negocio
df_db = cargar_y_validar_db()
calculos = calcular_capas_financieras(df_db, config)
m = calculos["metricas"]
e = calculos["evaluacion_economica"]
c = calculos["caja"]
r = calculos["riesgos"]
n = calculos["negocio"]

# Encabezado
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(f"{config['nombre']}")
    st.caption(f"📂 **Giro:** {config['giro']} | 📍 **Ubicación:** {n['ubicacion_estado']} ({n['tipo_zona']}) | 📅 **Días analizados:** {m['dias_registrados']}")

with col_head2:
    st.success(f"🟢 {len(df_db)} Registros | 🛡️ Riesgo: +{r['riesgo_seguridad_pct']}%")

st.divider()

# ==========================================
# 7. BARRA LATERAL (ENTRADAS DE MOVIMIENTOS)
# ==========================================
with st.sidebar:
    st.header("📥 Registrar Dinero")
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
            ayuda_concepto = "Ejemplo: Ventas del día, pedidos especiales."
        elif "Mercancía" in tipo_opcion:
            concepto_def = "Compra de refrescos / abarrotes"
            ayuda_concepto = "Mercancía para revender o ingredientes."
        else:
            concepto_def = "Renta del local"
            ayuda_concepto = "Gastos fijos: Renta, luz, sueldos fijos, internet."

        concepto_input = st.text_input("¿En qué concepto o motivo?", value=concepto_def, help=ayuda_concepto)
        
        btn_guardar = st.form_submit_button("💾 Guardar Movimiento", type="primary", use_container_width=True)
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
            st.success("✅ ¡Movimiento guardado!")
            st.rerun()

    st.divider()
    st.subheader("⚙️ Opciones del Negocio")
    
    if st.button("🔄 Cargar Datos Demo", use_container_width=True):
        restaurar_datos_demo()
        st.success("Datos demo restaurados.")
        st.rerun()

    if st.button("🗑️ Vaciar Registros (Empezar en 0)", use_container_width=True):
        df_vacio = pd.DataFrame(columns=['fecha', 'tipo', 'monto', 'concepto', 'es_costo_directo'])
        df_vacio.to_csv(CSV_FILE, index=False)
        st.success("Base de datos limpia.")
        st.rerun()

    if st.button("✏️ Editar Parámetros y Riesgo de Zona", use_container_width=True):
        st.session_state.onboarding_complete = False
        st.rerun()

# ==========================================
# 8. SECCIÓN 1: SALUD DIARIA DEL NEGOCIO (TARJETAS NATIVAS)
# ==========================================
st.subheader("📊 1. ¿Cómo va tu Operación del Día a Día?")
st.caption("Monitorea cuánto entra, la ganancia limpia real descontando mermas del lugar y tu meta mínima.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💵 Ventas Totales Cobradas",
        value=f"${m['ingresos_totales']:,.2f}",
        delta=f"Promedio: ${m['promedio_venta_diaria']:,.2f} / día"
    )

with col2:
    st.metric(
        label="💰 Ganancia Neta Real",
        value=f"${m['utilidad_neta']:,.2f}",
        delta=f"-${r['merma_estimada_pesos']:,.0f} merma",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="🎯 Meta Mínima Diaria (P.E.)",
        value=f"${m['punto_equilibrio_diario']:,.2f}",
        delta="Venta para salir a mano"
    )

with col4:
    dias_txt = f"{c['dias_cobertura']} Días" if c['dias_cobertura'] < 900 else "Sin gastos reg."
    st.metric(
        label="🛡️ Autonomía de Caja",
        value=dias_txt,
        delta=f"Caja: ${c['caja_disponible']:,.2f}"
    )

st.write("")

# ==========================================
# 9. SECCIÓN 2: EVALUACIÓN ECONÓMICA REALISTA Y COMPARACIÓN DE RIESGO
# ==========================================
st.subheader("📈 2. Rentabilidad de tu Inversión (Ajustada al Riesgo del Lugar)")
st.caption(f"Tasa de rendimiento mínima exigida al negocio: **{r['tasa_descuento_total_pct']}% anual** (Tasa base {r['tasa_descuento_base_pct']}% + Prima de {n['tipo_zona']} +{r['riesgo_seguridad_pct']}%).")

col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
    st.metric(
        label="⚡ ROI Realista Anual",
        value=f"{e['roi_anual_pct']}% / año",
        delta=f"Capital: ${e['inversion_inicial']:,.2f}"
    )

with col_e2:
    st.metric(
        label="💎 VPN con Riesgo del Lugar",
        value=f"${e['vpn']:,.2f}",
        delta=f"-${r['impacto_riesgo_vpn']:,.0f} por riesgo",
        delta_color="inverse"
    )

with col_e3:
    st.metric(
        label="🔥 TIR Anual Realista",
        value=f"{e['tir_anual_pct']}%",
        delta=f"Meta: {r['tasa_descuento_total_pct']}%"
    )

with col_e4:
    payback_display = f"{e['payback_meses']} Meses" if e['payback_meses'] < 100 else "Indefinido"
    st.metric(
        label="⏱️ Tiempo de Retorno",
        value=payback_display,
        delta="Recuperación inversión"
    )

st.write("")

# ==========================================
# 10. PESTAÑAS DE ANÁLISIS, RIESGOS, GRÁFICAS Y GUÍA
# ==========================================
tab_diag, tab_riesgo, tab_graf, tab_tabla, tab_guia = st.tabs([
    "📢 Diagnóstico y Consejos", 
    "🛡️ Matriz de Riesgo y Ubicación",
    "📊 Gráficas Visuales", 
    "📜 Historial de Registros",
    "🎓 Guía Financiera Fácil"
])

with tab_diag:
    st.subheader("🧭 Diagnóstico Financiero")
    diagnosticos = generar_diagnostico_determinista(calculos)
    for item in diagnosticos:
        if item["tipo"] == "alerta":
            st.error(f"**{item['titulo']}**\n\n{item['texto']}")
        elif item["tipo"] == "advertencia":
            st.warning(f"**{item['titulo']}**\n\n{item['texto']}")
        elif item["tipo"] == "info":
            st.info(f"**{item['titulo']}**\n\n{item['texto']}")
        else:
            st.success(f"**{item['titulo']}**\n\n{item['texto']}")
    
    st.divider()
    st.subheader("💡 Consejos Prácticos para este Negocio:")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info("""
        **Para mitigar el riesgo del lugar:**
        1. **Fondo de contingencia local:** Mantén un colchón de efectivo en caja para emergencias de luz, desabasto o eventualidades de la zona.
        2. **Control estricto de mermas:** Anota los productos rotos o caducados para saber qué proveedores te generan más pérdidas.
        """)
    with col_c2:
        st.info("""
        **Para maximizar ganancias:**
        1. **Supera tu meta diaria:** Cada peso que vendes arriba de tu Punto de Equilibrio es ganancia líquida.
        2. **Monitorea tu TIR:** Si tu TIR supera el rendimiento exigido del lugar, el negocio justifica plenamente el esfuerzo.
        """)

with tab_riesgo:
    st.subheader("🛡️ Desglose del Impacto del Riesgo en tu Negocio")
    st.write(f"Aquí puedes ver exactamente **cuánto dinero y rentabilidad pierde tu negocio debido al lugar** ({n['ubicacion_estado']}):")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric(
            label="📦 Impacto en Merma / Pérdidas",
            value=f"-${r['merma_estimada_pesos']:,.2f}",
            delta=f"Sin merma: ${m['utilidad_sin_riesgo']:,.2f}"
        )
        st.caption(f"Pérdida directa ({r['riesgo_merma_pct']}% de ventas) por robo hormiga o fallas en {n['tipo_zona']}.")
        
    with col_r2:
        st.metric(
            label="📉 Impacto en el Valor del Negocio (VPN)",
            value=f"-${r['impacto_riesgo_vpn']:,.2f}",
            delta=f"VPN sin riesgo: ${r['vpn_sin_riesgo']:,.2f}"
        )
        st.caption(f"El valor cae por la prima de riesgo exigida ({r['tasa_descuento_total_pct']}%).")
        
    with col_r3:
        st.metric(
            label="🎯 Meta de Rentabilidad Exigida",
            value=f"{r['tasa_descuento_total_pct']}% anual",
            delta=f"TIR alcanzada: {e['tir_anual_pct']}%"
        )
        st.caption(f"Tasa Base ({r['tasa_descuento_base_pct']}%) + Sobretasa de Inseguridad (+{r['riesgo_seguridad_pct']}%).")

    st.divider()
    st.subheader("🗺️ Matriz de Riesgo por Tipo de Zona en México")
    df_zonas = pd.DataFrame([
        {"Tipo de Zona": k, "Prima de Riesgo": f"+{v['riesgo_seguridad_pct']}%", "Merma Promedio": f"{v['riesgo_merma_sugerida']}%", "Características": v['descripcion']}
        for k, v in PERFILES_RIESGO_ZONA.items()
    ])
    st.dataframe(df_zonas, use_container_width=True)

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
                labels={'fecha': 'Fecha', 'monto': 'Ventas ($)'}
            )
            if m['punto_equilibrio_diario'] > 0:
                fig_bar.add_hline(
                    y=m['punto_equilibrio_diario'], 
                    line_dash="dash", 
                    line_color="#d97706", 
                    annotation_text=f"Meta mínima (${m['punto_equilibrio_diario']:,.0f}/día)",
                    annotation_position="top right"
                )
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
                hole=0.45
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay gastos registrados aún para graficar.")

with tab_tabla:
    st.subheader("📋 Historial de Transacciones Registradas")
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
    st.subheader("🎓 Diccionario Financiero para no Financieros")
    st.write("Conceptos clave explicados con peras y manzanas:")
    
    col_g_a, col_g_b = st.columns(2)
    with col_g_a:
        with st.container(border=True):
            st.markdown("#### 🎯 Punto de Equilibrio")
            st.write("Es la **meta mínima de venta** para cubrir tus compras y gastos del negocio. Si vendes justo esa cantidad, no ganas ni pierdes ($0 de ganancia). Todo lo que vendas por encima es ganancia neta.")
        
        with st.container(border=True):
            st.markdown("#### 💰 Ganancia Neta Real")
            st.write("El dinero que te queda limpio en el bolsillo tras pagar proveedores, renta, luz, sueldos y **descontar las pérdidas de merma por la zona**.")
        
        with st.container(border=True):
            st.markdown("#### 🛡️ Autonomía de Caja")
            st.write("Indica **cuántos días resiste tu negocio pagando gastos** con el dinero de tu caja si dejas de vender hoy. Ayuda a prever contingencias.")
        
    with col_g_b:
        with st.container(border=True):
            st.markdown("#### 📍 Prima de Riesgo por Ubicación")
            st.write("Poner un negocio en una zona con delincuencia o difícil acceso es más riesgoso que invertir en una zona segura o en el banco. Por eso, se le exige ganar un **porcentaje extra (%)** para que valga la pena.")
        
        with st.container(border=True):
            st.markdown("#### 💎 VPN (Valor Presente Neto con Riesgo)")
            st.write("Calcula si el negocio te deja más dinero que el banco, **incluso descontando la inflación y el riesgo de tu colonia/municipio**. Si es positivo ($), el negocio es viable.")

        with st.container(border=True):
            st.markdown("#### ⏱️ Tiempo de Recuperación (Payback)")
            st.write("El número estimado de **meses para recuperar toda la inversión inicial** invertida al abrir tu negocio.")