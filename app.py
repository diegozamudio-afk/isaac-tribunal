import streamlit as st
import pandas as pd
import gspread
import json
import plotly.express as px
from google.oauth2.service_account import Credentials

# Configuración
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

@st.cache_data(ttl=60)
def conectar_sheets():
    # Asegúrate de configurar 'gcp_service_account' en los Secrets de Streamlit
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(
        credenciales_dict, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC - Inteligencia de Gestión")

# Carga de datos
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Renombrar columna para asegurar consistencia
        if 'Tipo de Infracción' in df.columns:
            df = df.rename(columns={'Tipo de Infracción': 'tipo'})
        
        # Limpieza de coordenadas
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce') / 10000
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce') / 10000
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registros Totales", len(df))
        col2.metric("Infracciones Hoy", len(df[df['lat'] != 0]))
        col3.metric("Usuarios CiDi Tuc", "130k")
        col4.metric("Recaudación Est.", f"${len(df) * 5000:,.0f}")

        st.markdown("---")

        # Mapa y Gráficos
        st.subheader("📍 Mapa de Calor: Zonas Críticas")
        st.map(df.dropna(subset=['lat', 'lon']))

        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("Distribución por Tipo")
            if 'tipo' in df.columns:
                fig_pie = px.pie(df, names='tipo', color='tipo', 
                                 color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("Columna 'tipo' no encontrada.")

        with col_der:
            st.subheader("Volumen de Registros")
            st.bar_chart(df.index)

        with st.expander("Ver Registros Detallados"):
            st.dataframe(df)
    else:
        st.info("La planilla está vacía.")
except Exception as e:
    st.error(f"Error cargando dashboard: {e}")

if st.button("🔄 Actualizar"):
    st.rerun()
