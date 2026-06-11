import streamlit as st
import pandas as pd
import gspread
import json
import plotly.express as px
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

# --- CONEXIÓN ---
@st.cache_data(ttl=60) # Recarga cada 60 seg
def conectar_sheets():
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC - Inteligencia de Gestión")

try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Procesamiento
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce') / 10000
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce') / 10000
        
        # --- NUEVO: NIVEL 1 (KPIs) ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registros Totales", len(df))
        col2.metric("Infracciones Hoy", len(df[df['lat'] != 0])) # Ajustar según tu columna fecha
        col3.metric("Usuarios CiDi Tuc", "130k", "Meta: 800k")
        col4.metric("Recaudación Est.", f"${len(df) * 5000:,.0f}") # Ejemplo cálculo

        st.markdown("---")

        # --- NIVEL 2: MAPA ---
        st.subheader("📍 Mapa de Calor: Zonas Críticas")
        st.map(df.dropna(subset=['lat', 'lon']))

        # --- NUEVO: NIVEL 3 (GRÁFICOS) ---
        st.markdown("---")
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.subheader("Distribución por Tipo")
            if 'tipo' in df.columns: # Asumiendo que tenés columna 'tipo'
                fig_pie = px.pie(df, names='tipo', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.write("Columna 'tipo' no encontrada en Sheets.")

        with col_der:
            st.subheader("Volumen de Registros")
            st.bar_chart(df.index)

        # --- TABLA ---
        with st.expander("Ver Registros Detallados"):
            st.dataframe(df)

    else:
        st.info("La planilla está vacía.")

except Exception as e:
    st.error(f"Error: {e}")

# Botón recarga manual
if st.button("🔄 Actualizar Datos"):
    st.rerun()
