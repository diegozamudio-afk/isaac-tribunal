import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(page_title="ISAAC - Tribunal de Faltas", layout="wide")

st.title("🚦 ISAAC - Monitoreo Activo de Infracciones")
st.markdown("### Mapa de Calor y Zonas Críticas")

# Datos simulados para la demostración (Latitudes y Longitudes de Tucumán)
data = pd.DataFrame({
    'Barrio/Zona': ['Centro', 'Barrio Norte', 'Yerba Buena', 'Terminal'],
    'lat': [-26.8300, -26.8150, -26.8100, -26.8350],
    'lon': [-65.2050, -65.2020, -65.3000, -65.1950],
    'infracciones': [85, 42, 60, 25]
})

col1, col2 = st.columns([2, 1])

with col1:
    # Creación del Mapa de Calor
    mapa = folium.Map(location=[-26.8241, -65.2072], zoom_start=12) # Centro
    for i, row in data.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['infracciones'] / 3,
            color='red',
            fill=True,
            fill_color='red',
            tooltip=f"{row['Barrio/Zona']}: {row['infracciones']} Actas"
        ).add_to(mapa)
    
    st_folium(mapa, width=700, height=400)

with col2:
    st.info("📊 **Métricas en Tiempo Real**")
    st.metric(label="Actas Procesadas Hoy", value="212", delta="15% vs ayer")
    st.metric(label="Agentes en Calle", value="14")
    st.metric(label="Precisión OCR (Cámaras)", value="98.5%")

st.success("🟢 Sistema ISAAC Operativo y Enlazado a la Base de Datos.")
# --- BOTÓN PARA LIMPIAR DATOS ---
if st.sidebar.button("⚠️ Reiniciar Mapa de Calor"):
    # Esto borra todas las filas excepto la cabecera (fila 1)
    hoja = conectar_sheets() # Asegurate de tener la conexión a sheets aquí
    hoja.delete_rows(2, hoja.row_count)
    st.sidebar.success("Mapa reseteado a 0.")
    st.rerun() # Recarga la página para mostrar el mapa vacío
    # --- CARGA AUTOMÁTICA DESDE GOOGLE SHEETS ---
def obtener_datos():
    hoja = conectar_sheets() # La función que ya tenías
    datos = hoja.get_all_records()
    return pd.DataFrame(datos)

df = obtener_datos()

# --- MAPA DE CALOR DINÁMICO ---
if not df.empty:
    mapa = folium.Map(location=[df.lat.mean(), df.lon.mean()], zoom_start=13)
    for i, row in df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=10,
            color='red'
        ).add_to(mapa)
    st_folium(mapa)
else:
    st.write("Esperando nuevas infracciones...")
