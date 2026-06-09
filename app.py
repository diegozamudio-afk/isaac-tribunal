import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# Configuración
st.set_page_config(page_title="Dashboard ISAAC", layout="wide")

def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    # Abrimos el archivo por nombre
    archivo = cliente.open("ISAAC - Monitoreo")
    # Abrimos la pestaña por su nombre (verificá que se llame 'Hoja1' o como la tengas)
    return archivo.worksheet("Hoja1")

st.title("📊 Dashboard de Control - ISAAC")

# --- BOTÓN DE LIMPIEZA ---
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    try:
        hoja = conectar_sheets()
        # Borra desde la fila 2 hasta el final, dejando los encabezados en la fila 1
        hoja.delete_rows(2, hoja.row_count)
        st.sidebar.success("¡Mapa reseteado a 0!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error al limpiar: {e}")

# --- CARGA Y MAPA ---
try:
    hoja = conectar_sheets()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    st.write("---")
    st.write("DEBUG: Contenido del DataFrame:")
    st.write(df)  # <--- ESTO ES LA CLAVE
    
    if not df.empty and 'lat' in df.columns:
        st.write(f"Total infracciones: {len(df)}")
        # ... resto de tu código del mapa ...
    else:
        st.warning("⚠️ El DataFrame está vacío o no encuentra la columna 'lat'.")
        st.write("Columnas detectadas:", df.columns.tolist())
except Exception as e:
    st.error(f"Error técnico: {e}")
