import sys
import os
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import DB

st.set_page_config(
    page_title="Hospital Supply Chain Monitor",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Supply Chain Intelligence")
st.caption("Monitoreo de escasez de medicamentos — FDA Drug Shortages")

@st.cache_data
def cargar_datos():
    db = DB()
    df = db.query("SELECT * FROM medical_products ORDER BY date_scraped DESC")
    return df

@st.cache_data
def cargar_alertas():
    db = DB()
    try:
        df = db.query("SELECT * FROM alerts ORDER BY triggered_at DESC")
    except:
        df = pd.DataFrame()
    return df

df = cargar_datos()
df_alertas = cargar_alertas()

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.subheader("Resumen general")

col1, col2, col3, col4 = st.columns(4)

total_hoy = df[df["date_scraped"] == df["date_scraped"].max()]
en_escasez = total_hoy[total_hoy["status"].str.strip() == "Currently in Shortage"]
resueltos  = total_hoy[total_hoy["status"].str.strip() == "Resolved Shortage"]

with col1:
    st.metric(label="En escasez hoy",   value=len(en_escasez))
with col2:
    st.metric(label="Resueltos hoy",    value=len(resueltos))
with col3:
    st.metric(label="Total histórico",  value=len(df))
with col4:
    st.metric(label="Alertas generadas",value=len(df_alertas))

# ── Tabla con colores y filtros ───────────────────────────────────────────────
st.divider()
st.subheader("Medicamentos en escasez activa")

col_filtro1, col_filtro2 = st.columns(2)

with col_filtro1:
    estados = ["Todos"] + list(df["status"].str.strip().unique())
    filtro_estado = st.selectbox("Filtrar por estado", estados)

with col_filtro2:
    busqueda = st.text_input("Buscar medicamento", placeholder="Ej: Albuterol...")

df_filtrado = df[df["date_scraped"] == df["date_scraped"].max()].copy()
df_filtrado["status"] = df_filtrado["status"].str.strip()

if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status"] == filtro_estado]

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["product_name"].str.contains(busqueda, case=False, na=False)
    ]

def colorear_status(val):
    if val == "Currently in Shortage":
        return "background-color: #ffcccc; color: #8b0000"
    elif val == "Resolved Shortage":
        return "background-color: #ccffcc; color: #006400"
    return ""

st.dataframe(
    df_filtrado[["product_name", "status", "date_scraped"]].style.applymap(
        colorear_status, subset=["status"]
    ),
    use_container_width=True,
    hide_index=True
)
st.caption(f"Mostrando {len(df_filtrado)} medicamentos")

# ── Movimientos recientes ─────────────────────────────────────────────────────
st.divider()
st.subheader("Movimientos recientes")

col_new, col_res = st.columns(2)

with col_new:
    st.markdown("#### 🔴 Últimos en entrar en escasez")
    df_nuevos = df[df["status"].str.strip() == "Currently in Shortage"].sort_values(
        "date_scraped", ascending=False
    ).drop_duplicates(subset=["product_name"], keep="first")
    st.dataframe(
        df_nuevos[["product_name", "date_scraped"]].head(10),
        use_container_width=True,
        hide_index=True
    )

with col_res:
    st.markdown("#### 🟢 Últimos en resolverse")
    df_resueltos = df[df["status"].str.strip() == "Resolved Shortage"].sort_values(
        "date_scraped", ascending=False
    ).drop_duplicates(subset=["product_name"], keep="first")
    st.dataframe(
        df_resueltos[["product_name", "date_scraped"]].head(10),
        use_container_width=True,
        hide_index=True
    )

# ── Gráfico histórico ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Evolución histórica de escaseces")

df_historico = df[df["status"].str.strip() == "Currently in Shortage"].groupby(
    "date_scraped"
).size().reset_index(name="total_en_escasez")

if len(df_historico) > 1:
    fig = px.line(
        df_historico,
        x="date_scraped",
        y="total_en_escasez",
        markers=True,
        labels={
            "date_scraped":     "Fecha",
            "total_en_escasez": "Medicamentos en escasez"
        },
        title="Medicamentos en escasez activa por día"
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(tickformat="%b %d", dtick="D1")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Ejecuta el pipeline durante más días para ver la evolución histórica.")

# ── Alertas recientes ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Alertas recientes")

if df_alertas.empty:
    st.success("Sin alertas activas. Todos los medicamentos estables.")
else:
    st.dataframe(
        df_alertas[["product_name", "alert_type", "message", "triggered_at"]],
        use_container_width=True,
        hide_index=True
    )