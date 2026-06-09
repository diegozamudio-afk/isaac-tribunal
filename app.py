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

# --- BOTÓN DE LIMPIEZA ---
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    try:
        hoja = conectar_sheets()
        hoja.delete_rows(2, hoja.row_count)
        st.rerun()
    except Exception as e:
        st.error(f"Error al limpiar: {e}")

# --- CARGA Y MAPA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    # IMPORTANTE: Convertimos a numérico y forzamos la eliminación de errores
    if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])
        
        if not df.empty:
            # Creamos el mapa
            mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)
            for _, row in df.iterrows():
                folium.CircleMarker(
                    [row['lat'], row['lon']], 
                    radius=8, 
                    color='red', 
                    fill=True,
                    popup=row['Infraccion']
                ).add_to(mapa)
            
            # Mostramos el mapa
            st_folium(mapa, width=800, height=500)
        else:
            st.warning("Hay datos pero las columnas 'lat'/'lon' no tienen valores numéricos válidos.")
    else:
        st.info("Esperando datos... asegurate de que las columnas se llamen 'lat' y 'lon'.")
        
except Exception as e:
    st.error(f"Error técnico: {e}")
