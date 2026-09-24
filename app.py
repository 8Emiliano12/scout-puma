import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS PARA IPAD/MÓVIL ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

# Magia CSS: Hace los botones gigantes, los íconos grandes y el texto fácil de leer al sol
st.markdown("""
    <style>
    div.stButton > button {
        height: 80px;
        font-size: 22px !important;
        font-weight: bold;
        border-radius: 12px;
        background-color: #1F4E78;
        color: white;
    }
    div.stDownloadButton > button {
        height: 60px;
        font-size: 18px !important;
        border-radius: 10px;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stRadio label, .stSlider label {
        font-size: 18px !important;
        font-weight: 800;
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MEMORIA DE LA APLICACIÓN Y ROSTER ---
if 'lista_jugadas' not in st.session_state:
    st.session_state.lista_jugadas = []
if 'yarda_actual' not in st.session_state:
    st.session_state.yarda_actual = 20

# Listas separadas por posición ofensiva
LISTA_QB = ["N/A", "3 - Garza", "10 - Sánchez", "17 - Corona"]
LISTA_RB = ["N/A", "23 - Pérez", "26 - Schrader", "32 - Báez", "34 - Melo", "35 - Santillán", "44 - Hernández"]
LISTA_WR = ["N/A", "1 - Blanco", "12 - Cardona", "13 - Vivas", "14 - Medrano", "18 - Ponce", "81 - Román", "82 - Reyes", "83 - Reyes", "84 - Granados", "88 - Villafuerte", "98 - Miranda"]

# Combinaciones lógicas para los menús (El [1:] evita repetir el "N/A")
PASADORES = LISTA_QB
CORREDORES = LISTA_RB + LISTA_WR[1:] + LISTA_QB[1:] # RBs primero, luego WRs y QBs
RECEPTORES = LISTA_WR + LISTA_RB[1:] # WRs primero, luego RBs

# --- 3. INTERFAZ GRÁFICA ---
st.title("🏈 Scout Pumas CU")

# Control de Periodo Global (Ocupa toda la pantalla arriba)
periodo_actual = st.selectbox("⏱️ PERIODO DE PRÁCTICA (Aplica para todas las jugadas)", 
                              ["SKELL OFENSA", "2DO DOWN RUN FIT", "RED ZONE", "TEAM", "OTRO"])
st.markdown("---")

# Fila 1: La Cancha y Posición
st.subheader("📍 1. Posición del Balón")
col_cancha, col_datos = st.columns([2, 1])

with col_cancha:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/American_football_field.svg/1000px-American_football_field.svg.png", use_container_width=True)
    st.session_state.yarda_actual = st.slider("Desliza para mover el balón de yarda", min_value=1, max_value=50, value=st.session_state.yarda_actual)

with col_datos:
    # Formato "L (Texto)" para extraer fácilmente la primera letra y que sea compatible con Hudl
    hash_mark = st.radio("➖ Hash Mark", ["L (Izquierdo)", "M (Centro)", "R (Derecho)"])
    d_c1, d_c2 = st.columns(2)
    with d_c1:
        down = st.number_input("⬇️ Down", min_value=1, max_value=4, value=1)
    with d_c2:
        distancia = st.number_input("📏 Distancia", min_value=1, value=10)

st.markdown("---")

# Fila 2: Jugada y Resultado
st.subheader("📋 2. Jugada y Resultado")
col_jugada, col_resultado = st.columns(2)

with col_jugada:
    personnel = st.selectbox("👥 Personal", ["10", "11", "12", "20", "21", "22", "Otro"])
    off_form = st.text_input("📝 Formación", placeholder="Ej. Trips Right")
    off_play = st.text_input("🏃 Jugada", placeholder="Ej. Zone Right")
    
    st.write("🏈 **Jugadores Involucrados**")
    passer = st.selectbox("🎯 QB (Lanzador)", PASADORES, index=0)
    runner = st.selectbox("💨 Corredor", CORREDORES, index=0)
    receiver = st.selectbox("👐 Receptor", RECEPTORES, index=0)

with col_resultado:
    # Formato "Hudl (Texto)" para mantener compatibilidad al exportar
    resultado = st.radio("🏁 Resultado de la jugada", ["Pass (Pase)", "Rush (Carrera)", "Drop (Caído)", "Interception (INT)"], horizontal=True)
    ganancia = st.number_input("📈 Yardas Ganadas / Perdidas", value=0, step=1)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✅ GUARDAR JUGADA", use_container_width=True):
        nueva_jugada = {
            "TITLE": periodo_actual,  
            "PLAY #": len(st.session_state.lista_jugadas) + 1,
            "PERSONNEL": personnel,
            "HASH": hash_mark[0], # Extrae la L, M o R
            "YARD LN": st.session_state.yarda_actual, 
            "DN": down,               
            "DIST": distancia,        
            "OFF FORM": off_form,
            "MOTION": "", 
            "OFF PLAY": off_play,
            "RESULT": resultado.split(" ")[0], # Extrae Pass, Rush, Drop o Interception
            "GAIN/LS": ganancia,
            "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "",
            "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
            "PASSER": passer.split(" - ")[0] if passer != "N/A" else ""
        }
        st.session_state.lista_jugadas.append(nueva_jugada)
        st.success(f"¡Jugada {len(st.session_state.lista_jugadas)} guardada correctamente!")

st.markdown("---")

# --- 4. EXPORTACIÓN PARA HUDL ---
if st.session_state.lista_jugadas:
    st.subheader(f"📊 Resumen de la práctica ({len(st.session_state.lista_jugadas)} jugadas)")
    df_jugadas = pd.DataFrame(st.session_state.lista_jugadas)
    
    col_csv, col_excel = st.columns(2)
    with col_csv:
        csv_data = df_jugadas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV para Hudl", data=csv_data, file_name='hudl_import.csv', mime='text/csv', use_container_width=True)
    with col_excel:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_jugadas.to_excel(writer, index=False, sheet_name='Practica')
        st.download_button("📊 Descargar Tabla Excel", data=excel_buffer.getvalue(), file_name='reporte.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
