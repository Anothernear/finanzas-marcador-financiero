import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import uuid
import os
import base64
import re
import unicodedata
from datetime import datetime, date

BASE_DIR_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_IMAGENES = "imagenes_productos"


def nombre_a_ruta_imagen(nombre: str, ext: str = "png") -> str:
    """Convierte el nombre de un producto en una ruta limpia dentro de imagenes_productos/."""
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    if not slug:
        slug = "producto"
    return f"{CARPETA_IMAGENES}/{slug}.{ext}"


def resolver_imagen_producto(ruta_imagen: str, nombre: str, categoria: str = "") -> str:
    """
    Resuelve la imagen de un producto para que funcione tanto en local como en Streamlit.io:
    1. Si 'ruta_imagen' es una URL web (https://...), la devuelve directo.
    2. Si 'ruta_imagen' es un archivo local existente en 'imagenes_productos/' (.png, .jpg, .jpeg, .webp, .svg),
       lo lee y codifica en Base64 Data URI para que Streamlit.io lo muestre sin errores en tablas y tarjetas.
    3. Si el archivo aún no existe en la carpeta, usa la ilustración SVG automática como respaldo.
    """
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)
    ruta_limpia = str(ruta_imagen).strip() if pd.notna(ruta_imagen) else ""

    if ruta_limpia.startswith(("http://", "https://", "data:image/")):
        return ruta_limpia

    # Buscar el archivo en la ruta indicada o con extensiones comunes (.png, .jpg, .jpeg, .webp, .svg)
    candidatos = [ruta_limpia] if ruta_limpia else []
    base_sin_ext = os.path.splitext(nombre_a_ruta_imagen(nombre))[0]
    for ext in ["png", "jpg", "jpeg", "webp", "svg"]:
        cand = f"{base_sin_ext}.{ext}"
        if cand not in candidatos:
            candidatos.append(cand)

    for cand in candidatos:
        if not cand:
            continue
        rutas_posibles = [cand, os.path.join(BASE_DIR_PROYECTO, cand)]
        for ruta_real in rutas_posibles:
            if os.path.isfile(ruta_real):
                ext_real = os.path.splitext(ruta_real)[1].lower().lstrip(".")
                mime = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "webp": "image/webp",
                    "svg": "image/svg+xml"
                }.get(ext_real, "image/png")
                try:
                    with open(ruta_real, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")
                    return f"data:{mime};base64,{b64}"
                except Exception:
                    pass

    return generar_svg_producto(nombre, categoria)


# ==============================================================================
# 1. GENERADOR DE FOTOS SVG Y ENRIQUECIMIENTO DE CATÁLOGO DE PRODUCTOS
# ==============================================================================
def generar_svg_producto(nombre: str, categoria: str = "") -> str:
    """Genera una ilustración SVG nítida en formato data URI para cada producto."""
    n_low = str(nombre).lower()
    cat_low = str(categoria).lower()

    # Selección de ícono y paleta de colores intuitiva según producto
    if "coca" in n_low or "refresco" in n_low:
        emoji, bg1, bg2, badge = "🥤", "#fee2e2", "#ef4444", "BEBIDA"
    elif "cerveza" in n_low or "corona" in n_low:
        emoji, bg1, bg2, badge = "🍺", "#fef3c7", "#f59e0b", "BEBIDA"
    elif "leche" in n_low or "lácteo" in cat_low or "lacteo" in cat_low:
        emoji, bg1, bg2, badge = "🥛", "#e0f2fe", "#0284c7", "LÁCTEOS"
    elif "gansito" in n_low or "pastel" in n_low:
        emoji, bg1, bg2, badge = "🧁", "#fce7f3", "#db2777", "SNACK"
    elif "sabritas" in n_low or "papas" in n_low or "snack" in cat_low:
        emoji, bg1, bg2, badge = "🍟", "#fef9c3", "#ca8a04", "SNACK"
    elif "frijol" in n_low or "arroz" in n_low or "semilla" in n_low:
        emoji, bg1, bg2, badge = "🫘", "#ffedd5", "#ea580c", "ABARROTES"
    elif "huevo" in n_low:
        emoji, bg1, bg2, badge = "🥚", "#fef3c7", "#d97706", "ABARROTES"
    elif "atún" in n_low or "atun" in n_low or "lata" in n_low:
        emoji, bg1, bg2, badge = "🥫", "#e0e7ff", "#4f46e5", "ENLATADOS"
    elif "tortilla" in n_low or "maíz" in n_low:
        emoji, bg1, bg2, badge = "🫓", "#fef9c3", "#eab308", "ALIMENTOS"
    elif "concha" in n_low:
        emoji, bg1, bg2, badge = "🥯", "#fae8ff", "#9333ea", "PANADERÍA"
    elif "cuerno" in n_low or "croissant" in n_low:
        emoji, bg1, bg2, badge = "🥐", "#ffedd5", "#d97706", "PANADERÍA"
    elif "baguette" in n_low:
        emoji, bg1, bg2, badge = "🥖", "#fef3c7", "#b45309", "PANADERÍA"
    elif "bolillo" in n_low or "telera" in n_low or "pan" in n_low or "panadería" in cat_low:
        emoji, bg1, bg2, badge = "🍞", "#ffedd5", "#c2410c", "PANADERÍA"
    else:
        emoji, bg1, bg2, badge = "📦", "#f1f5f9", "#475569", (categoria[:10].upper() if categoria else "PRODUCTO")

    titulo_corto = str(nombre)[:18] + ("..." if len(str(nombre)) > 18 else "")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="160" height="120" viewBox="0 0 160 120">
        <defs>
            <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{bg1}"/>
                <stop offset="100%" stop-color="#ffffff"/>
            </linearGradient>
        </defs>
        <rect width="156" height="116" x="2" y="2" rx="14" fill="url(#g)" stroke="{bg2}" stroke-width="2"/>
        <rect x="8" y="8" width="68" height="18" rx="9" fill="{bg2}"/>
        <text x="42" y="20" font-family="Arial, sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">{badge}</text>
        <text x="80" y="72" font-family="Segoe UI Emoji, Apple Color Emoji, sans-serif" font-size="42" text-anchor="middle">{emoji}</text>
        <text x="80" y="105" font-family="Arial, sans-serif" font-size="10.5" font-weight="bold" fill="#1e293b" text-anchor="middle">{titulo_corto}</text>
    </svg>"""
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def asegurar_columnas_productos(df_prod: pd.DataFrame, tc_usd: float = 19.85, tc_eur: float = 21.40) -> pd.DataFrame:
    """Garantiza que el DataFrame de productos tenga foto, código de barras, punto de reorden y moneda/tipo de cambio."""
    if df_prod is None or df_prod.empty:
        return pd.DataFrame(columns=["producto", "categoria", "codigo_barras", "moneda_origen", "costo_moneda_origen", "costo_compra", "precio_venta", "inventario", "punto_reorden", "unidades_vendidas_hoy", "foto_url", "Estado Stock"])

    df = df_prod.copy().reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]
    if "producto" not in df.columns:
        df["producto"] = "Nuevo Producto"
    df["producto"] = df["producto"].fillna("Nuevo Producto").astype(str)
    if "categoria" not in df.columns:
        df["categoria"] = "General"
    else:
        df["categoria"] = df["categoria"].fillna("General").astype(str)

    df["costo_compra"] = pd.to_numeric(df.get("costo_compra", 10.0), errors="coerce").fillna(10.0)
    df["precio_venta"] = pd.to_numeric(df.get("precio_venta", 15.0), errors="coerce").fillna(15.0)
    df["inventario"] = pd.to_numeric(df.get("inventario", 50), errors="coerce").fillna(0).astype(int)
    df["unidades_vendidas_hoy"] = pd.to_numeric(df.get("unidades_vendidas_hoy", 0), errors="coerce").fillna(0).astype(int)

    # Código de barras EAN-13 simulado por producto (siempre como string para compatibilidad con TextColumn)
    if "codigo_barras" not in df.columns:
        df["codigo_barras"] = [f"75010553{1000 + i:04d}" for i in range(len(df))]
    else:
        df["codigo_barras"] = df["codigo_barras"].astype(str)
        for i in range(len(df)):
            val = str(df.at[i, "codigo_barras"]).strip().replace(".0", "")
            if not val or val == "nan":
                df.at[i, "codigo_barras"] = f"75010553{1000 + i:04d}"
            else:
                df.at[i, "codigo_barras"] = val
    df["codigo_barras"] = df["codigo_barras"].astype(str)

    # Punto de reorden sugerido según categoría
    if "punto_reorden" not in df.columns:
        reorden_list = []
        for _, r in df.iterrows():
            cat = str(r.get("categoria", "")).lower()
            if "pan" in cat or "alimento" in cat:
                reorden_list.append(20)
            elif "bebida" in cat or "lácteo" in cat:
                reorden_list.append(15)
            else:
                reorden_list.append(12)
        df["punto_reorden"] = reorden_list
    else:
        df["punto_reorden"] = pd.to_numeric(df["punto_reorden"], errors="coerce").fillna(15).astype(int)

    # Moneda de origen y costo en moneda extranjera (para productos importados)
    if "moneda_origen" not in df.columns:
        df["moneda_origen"] = "MXN (Nacional)"
    else:
        df["moneda_origen"] = df["moneda_origen"].fillna("MXN (Nacional)")

    if "costo_moneda_origen" not in df.columns:
        df["costo_moneda_origen"] = df["costo_compra"].astype(float)
    else:
        df["costo_moneda_origen"] = pd.to_numeric(df["costo_moneda_origen"], errors="coerce").fillna(df["costo_compra"])

    # Recalcular costo_compra en MXN cuando el producto es importado (USD o EUR)
    for i in range(len(df)):
        mon = str(df.at[i, "moneda_origen"]).upper()
        c_orig = float(df.at[i, "costo_moneda_origen"])
        if "USD" in mon:
            df.at[i, "costo_compra"] = round(c_orig * tc_usd, 2)
        elif "EUR" in mon:
            df.at[i, "costo_compra"] = round(c_orig * tc_eur, 2)
        else:
            # Si es MXN, mantener sincronizado costo_moneda_origen con costo_compra
            if c_orig <= 0:
                df.at[i, "costo_moneda_origen"] = float(df.at[i, "costo_compra"])

    # Ruta de imagen real (en carpeta imagenes_productos/ o URL de internet/GitHub)
    if "ruta_imagen" not in df.columns:
        df["ruta_imagen"] = [nombre_a_ruta_imagen(r.get("producto", "producto")) for _, r in df.iterrows()]
    else:
        df["ruta_imagen"] = df["ruta_imagen"].astype(str)
        for i in range(len(df)):
            r_val = str(df.at[i, "ruta_imagen"]).strip()
            if not r_val or r_val == "nan":
                df.at[i, "ruta_imagen"] = nombre_a_ruta_imagen(df.at[i, "producto"])

    # Foto renderizable (convierte el archivo de imagenes_productos/ a Base64 para funcionar en Streamlit.io o usa URL)
    df["foto_url"] = [
        resolver_imagen_producto(df.at[i, "ruta_imagen"], df.at[i, "producto"], df.at[i, "categoria"])
        for i in range(len(df))
    ]

    # Estado del Punto de Reorden
    estados = []
    for _, r in df.iterrows():
        inv = int(r.get("inventario", 0))
        rop = int(r.get("punto_reorden", 15))
        if inv <= 0:
            estados.append("🚨 AGOTADO (0)")
        elif inv <= rop:
            estados.append("🔴 REORDENAR YA")
        elif inv <= int(rop * 1.4):
            estados.append("🟡 Preventivo")
        else:
            estados.append("🟢 Óptimo")
    df["Estado Stock"] = estados

    return df


# ==============================================================================
# 2. SECCIÓN DE PUNTOS DE REORDEN, ANÁLISIS ABC Y GALERÍA CON FOTOS
# ==============================================================================
def render_analisis_inventarios_y_galeria(df_prod: pd.DataFrame, archivo_productos: str):
    """Renderiza el panel de Puntos de Reorden (ROP), clasificación ABC y catálogo visual con fotos."""
    st.markdown("#### 🚨 Control de Puntos de Reorden (ROP) y Alertas de Abastecimiento")
    st.caption("El **Punto de Reorden** indica el nivel mínimo de existencias en el que debes hacer un nuevo pedido al proveedor para no quedarte sin producto.")

    df_calc = df_prod.copy()
    df_calc["valor_inventario_costo"] = df_calc["inventario"] * df_calc["costo_compra"]
    df_calc["valor_inventario_venta"] = df_calc["inventario"] * df_calc["precio_venta"]
    df_calc["unidades_a_pedir"] = np.maximum(0, (df_calc["punto_reorden"] * 2) - df_calc["inventario"])
    df_calc["costo_reposicion"] = df_calc["unidades_a_pedir"] * df_calc["costo_compra"]

    en_reorden = df_calc[df_calc["inventario"] <= df_calc["punto_reorden"]]
    preventivos = df_calc[(df_calc["inventario"] > df_calc["punto_reorden"]) & (df_calc["inventario"] <= df_calc["punto_reorden"] * 1.4)]
    optimos = df_calc[df_calc["inventario"] > df_calc["punto_reorden"] * 1.4]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🔴 En Punto de Reorden", f"{len(en_reorden)} prod.", help="Productos con stock igual o menor al punto de reorden")
    k2.metric("🟡 Stock Preventivo", f"{len(preventivos)} prod.", help="Productos próximos a tocar el punto de reorden")
    k3.metric("🟢 Stock Óptimo", f"{len(optimos)} prod.", help="Productos con abasto suficiente")
    k4.metric("💰 Valor del Inventario (Costo)", f"${df_calc['valor_inventario_costo'].sum():,.2f}", f"Venta: ${df_calc['valor_inventario_venta'].sum():,.2f}")

    if not en_reorden.empty:
        with st.container(border=True):
            st.error(f"⚠️ **¡Atención Almacén y Compras!** Tienes **{len(en_reorden)} producto(s)** por debajo del Punto de Reorden:")
            cols_rop = st.columns(min(3, len(en_reorden)))
            for idx, (_, r_item) in enumerate(en_reorden.iterrows()):
                with cols_rop[idx % len(cols_rop)]:
                    st.markdown(f"""
                    <div style='background:#fef2f2; border:1px solid #f87171; border-radius:10px; padding:10px; margin-bottom:8px;'>
                        <div style='font-weight:700; color:#991b1b;'>{r_item['producto']}</div>
                        <div style='font-size:0.85rem; color:#7f1d1d;'>
                            Stock actual: <b>{int(r_item['inventario'])}</b> | Punto Reorden: <b>{int(r_item['punto_reorden'])}</b><br>
                            📦 Sugerido pedir: <b>{int(r_item['unidades_a_pedir'])} unid.</b> (${r_item['costo_reposicion']:,.2f})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("🚚 Surtir Automáticamente Productos en Punto de Reorden (Reabastecer al Doble del ROP)", type="primary", use_container_width=True):
                for idx_r in en_reorden.index:
                    df_prod.at[idx_r, "inventario"] = int(df_prod.at[idx_r, "punto_reorden"]) * 2
                cols_save = [c for c in ["producto", "categoria", "codigo_barras", "moneda_origen", "costo_moneda_origen", "costo_compra", "precio_venta", "inventario", "punto_reorden", "unidades_vendidas_hoy", "foto_url"] if c in df_prod.columns]
                df_prod[cols_save].to_csv(archivo_productos, index=False)
                st.success("✅ ¡Orden de reabastecimiento aplicada! El inventario ha sido surtido.")
                st.rerun()
    else:
        st.success("✅ **Inventario Saludable:** Todos tus productos están por encima de su punto de reorden.")

    st.markdown("---")
    # Clasificación ABC de Inventarios
    st.markdown("#### 📊 Análisis ABC de Inventarios (Ley de Pareto 80/20)")
    df_abc = df_calc.sort_values(by="valor_inventario_venta", ascending=False).copy()
    total_val = max(df_abc["valor_inventario_venta"].sum(), 1.0)
    df_abc["pct_valor"] = (df_abc["valor_inventario_venta"] / total_val) * 100
    df_abc["pct_acumulado"] = df_abc["pct_valor"].cumsum()
    df_abc["Clase ABC"] = df_abc["pct_acumulado"].apply(
        lambda x: "Clase A (Alta prioridad - 80% valor)" if x <= 80 else ("Clase B (Media prioridad - 15% valor)" if x <= 95 else "Clase C (Baja prioridad - 5% valor)")
    )

    fig_abc = px.bar(
        df_abc,
        x="producto",
        y="inventario",
        color="Estado Stock",
        hover_data=["punto_reorden", "costo_compra", "precio_venta", "Clase ABC"],
        title="📦 Nivel de Inventario Actual vs. Punto de Reorden por Producto",
        color_discrete_map={
            "🚨 AGOTADO (0)": "#991b1b",
            "🔴 REORDENAR YA": "#ef4444",
            "🟡 Preventivo": "#f59e0b",
            "🟢 Óptimo": "#10b981"
        }
    )
    fig_abc.add_scatter(
        x=df_abc["producto"],
        y=df_abc["punto_reorden"],
        mode="lines+markers",
        name="Línea de Punto de Reorden (ROP)",
        line=dict(color="#1e293b", width=2, dash="dot")
    )
    st.plotly_chart(fig_abc, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🖼️ Catálogo Visual de Productos (Fotos, Códigos de Barras, Costos y Márgenes)")
    st.caption("Vista interactiva con fotografía del producto, código de barras EAN-13, moneda de origen, margen de ganancia y estado de stock.")

    with st.expander("📸 Subir o Vincular Foto Real de Producto (Carpeta `imagenes_productos/` compatible con Streamlit.io)", expanded=False):
        st.markdown("""
        **¿Cómo funciona para local y Streamlit.io?**
        1. Todas las fotos reales se guardan en la carpeta **`imagenes_productos/`** de tu proyecto (o puedes pegar una URL externa `https://...`).
        2. En `productos_template.csv`, la columna `ruta_imagen` guarda la ruta relativa (ej. `imagenes_productos/coca_cola_600ml.png`).
        3. Cuando subes tu repositorio a GitHub y lo despliegas en **Streamlit.io**, el sistema lee el archivo de `imagenes_productos/` y lo convierte automáticamente a formato embebido para que se vea en todas las tablas y tarjetas sin romperse.
        """)
        c_up1, c_up2 = st.columns([1.2, 1.5])
        with c_up1:
            prod_foto_sel = st.selectbox("1. Selecciona el producto:", df_calc["producto"].tolist(), key="sel_prod_subir_foto")
            idx_pf = df_calc.index[df_calc["producto"] == prod_foto_sel].tolist()[0]
            ruta_actual_pf = str(df_calc.at[idx_pf, "ruta_imagen"]) if "ruta_imagen" in df_calc.columns else nombre_a_ruta_imagen(prod_foto_sel)
            st.caption(f"📂 Ruta en CSV (`ruta_imagen`): `{ruta_actual_pf}`")
            url_ext_input = st.text_input("O pega una URL directa de internet (opcional):", value=ruta_actual_pf if ruta_actual_pf.startswith("http") else "", placeholder="https://...", key="url_ext_foto_input")
            if st.button("🔗 Guardar URL de Imagen", use_container_width=True, key="btn_save_url_foto"):
                if url_ext_input.strip():
                    df_save_f = pd.read_csv(archivo_productos)
                    df_save_f = asegurar_columnas_productos(df_save_f)
                    df_save_f.loc[df_save_f["producto"] == prod_foto_sel, "ruta_imagen"] = url_ext_input.strip()
                    cols_s = [c for c in ["producto", "categoria", "codigo_barras", "moneda_origen", "costo_moneda_origen", "costo_compra", "precio_venta", "inventario", "punto_reorden", "unidades_vendidas_hoy", "ruta_imagen"] if c in df_save_f.columns]
                    df_save_f[cols_s].to_csv(archivo_productos, index=False)
                    st.success(f"✅ Imagen vinculada para {prod_foto_sel}")
                    st.rerun()
        with c_up2:
            archivo_subido = st.file_uploader("2. O sube el archivo de imagen desde tu computadora (.png, .jpg, .webp):", type=["png", "jpg", "jpeg", "webp"], key="uploader_foto_real")
            if archivo_subido is not None:
                ext_sub = os.path.splitext(archivo_subido.name)[1].lower().lstrip(".") or "png"
                ruta_destino = nombre_a_ruta_imagen(prod_foto_sel, ext=ext_sub)
                os.makedirs(CARPETA_IMAGENES, exist_ok=True)
                with open(ruta_destino, "wb") as f_out:
                    f_out.write(archivo_subido.getbuffer())
                df_save_f = pd.read_csv(archivo_productos)
                df_save_f = asegurar_columnas_productos(df_save_f)
                df_save_f.loc[df_save_f["producto"] == prod_foto_sel, "ruta_imagen"] = ruta_destino
                cols_s = [c for c in ["producto", "categoria", "codigo_barras", "moneda_origen", "costo_moneda_origen", "costo_compra", "precio_venta", "inventario", "punto_reorden", "unidades_vendidas_hoy", "ruta_imagen"] if c in df_save_f.columns]
                df_save_f[cols_s].to_csv(archivo_productos, index=False)
                st.success(f"✅ Foto guardada en `{ruta_destino}` y vinculada en `productos_template.csv`!")
                st.rerun()

    filtro_cat = st.selectbox(
        "Filtrar catálogo por categoría:",
        ["Todas las categorías"] + sorted(df_calc["categoria"].dropna().unique().tolist()),
        key="filtro_cat_galeria"
    )
    df_gal = df_calc if filtro_cat == "Todas las categorías" else df_calc[df_calc["categoria"] == filtro_cat]

    cols_gal = st.columns(3)
    for idx, (_, row_g) in enumerate(df_gal.iterrows()):
        with cols_gal[idx % 3]:
            with st.container(border=True):
                st.image(row_g["foto_url"], use_container_width=True)
                st.markdown(f"**{row_g['producto']}**")
                st.caption(f"🏷️ `{row_g['categoria']}` | 🏁 `{row_g.get('moneda_origen', 'MXN')}`")
                st.code(f"║▌║█║▌ {row_g['codigo_barras']}", language=None)
                c_a, c_b = st.columns(2)
                c_a.metric("Costo", f"${row_g['costo_compra']:,.2f}")
                c_b.metric("Precio", f"${row_g['precio_venta']:,.2f}")
                gan = float(row_g["precio_venta"]) - float(row_g["costo_compra"])
                marg = (gan / float(row_g["precio_venta"]) * 100) if float(row_g["precio_venta"]) > 0 else 0.0
                st.caption(f"📈 **Ganancia:** ${gan:,.2f} (**{marg:.1f}%** margen)")
                st.caption(f"📦 **Stock:** {int(row_g['inventario'])} u. (Reorden: {int(row_g['punto_reorden'])}) — {row_g['Estado Stock']}")


# ==============================================================================
# 3. SUGERENCIAS DE ADQUISICIÓN POR GEOLOCALIZACIÓN Y TENDENCIAS DEL MERCADO
# ==============================================================================
def render_sugerencias_geolocalizacion_y_mercado(config: dict, n: dict, df_prod: pd.DataFrame):
    """Motor de recomendaciones de adquisición de productos según Estado, Zona, Giro y Tendencias de Mercado."""
    estado = n.get("ubicacion_estado", config.get("ubicacion_estado", "Estado de México"))
    zona = n.get("tipo_zona", config.get("tipo_zona", "Zona Comercial / Centro"))
    giro = config.get("giro", "Tienda de Abarrotes / Miscelánea")

    st.markdown("---")
    st.markdown(f"### 🧭 Sistema Inteligente de Sugerencias de Adquisición por Geolocalización")
    st.caption(f"Recomendaciones estratégicas de compra basadas en tu ubicación (**{estado}**), entorno (**{zona}**) y giro (**{giro}**).")

    # Clasificación climática y socioeconómica regional
    estados_norte = ["Nuevo León", "Chihuahua", "Sonora", "Coahuila", "Tamaulipas", "Baja California", "Baja California Sur", "Sinaloa", "Durango"]
    estados_costa_sur = ["Quintana Roo", "Yucatán", "Campeche", "Tabasco", "Veracruz", "Guerrero", "Oaxaca", "Chiapas", "Colima", "Nayarit"]
    estados_centro = ["Ciudad de México", "Estado de México", "Puebla", "Hidalgo", "Tlaxcala", "Morelos", "Querétaro", "Guanajuato", "Jalisco", "Michoacán"]

    if any(est.lower() in str(estado).lower() for est in estados_norte):
        region_nombre = "Región Norte / Clima Extremo-Seco"
        coordenadas = (25.6866, -100.3161)
        recs_regionales = [
            {"Producto Sugerido": "Bebidas Isotónicas y Agua Embotellada 1L/1.5L", "Prioridad": "🔥 Muy Alta", "Margen Est.": "38%", "Motivo Geolocalizado": f"En {estado} las temperaturas elevadas disparan la rotación de hidratación un +45%."},
            {"Producto Sugerido": "Harina de Trigo, Tortillas de Harina y Carbón", "Prioridad": "⭐ Alta", "Margen Est.": "32%", "Motivo Geolocalizado": "Alta demanda regional en fines de semana y reuniones familiares."},
            {"Producto Sugerido": "Hielo en Bolsa 5kg y Cerveza Clara", "Prioridad": "🔥 Muy Alta", "Margen Est.": "40%", "Motivo Geolocalizado": "Producto ancla que arrastra venta cruzada de botanas y snacks."},
            {"Producto Sugerido": "Snacks Importados (USD) y Enlatados", "Prioridad": "🟢 Media-Alta", "Margen Est.": "35%", "Motivo Geolocalizado": "Cercanía fronteriza favorece aceptación de marcas importadas."}
        ]
    elif any(est.lower() in str(estado).lower() for est in estados_costa_sur):
        region_nombre = "Región Sur-Sureste / Clima Cálido-Húmedo"
        coordenadas = (20.9674, -89.5926)
        recs_regionales = [
            {"Producto Sugerido": "Refrescos Individuales 600ml, Jugos y Electrolitos", "Prioridad": "🔥 Muy Alta", "Margen Est.": "36%", "Motivo Geolocalizado": f"El clima cálido-húmedo de {estado} exige stock frío continuo con punto de reorden +30% mayor."},
            {"Producto Sugerido": "Lácteos UHT (Ultrapasteurizados) y Enlatados", "Prioridad": "⭐ Alta", "Margen Est.": "28%", "Motivo Geolocalizado": "Reduce la merma por humedad y calor frente a productos frescos sin cadena de frío."},
            {"Producto Sugerido": "Repelentes, Hielo y Botanas Saladas", "Prioridad": "⭐ Alta", "Margen Est.": "42%", "Motivo Geolocalizado": "Alta rotación en zonas costeras, turísticas y tropicales."},
            {"Producto Sugerido": "Pan Dulce Empacado de Larga Duración", "Prioridad": "🟢 Media", "Margen Est.": "34%", "Motivo Geolocalizado": "Menor pérdida por humedad ambiental comparado con pan expuesto."}
        ]
    else:
        region_nombre = "Región Centro-Bajío / Clima Templado y Alta Densidad"
        coordenadas = (19.4969, -98.8829) # Chapingo / Texcoco / Centro
        recs_regionales = [
            {"Producto Sugerido": "Pan Dulce Recién Horneado, Bolillo y Café Listo para Llevar", "Prioridad": "🔥 Muy Alta", "Margen Est.": "50%", "Motivo Geolocalizado": f"En {estado} (clima templado/fresco matutino y nocturno) el binomio pan + bebida caliente/lácteo lidera las ventas."},
            {"Producto Sugerido": "Abarrotes de Canasta Básica (Huevo, Frijol, Leche, Tortilla)", "Prioridad": "🔥 Muy Alta", "Margen Est.": "26%", "Motivo Geolocalizado": "Alta densidad habitacional genera compras diarias de reposición familiar."},
            {"Producto Sugerido": "Snacks Individuales, Gansitos y Bebidas Energéticas", "Prioridad": "⭐ Alta", "Margen Est.": "35%", "Motivo Geolocalizado": "Tráfico estudiantil y laboral constante en horas pico (08:00-10:00 y 14:00-16:00)."},
            {"Producto Sugerido": "Insumos Importados Gourmet (Quesos/Harinas Especiales)", "Prioridad": "🟢 Media", "Margen Est.": "44%", "Motivo Geolocalizado": "Diferenciación frente a tiendas de conveniencia cercanas."}
        ]

    col_geo1, col_geo2 = st.columns([1.4, 1])
    with col_geo1:
        st.markdown(f"#### 🎯 Productos Recomendados para Adquirir en **{estado}**")
        st.info(f"📍 **Perfil Regional Detectado:** `{region_nombre}` | **Entorno:** `{zona}`")
        df_recs = pd.DataFrame(recs_regionales)
        st.dataframe(df_recs, use_container_width=True, hide_index=True)

    with col_geo2:
        st.markdown("#### 🗺️ Geolocalización Operativa")
        df_map = pd.DataFrame({"lat": [coordenadas[0]], "lon": [coordenadas[1]]})
        st.map(df_map, zoom=6, use_container_width=True)
        st.caption(f"📌 Coordenadas de referencia comercial: `{coordenadas[0]:.4f}, {coordenadas[1]:.4f}` ({estado})")

    # Tendencias del Mercado
    st.markdown("#### 📈 Tendencias del Mercado y Proyección Estacional por Categoría")
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    df_tend = pd.DataFrame({
        "Mes": meses,
        "Panadería y Alimentos": [115, 110, 95, 85, 80, 85, 90, 95, 110, 125, 135, 145],
        "Bebidas y Refrescos": [80, 85, 105, 130, 145, 140, 130, 125, 100, 90, 85, 110],
        "Abarrotes y Lácteos": [105, 100, 100, 98, 102, 100, 103, 108, 112, 115, 120, 130],
        "Snacks e Importados": [90, 95, 100, 110, 115, 110, 120, 115, 110, 120, 125, 140]
    })
    fig_tend = px.line(
        df_tend,
        x="Mes",
        y=["Panadería y Alimentos", "Bebidas y Refrescos", "Abarrotes y Lácteos", "Snacks e Importados"],
        markers=True,
        title=f"📊 Índice de Demanda Mensual del Mercado en {estado} (Base 100 = Promedio Anual)",
        labels={"value": "Índice de Demanda", "variable": "Categoría Comercial"}
    )
    st.plotly_chart(fig_tend, use_container_width=True)


# ==============================================================================
# 4. MÓDULO DE FACTURACIÓN ELECTRÓNICA (CFDI 4.0 CON DESGLOSE DE IVA)
# ==============================================================================
def render_modulo_facturacion_cfdi(df_db: pd.DataFrame, config: dict):
    """Módulo interactivo para emitir facturas electrónicas CFDI 4.0 a partir de tickets de venta."""
    st.markdown("#### 📄 Emisión de Factura Electrónica (CFDI 4.0 - SAT)")
    st.caption("Selecciona un folio de venta, ingresa los datos fiscales del cliente y genera el comprobante fiscal con desglose de IVA (16%), UUID y códigos de validación.")

    df_ventas = df_db[df_db["tipo"] == "venta"].copy() if not df_db.empty else pd.DataFrame()
    if df_ventas.empty:
        st.info("Registra al menos una venta en el Punto de Venta para poder emitir su factura electrónica.")
        return

    df_ventas = df_ventas.sort_values(by=["fecha", "hora"], ascending=False)
    opciones_vta = [
        f"{r.get('folio', 'TK-0001')} | {r['fecha']} | ${float(r['monto']):,.2f} | {r.get('metodo_pago', 'Efectivo')}"
        for _, r in df_ventas.iterrows()
    ]

    col_f1, col_f2 = st.columns([1.1, 1.3])
    with col_f1:
        st.markdown("##### 1️⃣ Datos del Receptor (Cliente)")
        tk_sel = st.selectbox("Ticket de venta a facturar:", opciones_vta, key="cfdi_tk_sel")
        idx_vta = opciones_vta.index(tk_sel)
        row_vta = df_ventas.iloc[idx_vta]

        rfc_cliente = st.text_input("RFC del Cliente:", value="CACX7605101P8", max_chars=13, key="cfdi_rfc_cli").upper().strip()
        razon_cliente = st.text_input("Nombre o Razón Social:", value="COMERCIALIZADORA AGROINDUSTRIAL CHAPINGO S.A. DE C.V.", key="cfdi_razon_cli")
        cp_cliente = st.text_input("Código Postal Fiscal:", value="56230", max_chars=5, key="cfdi_cp_cli")
        regimen_cliente = st.selectbox(
            "Régimen Fiscal del Receptor:",
            [
                "601 - General de Ley Personas Morales",
                "612 - Personas Físicas con Actividades Empresariales y Profesionales",
                "626 - Régimen Simplificado de Confianza (RESICO)",
                "616 - Sin obligaciones fiscales (Público en General)"
            ],
            key="cfdi_reg_cli"
        )
        uso_cfdi = st.selectbox(
            "Uso del CFDI:",
            [
                "G03 - Gastos en general",
                "G01 - Adquisición de mercancías",
                "S01 - Sin efectos fiscales",
                "CP01 - Pagos"
            ],
            key="cfdi_uso_cli"
        )
        forma_pago_sat = "01 - Efectivo" if "Efectivo" in str(row_vta.get("metodo_pago", "")) else (
            "03 - Transferencia electrónica de fondos" if "Transferencia" in str(row_vta.get("metodo_pago", "")) else "04 - Tarjeta de crédito / 28 - Tarjeta de débito"
        )
        st.caption(f"💳 **Forma de Pago SAT detectada:** `{forma_pago_sat}` | **Método:** `PUE - Pago en una sola exhibición`")

    with col_f2:
        st.markdown("##### 2️⃣ Previsualización del Comprobante Fiscal Digital (CFDI 4.0)")
        monto_total = float(row_vta["monto"])
        tasa_iva = float(config.get("tasa_iva", 16.0)) / 100.0
        incluye_iva = bool(config.get("incluye_iva", True))

        if incluye_iva and tasa_iva > 0:
            subtotal_cfdi = monto_total / (1.0 + tasa_iva)
            iva_cfdi = monto_total - subtotal_cfdi
            total_cfdi = monto_total
        else:
            subtotal_cfdi = monto_total
            iva_cfdi = subtotal_cfdi * tasa_iva
            total_cfdi = subtotal_cfdi + iva_cfdi

        folio_tk = str(row_vta.get("folio", "TK-0001"))
        uuid_fiscal = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{folio_tk}-{rfc_cliente}")).upper()

        with st.container(border=True):
            st.markdown(f"""
            <div style='background:#f8fafc; padding:16px; border-radius:10px; border:1px solid #cbd5e1; font-family:monospace;'>
                <div style='display:flex; justify-content:space-between; border-bottom:2px solid #0284c7; padding-bottom:8px; margin-bottom:10px;'>
                    <div>
                        <strong style='font-size:1.1rem; color:#0f172a;'>{config.get('icono', '🏪')} {config.get('nombre', 'MI EMPRESA')}</strong><br>
                        <span style='font-size:0.8rem; color:#475569;'>RFC Emisor: <b>{config.get('rfc', 'XAXX010101000')}</b> | Lugar Exp.: {config.get('direccion', 'México')[:35]}</span>
                    </div>
                    <div style='text-align:right;'>
                        <span style='background:#0284c7; color:white; padding:3px 8px; border-radius:5px; font-size:0.75rem; font-weight:bold;'>CFDI 4.0 INGRESO</span><br>
                        <span style='font-size:0.75rem; color:#334155;'>Ticket Origen: <b>{folio_tk}</b></span>
                    </div>
                </div>
                <div style='font-size:0.82rem; color:#1e293b; margin-bottom:10px;'>
                    <b>RECEPTOR:</b> {razon_cliente}<br>
                    <b>RFC Receptor:</b> {rfc_cliente} | <b>C.P.:</b> {cp_cliente}<br>
                    <b>Régimen Fiscal:</b> {regimen_cliente}<br>
                    <b>Uso CFDI:</b> {uso_cfdi} | <b>Forma Pago:</b> {forma_pago_sat}
                </div>
                <div style='border-top:1px dashed #94a3b8; border-bottom:1px dashed #94a3b8; padding:8px 0; margin:8px 0; font-size:0.82rem;'>
                    <b>Concepto Facturado:</b> {row_vta.get('concepto', 'Venta de mostrador')}<br>
                    ClaveProdServ SAT: <code>50202300 / 50181900</code> | ClaveUnidad: <code>H87 (Pieza)</code> | ObjetoImp: <code>02 - Sí objeto de impuesto</code>
                </div>
                <div style='text-align:right; font-size:0.9rem; color:#0f172a;'>
                    Subtotal: <b>${subtotal_cfdi:,.2f} MXN</b><br>
                    IVA Trasladado ({config.get('tasa_iva', 16.0):.0f}%): <b>${iva_cfdi:,.2f} MXN</b><br>
                    <span style='font-size:1.15rem; color:#0284c7;'>TOTAL FACTURADO: <b>${total_cfdi:,.2f} MXN</b></span>
                </div>
                <div style='margin-top:10px; padding-top:8px; border-top:1px solid #e2e8f0; font-size:0.72rem; color:#64748b; word-break:break-all;'>
                    <b>Folio Fiscal (UUID):</b> {uuid_fiscal}<br>
                    <b>Fecha Timbrado:</b> {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} | <b>No. Certificado SAT:</b> 00001000000504465028<br>
                    <b>Sello Digital CFDI:</b> ||1.1|{uuid_fiscal}|{folio_tk}|SAT970701NN3||
                </div>
            </div>
            """, unsafe_allow_html=True)

            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante Version="4.0" Folio="{folio_tk}" Fecha="{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}" SubTotal="{subtotal_cfdi:.2f}" Moneda="MXN" Total="{total_cfdi:.2f}" TipoDeComprobante="I" MetodoPago="PUE" LugarExpedicion="{cp_cliente}">
  <cfdi:Emisor Rfc="{config.get('rfc', 'XAXX010101000')}" Nombre="{config.get('nombre', 'EMPRESA')}" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="{rfc_cliente}" Nombre="{razon_cliente}" DomicilioFiscalReceptor="{cp_cliente}" RegimenFiscalReceptor="{regimen_cliente[:3]}" UsoCFDI="{uso_cfdi[:3]}"/>
  <cfdi:Impuestos TotalImpuestosTrasladados="{iva_cfdi:.2f}">
    <cfdi:Traslados>
      <cfdi:Traslado Base="{subtotal_cfdi:.2f}" Impuesto="002" TipoFactor="Tasa" TasaOCuota="{tasa_iva:.6f}" Importe="{iva_cfdi:.2f}"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
  <tfd:TimbreFiscalDigital UUID="{uuid_fiscal}"/>
</cfdi:Comprobante>"""

            st.download_button(
                "📥 Descargar XML de Factura CFDI 4.0",
                data=xml_content,
                file_name=f"CFDI_{folio_tk}_{rfc_cliente}.xml",
                mime="application/xml",
                use_container_width=True,
                type="primary"
            )


# ==============================================================================
# 5. ÁREAS DE LA EMPRESA Y TABLERO DE RAZONES FINANCIERAS
# ==============================================================================
def render_areas_y_razones_financieras(calculos: dict, config: dict, df_db: pd.DataFrame, df_prod: pd.DataFrame):
    """Renderiza el mapa de las diferentes áreas involucradas de la empresa y todas las razones financieras."""
    m = calculos["metricas"]
    e = calculos["evaluacion_economica"]
    c = calculos["caja"]
    r = calculos["riesgos"]
    d = calculos["diario"]

    st.markdown("### 🏢 Mapa Integral de Áreas de la Empresa y Niveles de Control")
    st.caption("Visión departamental que conecta desde la inversión inicial y compras hasta el punto de venta, almacén, recursos humanos y finanzas.")

    valor_inv_costo = float((df_prod["inventario"] * df_prod["costo_compra"]).sum()) if not df_prod.empty else 0.0
    en_rop = int((df_prod["inventario"] <= df_prod["punto_reorden"]).sum()) if ("punto_reorden" in df_prod.columns and not df_prod.empty) else 0
    importados_cnt = int((df_prod["moneda_origen"] != "MXN (Nacional)").sum()) if ("moneda_origen" in df_prod.columns and not df_prod.empty) else 0

    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        with st.container(border=True):
            st.markdown("#### 🛒 1. Área de Ventas y Caja (POS)")
            st.caption("**Nivel de Control:** Cajeros y Supervisor de Piso")
            st.metric("Ventas Acumuladas", f"${m['ingresos_totales']:,.2f}", f"Hoy: ${d.get('venta_hoy', 0.0):,.2f}")
            st.markdown(f"- **Ticket y Código de Barras:** Activo (150mm)\n- **Meta Diaria (PE):** `${m['punto_equilibrio_diario']:,.2f}`\n- **Facturación CFDI 4.0:** Habilitada")

        with st.container(border=True):
            st.markdown("#### 👥 4. Área de Recursos Humanos y Personal")
            st.caption("**Nivel de Control:** Gerencia y Auditoría")
            usuarios_unicos = df_db["usuario"].nunique() if "usuario" in df_db.columns and not df_db.empty else 2
            st.metric("Personal con Operaciones", f"{usuarios_unicos} usuarios")
            st.markdown("- **Jerarquía:** Gerente (Total) / Cajero (Restringido)\n- **Control de Fecha:** Bloqueado con Huella Biométrica\n- **Corte de Turno:** Individual por jornada")

    with col_a2:
        with st.container(border=True):
            st.markdown("#### 📦 2. Área de Almacén e Inventarios")
            st.caption("**Nivel de Control:** Jefe de Almacén")
            st.metric("Valor en Almacén (Costo)", f"${valor_inv_costo:,.2f}", f"{len(df_prod)} SKUs activos")
            st.markdown(f"- **Alertas Punto de Reorden:** `{en_rop} productos`\n- **Merma Estimada:** `{r['riesgo_merma_pct']}%` (${r['merma_estimada_pesos']:,.2f})\n- **Control por Foto y Código:** Activo")

        with st.container(border=True):
            st.markdown("#### 🌍 5. Área de Compras e Importaciones")
            st.caption("**Nivel de Control:** Compras y Proveedores")
            tc_usd = st.session_state.get("tc_usd", 19.85)
            st.metric("Productos Importados", f"{importados_cnt} SKUs", f"TC USD: ${tc_usd:,.2f}")
            st.markdown(f"- **Geolocalización:** `{config.get('ubicacion_estado')}`\n- **Sugerencias Regionales:** Activas\n- **Cotizaciones de Proveedores:** Integradas")

    with col_a3:
        with st.container(border=True):
            st.markdown("#### 💼 3. Área de Finanzas y Contabilidad")
            st.caption("**Nivel de Control:** Dirección Financiera / Gerente")
            margen_op_val = float(m.get('margen_operativo_pct', m.get('margen_neto_pct', 0.0)))
            tir_val = float(e.get('tir_anual_pct', e.get('tir_estimada_pct', 0.0)))
            st.metric("Utilidad Neta Real", f"${m['utilidad_neta']:,.2f}", f"Margen: {margen_op_val:.1f}%")
            st.markdown(f"- **VAN (12 meses):** `${e['van_mensual']:,.2f}`\n- **TIR Estimada:** `{tir_val}%` vs Exigida `{r['tasa_descuento_total_pct']}%`\n- **IVA Configurado:** `{config.get('tasa_iva', 16.0)}%`")

        with st.container(border=True):
            st.markdown("#### 🏭 6. Área de Ingeniería de Planta y Costos")
            st.caption("**Nivel de Control:** Operaciones y Mantenimiento")
            st.metric("Inversión Inicial", f"${config.get('inversion_inicial', 0.0):,.2f}")
            st.markdown(f"- **Costos Fijos:** `${m['costos_fijos']:,.2f}`\n- **Costos Variables:** `${m['costos_variables']:,.2f}`\n- **Balance Energético CFE y Flujo:** Integrado")

    st.markdown("---")
    st.markdown("### 📊 Tablero Integral de Razones Financieras (Financial Ratios)")
    st.caption("Indicadores clave para evaluar liquidez, solvencia, eficiencia operativa y rentabilidad de la empresa.")

    # Cálculos de razones financieras
    caja_disp = float(c.get("caja_disponible", c.get("caja_actual", config.get("caja_disponible", 10000.0))))
    activo_circulante = caja_disp + valor_inv_costo
    pasivo_corto_plazo = max(float(m["costos_fijos"]) + float(m["costos_variables"]) * 0.25, 1000.0)

    razon_liquidez = activo_circulante / pasivo_corto_plazo
    prueba_acido = caja_disp / pasivo_corto_plazo
    capital_trabajo = activo_circulante - pasivo_corto_plazo

    ingresos = max(float(m["ingresos_totales"]), 1.0)
    utilidad_bruta = float(m["ingresos_totales"]) - float(m["costos_variables"])
    margen_bruto = (utilidad_bruta / ingresos) * 100.0
    margen_neto = float(m.get("margen_operativo_pct", m.get("margen_neto_pct", 0.0)))

    inv_inicial = max(float(config.get("inversion_inicial", 10000.0)), 1.0)
    roi_pct = (float(m["utilidad_neta"]) / inv_inicial) * 100.0
    rotacion_inv = float(m["costos_variables"]) / max(valor_inv_costo, 1.0)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("💧 Razón de Liquidez Corriente", f"{razon_liquidez:.2f}x", "Óptimo > 1.50x", help="(Caja + Inventario) / Pasivos de Corto Plazo")
    r2.metric("⚡ Prueba del Ácido", f"{prueba_acido:.2f}x", "Óptimo > 1.00x", help="Caja Disponible / Pasivos de Corto Plazo (sin depender de vender inventario)")
    r3.metric("🏦 Capital de Trabajo Neto", f"${capital_trabajo:,.2f}", "Liquidez operativa", help="Activo Circulante - Pasivo de Corto Plazo")
    r4.metric("🔄 Rotación de Inventario", f"{rotacion_inv:.2f} veces", "Velocidad de stock", help="Costo de Ventas / Valor del Inventario")

    r5, r6, r7, r8 = st.columns(4)
    r5.metric("📈 Margen de Utilidad Bruta", f"{margen_bruto:.1f}%", f"${utilidad_bruta:,.2f}", help="(Ventas - Costos Variables) / Ventas")
    r6.metric("💰 Margen de Utilidad Neta", f"{margen_neto:.1f}%", f"${m['utilidad_neta']:,.2f}", help="Utilidad Neta / Ventas Totales")
    r7.metric("🎯 ROI (Retorno s/ Inversión)", f"{roi_pct:.1f}%", f"TIR: {tir_val}%", help="Utilidad Neta / Inversión Inicial")
    r8.metric("⚖️ Relación Costo Fijo / Variable", f"${m['costos_fijos']:,.0f} / ${m['costos_variables']:,.0f}", f"PE: ${m['punto_equilibrio_diario']:,.0f}/día")

    # Tabla resumen de Razones Financieras con interpretación
    df_ratios = pd.DataFrame([
        {"Categoría": "Liquidez", "Razón Financiera": "Liquidez Corriente", "Fórmula": "(Caja + Inventario) / Gastos CP", "Valor Actual": f"{razon_liquidez:.2f} veces", "Meta Saludable": "> 1.50 veces", "Estado": "🟢 Saludable" if razon_liquidez >= 1.5 else ("🟡 Aceptable" if razon_liquidez >= 1.0 else "🔴 Ajustado")},
        {"Categoría": "Liquidez", "Razón Financiera": "Prueba del Ácido", "Fórmula": "Caja Disponible / Gastos CP", "Valor Actual": f"{prueba_acido:.2f} veces", "Meta Saludable": "> 1.00 veces", "Estado": "🟢 Saludable" if prueba_acido >= 1.0 else "🟡 Preventivo"},
        {"Categoría": "Solvencia", "Razón Financiera": "Capital de Trabajo", "Fórmula": "Activo Circulante - Pasivo CP", "Valor Actual": f"${capital_trabajo:,.2f}", "Meta Saludable": "> $0.00", "Estado": "🟢 Positivo" if capital_trabajo > 0 else "🔴 Negativo"},
        {"Categoría": "Rentabilidad", "Razón Financiera": "Margen Bruto", "Fórmula": "(Ventas - Costo Variable) / Ventas", "Valor Actual": f"{margen_bruto:.1f}%", "Meta Saludable": "> 30.0%", "Estado": "🟢 Saludable" if margen_bruto >= 30 else "🟡 Moderado"},
        {"Categoría": "Rentabilidad", "Razón Financiera": "Margen Operativo / Neto", "Fórmula": "Utilidad Neta / Ventas", "Valor Actual": f"{margen_neto:.1f}%", "Meta Saludable": "> 15.0%", "Estado": "🟢 Saludable" if margen_neto >= 15 else ("🟡 Moderado" if margen_neto > 0 else "🔴 Pérdida")},
        {"Categoría": "Evaluación", "Razón Financiera": "VAN (12 Meses)", "Fórmula": "Flujos Descontados - Inversión", "Valor Actual": f"${e['van_mensual']:,.2f}", "Meta Saludable": "> $0.00", "Estado": "🟢 Viable" if e["van_mensual"] > 0 else "🔴 No Viable"},
        {"Categoría": "Evaluación", "Razón Financiera": "TIR Anualizada", "Fórmula": "Tasa donde VAN = 0", "Valor Actual": f"{tir_val}%", "Meta Saludable": f"> {r['tasa_descuento_total_pct']}%", "Estado": "🟢 Supera TMAR" if tir_val >= r["tasa_descuento_total_pct"] else "🟡 Bajo TMAR"}
    ])
    st.dataframe(df_ratios, use_container_width=True, hide_index=True)
