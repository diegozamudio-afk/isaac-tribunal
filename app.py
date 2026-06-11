import streamlit as st
import pandas as pd
import gspread
import json
import plotly.express as px

st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

@st.cache_data(ttl=60)
def conectar_sheets():
    # Asegúrate de configurar 'gcp_service_account' en los Secrets de Streamlit
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    cliente = gspread.service_account_from_dict(credenciales_dict)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1")

st.title("📊 Dashboard ISAAC - Inteligencia de Gestión")

try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Normalización de columnas
        if 'Tipo de Infracción' in df.columns:
            df = df.rename(columns={'Tipo de Infracción': 'tipo'})
        
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce') / 10000
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce') / 10000
        
        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Registros Totales", len(df))
        col2.metric("Tipo más frecuente", df['tipo'].mode()[0] if 'tipo' in df.columns else "N/A")
        col3.metric("Última actualización", df['Fecha'].iloc[-1] if 'Fecha' in df.columns else "N/A")

        st.markdown("---")
        
        # Mapa y Gráficos
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📍 Mapa de Calor")
            st.map(df.dropna(subset=['lat', 'lon']))
        with c2:
            st.subheader("Distribución por Tipo")
            if 'tipo' in df.columns:
                fig = px.pie(df, names='tipo', color='tipo', color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        # TABLA SIEMPRE VISIBLE
        st.markdown("---")
        st.subheader("📋 Detalle de Infracciones Registradas")
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("La planilla está vacía.")
except Exception as e:
    st.error(f"Error cargando dashboard: {e}")

if st.button("🔄 Actualizar"):
    st.rerun()
