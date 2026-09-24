import streamlit as st
import pandas as pd
import io

# 1. Configuración responsiva (Clave para iPad y celular)
st.set_page_config(
    page_title="Pumas CU Scout",
    page_icon="🏈",
    layout="wide" 
)

# 2. Inicializar la "Memoria" de la App (Session State)
if 'lista_jugadas' not in st.session_state:
    st.session_state.lista_jugadas = []

if 'yarda_actual' not in st.session_state:
    st.session_state.yarda_actual = 20

# 3. Encabezado de la aplicación
st.title("🏈 Tracker de Práctica - Pumas CU")
st.markdown("---")

# 4. Indicador visual para confirmar que la memoria funciona
st.write(f"📝 Jugadas en memoria: {len(st.session_state.lista_jugadas)}")
# --- PASO 2: CONTEXTO Y POSICIÓN DEL BALÓN ---
st.subheader("📍 1. Contexto y Posición")

# Creamos dos columnas. En iPad se verán mitad y mitad. En celular, una debajo de la otra.
col1, col2 = st.columns(2)

with col1:
    # Selector Global de Periodo (TITLE)
    periodo_actual = st.selectbox(
        "Periodo de Práctica", 
        ["SKELL OFENSA", "2DO DOWN RUN FIT", "RED ZONE", "TEAM", "OTRO"]
    )
    
    # Sub-columnas para Down y Distancia
    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        down = st.number_input("Down", min_value=1, max_value=4, value=1)
    with sub_c2:
        distancia = st.number_input("Distancia", min_value=1, value=10)

with col2:
    # Hash Mark (Botones horizontales)
    hash_mark = st.radio("Hash", ["L", "M", "R"], horizontal=True)
    
    # La Yarda Pegajosa (Slider)
    yarda_seleccionada = st.slider(
        "Línea de Golpeo (Yarda)", 
        min_value=1, max_value=50, 
        value=st.session_state.yarda_actual
    )
    # Guardamos la yarda en la memoria
    st.session_state.yarda_actual = yarda_seleccionada

st.markdown("---")
