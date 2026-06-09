import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    # Asegurate de tener el secreto 'gcp_service_account' en los settings de la app
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC - Control Móvil")

# --- BOTONES DE CONTROL ---
col1, col2 = st.columns(2)
if col1.button("🔄 Recargar Datos"):
    st.rerun()

if col2.button("⚠️ Reiniciar Base de Datos"):
    try:
        hoja = conectar_sheets()
        hoja.delete_rows(2, hoja.row_count)
        st.success("Base reiniciada correctamente.")
        st.rerun()
    except Exception as e:
        st.error(f"Error al reiniciar: {e}")

# --- PROCESAMIENTO Y MAPA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Convertimos a número y corregimos la escala dividiendo por 10.000
        # Esto transforma -268241 en -26.8241
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce') / 10000
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce') / 10000
        
        # Filtramos filas con datos válidos para el mapa
        df_mapa = df.dropna(subset=['lat', 'lon'])
        
        if not df_mapa.empty:
            st.write(f"### Mapa de Infracciones ({len(df_mapa)} registros)")
            # st.map usa la infraestructura nativa de Streamlit, es lo más estable
            st.map(df_mapa)
            
            st.write("### Detalle de registros:")
            st.dataframe(df)
        else:
            st.warning("No hay coordenadas válidas para mostrar en el mapa.")
    else:
        st.info("La planilla está vacía.")

except Exception as e:
    st.error(f"Error técnico: {e}")
