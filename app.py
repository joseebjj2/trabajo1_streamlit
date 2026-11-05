import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración inicial de la página (ancho completo y diseño moderno)
st.set_page_config(
    page_title="Dashboard de Ventas de Autos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para los títulos
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
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
    "💡 **Tip:** Pasa el cursor sobre los gráficos para ver los detalles interactivos."
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
    '<p class="main-header">🚗 Dashboard Interactivo de Ventas de Autos</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Exploración visual del rendimiento comercial y tendencias del mercado automotriz.</p>',
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
    ["📊 Ventas por Color", "📈 Evolución Temporal", "📋 Tabla y Descarga"]
)

with tab1:
    st.subheader("Ventas Totales Acumuladas por Color")
    st.write(
        "Gráfico interactivo que muestra el volumen total de ventas agrupado por cada color seleccionado."
    )

    por_color = (
        filtrado.groupby("color")["unidades"]
        .sum()
        .reset_index()
        .sort_values(by="unidades", ascending=False)
    )

    fig_color = px.bar(
        por_color,
        x="color",
        y="unidades",
        color="color",
        text="unidades",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"color": "Color", "unidades": "Unidades Vendidas"},
    )
    fig_color.update_traces(textposition="outside")
    fig_color.update_layout(showlegend=False, xaxis_title="", yaxis_title="Unidades")
    st.plotly_chart(fig_color, use_container_width=True)

with tab2:
    st.subheader("Evolución Mensual de Ventas")
    st.write(
        "Compara el comportamiento temporal de las ventas mes a mes según los colores activos."
    )

    pivot = filtrado.pivot_table(
        index="fecha", columns="color", values="unidades", aggfunc="sum"
    ).reset_index()

    fig_line = px.line(
        pivot,
        x="fecha",
        y=pivot.columns[1:],
        markers=True,
        labels={
            "value": "Unidades Vendidas",
            "fecha": "Fecha",
            "variable": "Color",
        },
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_line.update_layout(
        xaxis_title="",
        yaxis_title="Unidades",
        legend_title="Colores",
        hovermode="x unified",
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
