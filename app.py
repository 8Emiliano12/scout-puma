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
