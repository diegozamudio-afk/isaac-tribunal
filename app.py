import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Configuración básica
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

# Configuración de credenciales
def conectar_sheets():
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    archivo = cliente.open("ISAAC - Monitoreo")
    return archivo.worksheet("Hoja 1")

st.title("📊 Dashboard ISAAC")

# --- BOTONES DE CONTROL ---
col1, col2 = st.columns(2)
if col1.button("🔄 Recargar Datos"):
    st.rerun()

if col2.button("⚠️ Reiniciar Base de Datos"):
    try:
        hoja = conectar_sheets()
        hoja.delete_rows(2, hoja.row_count)
        st.success("Base reiniciada")
        st.rerun()
    except Exception as e:
        st.error(f"Error al reiniciar: {e}")

# --- PROCESAMIENTO Y MAPA ---
try:
    hoja = conectar_sheets()
    data = hoja.get_all_records()
    
    if data:
        df = pd.DataFrame(data)
        
        # Limpieza obligatoria: Coma a punto y conversión a float
        # Nos aseguramos de trabajar solo con lat/lon
        for col in ['lat', 'lon']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        
        # Filtramos filas con datos faltantes
        df_clean = df.dropna(subset=['lat', 'lon'])
        
        if not df_clean.empty:
            st.write(f"### Mostrando {len(df_clean)} infracciones")
            # st.map usa internamente columnas 'lat' y 'lon'
            st.map(df_clean[['lat', 'lon']])
            
            st.write("### Registros en Planilla:")
            st.dataframe(df_clean)
        else:
            st.warning("No hay coordenadas válidas para mostrar en el mapa.")
    else:
        st.info("La planilla está vacía.")

except Exception as e:
    st.error(f"Error en la carga: {e}")
