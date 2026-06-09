import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    return cliente.open("ISAAC - Monitoreo").sheet1

st.title("📊 Dashboard ISAAC")

# Obtener datos
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    if not df.empty and 'lat' in df.columns:
        st.write(f"Total infracciones: {len(df)}")
        mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)
        for _, row in df.iterrows():
            folium.CircleMarker([row['lat'], row['lon']], radius=8, color='red').add_to(mapa)
        st_folium(mapa, width=700)
    else:
        st.info("Esperando datos...")
except Exception as e:
    st.error(f"Error de conexión: {e}")
