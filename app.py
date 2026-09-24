import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS PARA IPAD/MÓVIL ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

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

# Listas Ofensivas
LISTA_QB = ["N/A", "3 - Garza", "10 - Sánchez", "17 - Corona"]
LISTA_RB = ["N/A", "23 - Pérez", "26 - Schrader", "32 - Báez", "34 - Melo", "35 - Santillán", "44 - Hernández"]
LISTA_WR = ["N/A", "1 - Blanco", "12 - Cardona", "13 - Vivas", "14 - Medrano", "18 - Ponce", "81 - Román", "82 - Reyes", "83 - Reyes", "84 - Granados", "88 - Villafuerte", "98 - Miranda"]

PASADORES = LISTA_QB
CORREDORES = LISTA_RB + LISTA_WR[1:] + LISTA_QB[1:] 
RECEPTORES = LISTA_WR + LISTA_RB[1:] 

# Lista Defensiva (DL, LB, DB, CB)
LISTA_DEFENSA = [
    "N/A", "0 - Morrison (DL)", "2 - Soriano (DB)", "4 - Mercado (LB)", "6 - González (LB)", 
    "7 - Bañuelos (DB)", "8 - Higelin (DB)", "9 - Carriles (DL)", "11 - Liceá (DL)", 
    "15 - Álvarez (CB)", "16 - Aguilar (LB)", "19 - Velasco (LB)", "21 - Moreno (DB)", 
    "22 - Acosta (LB)", "24 - Ceballos (CB)", "27 - Villegas (LB)", "28 - Cervantes (LB)", 
    "29 - Juárez (CB)", "30 - Cabrera (CB)", "31 - Arreola (LB)", "33 - Bañuelos (LB)", 
    "39 - Saldaña (LB)", "40 - Ocampo (LB)", "42 - Trejo (LB)", "43 - Rodríguez (CB)", 
    "52 - Contreras (LB)", "59 - González (LB)", "90 - Saavedra (LB)", "91 - Martínez (DL)", 
    "92 - Bautista (DL)", "94 - Soriano (DL)", "95 - Bautista (DL)", "99 - Valdéz (DL)"
]

# --- 3. INTERFAZ GRÁFICA ---
st.title("🏈 Scout Pumas CU")

periodo_actual = st.selectbox("⏱️ PERIODO DE PRÁCTICA", ["SKELL OFENSA", "2DO DOWN RUN FIT", "RED ZONE", "TEAM", "OTRO"])
st.markdown("---")

# Fila 1: Posición del Balón
st.subheader("📍 1. Posición del Balón")
col_yarda, col_datos = st.columns([2, 1])

with col_yarda:
    st.session_state.yarda_actual = st.slider("Desliza para mover el balón de yarda", min_value=1, max_value=50, value=st.session_state.yarda_actual)
    hash_mark = st.radio("➖ Hash Mark", ["L (Izquierdo)", "M (Centro)", "R (Derecho)"], horizontal=True)

with col_datos:
    d_c1, d_c2 = st.columns(2)
    with d_c1:
        down = st.number_input("⬇️ Down", min_value=1, max_value=4, value=1)
    with d_c2:
        distancia = st.number_input("📏 Distancia", min_value=1, value=10)

st.markdown("---")

# Fila 2: Jugadores Ofensivos y Defensivos
st.subheader("📋 2. Desarrollo de la Jugada")
col_ofensa, col_defensa = st.columns(2)

with col_ofensa:
    st.write("🏈 **Ofensiva**")
    passer = st.selectbox("🎯 QB (Lanzador)", PASADORES, index=0)
    runner = st.selectbox("💨 Corredor", CORREDORES, index=0)
    receiver = st.selectbox("👐 Receptor", RECEPTORES, index=0)

with col_defensa:
    st.write("🛡️ **Defensiva**")
    defensor_1 = st.selectbox("💥 Tackle / Captura / Pase Def.", LISTA_DEFENSA, index=0)
    defensor_2 = st.selectbox("🤝 Asistencia (Opcional)", LISTA_DEFENSA, index=0)

st.markdown("---")

# Fila 3: Resultado
st.subheader("🏁 3. Resultado")
col_res, col_gan = st.columns(2)

with col_res:
    # Se agregó Scramble al selector visual
    resultado = st.radio("Resultado", ["Pass (Pase)", "Rush (Carrera)", "Scramble", "Incompleto", "Sack", "Interception"], horizontal=True)
with col_gan:
    ganancia = st.number_input("📈 Yardas Ganadas / Perdidas", value=0, step=1)
    
st.markdown("<br>", unsafe_allow_html=True)

# --- GUARDAR JUGADA ---
if st.button("✅ GUARDAR JUGADA", use_container_width=True):
    nueva_jugada = {
        "TITLE": periodo_actual,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "HASH": hash_mark[0],
        "YARD LN": st.session_state.yarda_actual, 
        "DN": down,               
        "DIST": distancia,        
        "RESULT": resultado.split(" ")[0], # Extrae Pass, Rush, Scramble, Incompleto, Sack, etc.
        "GAIN/LS": ganancia,
        "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "",
        "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
        "PASSER": passer.split(" - ")[0] if passer != "N/A" else "",
        "TACKLER 1": defensor_1.split(" - ")[0] if defensor_1 != "N/A" else "",
        "TACKLER 2": defensor_2.split(" - ")[0] if defensor_2 != "N/A" else ""
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
