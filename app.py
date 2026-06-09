import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Asegurate que el nombre del secreto sea exactamente 'gcp_service_account'
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC")

# Botones de control
col1, col2 = st.columns(2)
if col1.button("🔄 Recargar"):
    st.rerun()
if col2.button("⚠️ Reiniciar Base"):
    hoja = conectar_sheets()
    hoja.delete_rows(2, hoja.row_count)
    st.rerun()

# --- MAPA ---
try:
    hoja = conectar_sheets()
    df = pd.DataFrame(hoja.get_all_records())

    if not df.empty:
        # Limpieza de coordenadas
        df['lat'] = df['lat'].astype(str).str.replace(',', '.').astype(float)
        df['lon'] = df['lon'].astype(str).str.replace(',', '.').astype(float)
        
        # Mapa nativo (infalible)
        st.map(df)
        
        st.write("### Registros:")
        st.dataframe(df)
    else:
        st.info("No hay datos cargados.")
except Exception as e:
    st.error(f"Error: {e}")
