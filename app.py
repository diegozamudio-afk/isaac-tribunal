import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# 1. Definición clara de la función de conexión
def conectar_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Usamos el secreto guardado en Streamlit
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    # Asegurate de que el nombre aquí coincida exactamente con tu planilla de Google
    return cliente.open("ISAAC - Monitoreo").sheet1

# 2. Función para obtener los datos
def obtener_datos():
    try:
        hoja = conectar_sheets()
        datos = hoja.get_all_records()
        return pd.DataFrame(datos)
    except Exception as e:
        st.error(f"Error al conectar con la planilla: {e}")
        return pd.DataFrame()

# 3. Interfaz del Dashboard
st.title("📊 Dashboard de Control - ISAAC")
st.write("Cargando datos en tiempo real desde Google Sheets...")

df = obtener_datos()

if not df.empty and 'lat' in df.columns:
    st.success(f"Se encontraron {len(df)} registros.")
    # Mapa
    mapa = folium.Map(location=[df['lat'].iloc[0], df['lon'].iloc[0]], zoom_start=14)
    for _, row in df.iterrows():
        folium.CircleMarker([row['lat'], row['lon']], radius=8, color='red').add_to(mapa)
    st_folium(mapa, width=700)
else:
    st.info("El mapa está vacío o no se han cargado datos aún.")
