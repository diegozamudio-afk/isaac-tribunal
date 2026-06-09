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

try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    if not df.empty:
        # 1. Convertir coordenadas a números
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])
        
        # 2. Dibujar mapa
        mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)
        
        for _, row in df.iterrows():
            # Verificamos si existe la columna, si no, ponemos un mensaje genérico
            popup_text = row['Infraccion'] if 'Infraccion' in row else "Sin descripción"
            
            folium.CircleMarker(
                [row['lat'], row['lon']], 
                radius=8, 
                color='red', 
                popup=popup_text
            ).add_to(mapa)
        
        st_folium(mapa, width=800, height=500)
    else:
        st.info("La planilla está conectada pero no tiene datos todavía.")
        st.write("Columnas detectadas en la planilla:", df.columns.tolist())

except Exception as e:
    st.error(f"Error detectado: {e}")
