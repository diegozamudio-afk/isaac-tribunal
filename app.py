import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard ISAAC - Control Móvil")

# --- BOTONES ---
if st.button("🔄 Recargar Datos"):
    st.rerun()

try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # 1. Convertimos a números
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        # 2. CORRECCIÓN: Dividimos por 10.000 para recuperar el decimal
        # Esto transforma -268241 en -26.8241
        df['lat'] = df['lat'] / 10000
        df['lon'] = df['lon'] / 10000
        
        st.write("### Mapa de Infracciones:")
        # 3. Graficamos
        st.map(df.dropna(subset=['lat', 'lon']))
        
        st.write("### Registros:")
        st.dataframe(df)
    else:
        st.info("La planilla está vacía.")

except Exception as e:
    st.error(f"Error: {e}")
