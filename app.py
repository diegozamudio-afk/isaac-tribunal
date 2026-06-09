import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# 1. Definir la función de conexión PRIMERO
def conectar_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Asegurate de que el secreto sea el mismo nombre que en el Agente
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    return cliente.open("ISAAC - Monitoreo").sheet1

# 2. Definir la función que obtiene los datos
def obtener_datos():
    hoja = conectar_sheets() # Ahora sí la va a encontrar
    datos = hoja.get_all_records()
    return pd.DataFrame(datos)

# 3. Resto de tu código para el mapa...
st.title("📊 Dashboard de Control")
df = obtener_datos()

if not df.empty:
    # Asegurate de que las columnas se llamen 'lat' y 'lon'
    # Si en tu Sheets se llaman diferente, cambialo acá:
    mapa = folium.Map(location=[df['lat'].iloc[0], df['lon'].iloc[0]], zoom_start=13)
    # ... código del mapa ...
