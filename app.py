import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# Configuración inicial
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    # Abrimos el archivo y la pestaña exacta
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard de Control - ISAAC")

# --- BOTÓN DE LIMPIEZA ---
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    try:
        hoja = conectar_sheets()
        hoja.delete_rows(2, hoja.row_count)
        st.sidebar.success("¡Mapa reseteado!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- CARGA Y MAPA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    # Aseguramos que lat y lon sean números
    if not df.empty:
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])
    
    if not df.empty:
        st.write(f"Infracciones registradas: {len(df)}")
        
        # Mapa
        mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)
        for _, row in df.iterrows():
            folium.CircleMarker(
                [row['lat'], row['lon']], 
                radius=8, 
                color='red', 
                popup=f"Patente: {row['Patente']} - {row['Infraccion']}"
            ).add_to(mapa)
        
        st_folium(mapa, width=800, height=500)
    else:
        st.info("Esperando nuevos datos en la planilla...")
        
except Exception as e:
    st.error(f"Error de conexión: {e}")
