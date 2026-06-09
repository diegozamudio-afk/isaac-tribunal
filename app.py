import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Asegurate de tener el secreto 'gcp_service_account' en los Settings de la App
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1") 

st.title("📊 Dashboard de Control - ISAAC")

# --- BARRA LATERAL CON CONTROLES ---
st.sidebar.header("Controles")

# Botón de Refresh
if st.sidebar.button("🔄 Recargar Datos"):
    st.rerun()

# Botón de Reinicio
if st.sidebar.button("⚠️ Reiniciar Base de Datos"):
    hoja = conectar_sheets()
    hoja.delete_rows(2, hoja.row_count)
    st.rerun()

# --- CARGA Y MAPA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    if not df.empty:
        # Convertimos lat y lon a números (reemplazando coma por punto)
        for col in ['lat', 'lon']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        
        # Filtramos datos válidos
        df_mapa = df.dropna(subset=['lat', 'lon'])
        
        if not df_mapa.empty:
            st.write(f"### Mapa de Infracciones ({len(df_mapa)} registros)")
            # st.map es infalible porque usa la infraestructura nativa de Streamlit
            st.map(df_mapa)
            
            st.write("### Detalle de registros:")
            st.dataframe(df_mapa)
        else:
            st.warning("No se encontraron coordenadas válidas.")
    else:
        st.info("Esperando datos en la planilla...")

except Exception as e:
    st.error(f"Error: {e}")
