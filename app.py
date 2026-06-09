import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")

st.title("🔎 Diagnóstico de Datos")

try:
    # 1. Conexión
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    hoja = archivo.worksheet("Hoja 1")
    
    # 2. Leer datos
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    # 3. MOSTRAR LA VERDAD
    st.write("Columnas detectadas:", df.columns.tolist())
    st.dataframe(df)
    
    # 4. Probar conversión forzada
    # IMPORTANTE: Asegurate que estos nombres coincidan con lo que salga arriba en "Columnas detectadas"
    if 'lat' in df.columns and 'lon' in df.columns:
        df['lat'] = pd.to_numeric(df['lat'].astype(str).str.replace(',', '.'), errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'].astype(str).str.replace(',', '.'), errors='coerce')
        
        st.write("Datos procesados (deberían ser números):")
        st.dataframe(df[['lat', 'lon']])
        
        # 5. Intentar graficar
        st.map(df.dropna(subset=['lat', 'lon']))
    else:
        st.error("¡Las columnas 'lat' y 'lon' no se llaman así en tu Sheets! Revisá los encabezados.")

except Exception as e:
    st.error(f"Error: {e}")
