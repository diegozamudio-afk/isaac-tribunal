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

# Botón de limpieza
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    hoja = conectar_sheets()
    hoja.delete_rows(2, hoja.row_count)
    st.rerun()

# --- LÓGICA DE PROCESAMIENTO ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # AQUÍ ESTÁ EL CAMBIO: Reemplazamos coma por punto antes de convertir
        for col in ['lat', 'lon']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['lat', 'lon'])
        
        if not df.empty:
            st.write(f"Infracciones registradas: {len(df)}")
            mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)
            for _, row in df.iterrows():
                folium.CircleMarker(
                    [row['lat'], row['lon']], 
                    radius=8, 
                    color='red',
                    popup=f"Patente: {row['Patente']} - {row['Infraccion']}"
                ).add_to(mapa)
            st_folium(mapa, width=800, height=400)
        else:
            st.warning("Datos recibidos pero las coordenadas no son numéricas.")
    else:
        st.info("Esperando datos en la planilla...")
except Exception as e:
    st.error(f"Error: {e}")
