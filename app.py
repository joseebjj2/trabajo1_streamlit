import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración inicial de la página (ancho completo)
st.set_page_config(
    page_title="Dashboard de Ventas de Autos - Modo Oscuro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para Modo Oscuro
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .main-header {
        font-size: 2.3rem;
        color: #60A5FA;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.read_csv("ventas.csv", sep=";", parse_dates=["fecha"])


df = cargar_datos()

# --- BARRA LATERAL: Filtros ---
st.sidebar.image("https://img.icons8.com/color/96/car--v1.png", width=70)
st.sidebar.header("⚙️ Panel de Control")
st.sidebar.markdown("Filtra los datos del tablero:")

colores_disponibles = sorted(df["color"].unique())
colores = st.sidebar.multiselect(
    "🎨 Colores de autos", colores_disponibles, default=colores_disponibles
)

anios_disponibles = sorted(df["fecha"].dt.year.unique())
anios = st.sidebar.multiselect(
    "📅 Años", anios_disponibles, default=anios_disponibles
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tip:** Los gráficos combinan barras y líneas para facilitar el análisis."
)

# Filtrado de datos
filtrado = df[df["color"].isin(colores) & df["fecha"].dt.year.isin(anios)]

if filtrado.empty:
    st.warning(
        "⚠️ Selecciona al menos un color y un año en la barra lateral para ver los datos."
    )
    st.stop()

# --- TÍTULO Y ENCABEZADO ---
st.markdown(
    '<p class="main-header">🚗 Dashboard Interactivo - Modo Noche</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Análisis visual avanzado del rendimiento de ventas automotrices.</p>',
    unsafe_allow_html=True,
)

# --- TARJETAS DE MÉTRICAS ---
total_unidades = filtrado["unidades"].sum()
color_top = filtrado.groupby("color")["unidades"].sum().idxmax()
unidades_top = filtrado.groupby("color")["unidades"].sum().max()
promedio_registro = filtrado["unidades"].mean()

col1, col2, col3 = st.columns(3)
col1.metric(
    label="📦 Total de Autos Vendidos",
    value=f"{total_unidades:,}".replace(",", "."),
)
col2.metric(
    label="🏆 Color Más Vendido",
    value=color_top,
    delta=f"{unidades_top:,} un.".replace(",", "."),
)
col3.metric(
    label="📊 Promedio por Registro", value=f"{promedio_registro:.1f} un."
)

st.markdown("---")

# --- PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(
    ["📊 Ventas por Color (Combinado)", "📈 Evolución Temporal (Combinado)", "📋 Tabla y Descarga"]
)

with tab1:
    st.subheader("Ventas Totales por Color (Barras y Línea)")
    st.write(
        "Visualización combinada de barras con una línea de tendencia superpuesta para evaluar el volumen total por color."
    )

    por_color = (
        filtrado.groupby("color")["unidades"]
        .sum()
        .reset_index()
        .sort_values(by="unidades", ascending=False)
    )

    # Gráfico combinado: Barras + Línea usando Graph Objects de Plotly
    fig_color = go.Figure()
    
    # Añadir barras
    fig_color.add_trace(
        go.Bar(
            x=por_color["color"],
            y=por_color["unidades"],
            name="Unidades (Barras)",
            marker_color="#3B82F6",
            text=por_color["unidades"],
            textposition="outside",
        )
    )
    
    # Añadir línea con los mismos datos
    fig_color.add_trace(
        go.Scatter(
            x=por_color["color"],
            y=por_color["unidades"],
            name="Tendencia (Línea)",
            mode="lines+markers",
            line=dict(color="#F43F5E", width=3),
            marker=dict(size=8),
        )
    )

    fig_color.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="Unidades",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_color, use_container_width=True)

with tab2:
    st.subheader("Evolución Mensual (Líneas y Barras de Fondo)")
    st.write(
        "Evolución temporal por color con líneas de tendencia acompañadas de barras mensuales de fondo."
    )

    pivot = filtrado.pivot_table(
        index="fecha", columns="color", values="unidades", aggfunc="sum"
    ).reset_index()

    fig_line = go.Figure()

    # Añadir barras semitransparentes de fondo para cada color
    for col in pivot.columns[1:]:
        fig_line.add_trace(
            go.Bar(
                x=pivot["fecha"],
                y=pivot[col],
                name=f"{col} (Barras)",
                opacity=0.3,
            )
        )

    # Añadir líneas encima
    for col in pivot.columns[1:]:
        fig_line.add_trace(
            go.Scatter(
                x=pivot["fecha"],
                y=pivot[col],
                name=f"{col} (Línea)",
                mode="lines+markers",
                line=dict(width=2),
                marker=dict(size=6),
            )
        )

    fig_line.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="Unidades",
        hovermode="x unified",
        legend_title="Series",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("Registros Detallados")
    st.write(
        "Consulta la tabla completa de datos filtrados o descárgala para análisis externos."
    )

    st.dataframe(filtrado, use_container_width=True)

    # Botón para descargar CSV
    csv = filtrado.to_csv(index=False, sep=";").encode("utf-8")
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name="ventas_autos_filtradas.csv",
        mime="text/csv",
    )
