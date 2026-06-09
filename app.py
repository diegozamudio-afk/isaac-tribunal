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
    # Asegurate de tener el secreto 'gcp_service_account' en los settings de la app
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC - Control Móvil")

# Botón de reinicio en barra lateral
if st.sidebar.button("⚠️ Reiniciar Base de Datos"):
    hoja = conectar_sheets()
    hoja.delete_rows(2, hoja.row_count)
    st.rerun()

try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Limpieza de datos (Coma a punto y conversión a número)
        for col in ['lat', 'lon']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        
        # Filtramos filas vacías
        df_mapa = df.dropna(subset=['lat', 'lon'])
        
        if not df_mapa.empty:
            st.write(f"Infracciones activas: {len(df_mapa)}")
            
            # Mapa con tiles estables para Streamlit Cloud
            mapa = folium.Map(
                location=[df_mapa['lat'].mean(), df_mapa['lon'].mean()], 
                zoom_start=14,
                tiles='CartoDB positron'
            )
            
            for _, row in df_mapa.iterrows():
                popup_msg = f"Patente: {row.get('Patente', 'N/A')} - {row.get('Infraccion', 'Multa')}"
                folium.CircleMarker(
                    [row['lat'], row['lon']], 
                    radius=10, color='red', fill=True, popup=popup_msg
                ).add_to(mapa)
            
            st_folium(mapa, width=800, height=500)
        else:
            st.warning("Datos recibidos pero las coordenadas no son válidas.")
    else:
        st.info("Esperando infracciones...")

except Exception as e:
    st.error(f"Error técnico: {e}")
