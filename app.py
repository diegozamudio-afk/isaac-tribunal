import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard de Control - ISAAC")

# --- BARRA LATERAL (Botones y Datos) ---
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    try:
        hoja = conectar_sheets()
        hoja.delete_rows(2, hoja.row_count)
        st.sidebar.success("¡Datos borrados!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error al limpiar: {e}")

# --- LÓGICA DE CARGA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Mostramos la tabla para verificar qué está pasando
        st.write("### Registros actuales:")
        st.dataframe(df)
        
        # Procesamiento para el mapa
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df_mapa = df.dropna(subset=['lat', 'lon'])
        
        if not df_mapa.empty:
            st.write("### Mapa de Infracciones:")
            mapa = folium.Map(location=[df_mapa['lat'].mean(), df_mapa['lon'].mean()], zoom_start=14)
            for _, row in df_mapa.iterrows():
                # Manejo seguro de columnas
                desc = row['Infraccion'] if 'Infraccion' in row else "Sin detalle"
                folium.CircleMarker([row['lat'], row['lon']], radius=8, color='red', popup=desc).add_to(mapa)
            st_folium(mapa, width=800, height=400)
        else:
            st.warning("No hay coordenadas válidas para mostrar en el mapa.")
    else:
        st.info("La planilla está vacía.")
except Exception as e:
    st.error(f"Error crítico: {e}")
