import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Estilos generales para botones secundarios */
    div.stButton > button {
        height: 60px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 10px;
        background-color: #f0f2f6;
        color: black;
        border: 2px solid #dcdcdc;
    }
    /* Botones primarios (Seleccionados o Guardar) */
    div.stButton > button[kind="primary"] {
        background-color: #1F4E78;
        color: white;
        border: none;
    }
    /* Botón de descarga */
    div.stDownloadButton > button {
        height: 80px;
        font-size: 20px !important;
        background-color: #2E7D32;
        color: white;
        border-radius: 12px;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stRadio label, .stSlider label {
        font-size: 18px !important;
        font-weight: 800;
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE MEMORIA INTELIGENTE ---
if 'lista_jugadas' not in st.session_state: st.session_state.lista_jugadas = []
if 'yarda_actual' not in st.session_state: st.session_state.yarda_actual = 20
if 'down' not in st.session_state: st.session_state.down = 1
if 'distancia' not in st.session_state: st.session_state.distancia = 10
if 'msg_exito' not in st.session_state: st.session_state.msg_exito = ""
if 'resultado' not in st.session_state: st.session_state.resultado = "Pass"

# Listas de Jugadores
LISTA_QB = ["N/A", "3 - Garza", "10 - Sánchez", "17 - Corona"]
LISTA_RB = ["N/A", "23 - Pérez", "26 - Schrader", "32 - Báez", "34 - Melo", "35 - Santillán", "44 - Hernández"]
LISTA_WR = ["N/A", "1 - Blanco", "12 - Cardona", "13 - Vivas", "14 - Medrano", "18 - Ponce", "81 - Román", "82 - Reyes", "83 - Reyes", "84 - Granados", "88 - Villafuerte", "98 - Miranda"]
PASADORES = LISTA_QB
CORREDORES = LISTA_RB + LISTA_WR[1:] + LISTA_QB[1:] 
RECEPTORES = LISTA_WR + LISTA_RB[1:] 

LISTA_DEFENSA = [
    "N/A", "0 - Morrison", "2 - Soriano", "4 - Mercado", "6 - González", "7 - Bañuelos", 
    "8 - Higelin", "9 - Carriles", "11 - Liceá", "15 - Álvarez", "16 - Aguilar", 
    "19 - Velasco", "21 - Moreno", "22 - Acosta", "24 - Ceballos", "27 - Villegas", 
    "28 - Cervantes", "29 - Juárez", "30 - Cabrera", "31 - Arreola", "33 - Bañuelos", 
    "39 - Saldaña", "40 - Ocampo", "42 - Trejo", "43 - Rodríguez", "52 - Contreras", 
    "59 - González", "90 - Saavedra", "91 - Martínez", "92 - Bautista", "94 - Soriano", 
    "95 - Bautista", "99 - Valdéz"
]

# --- 3. INTERFAZ GRÁFICA ---
st.title("🏈 Scout Pumas CU")

if st.session_state.msg_exito:
    st.success(st.session_state.msg_exito)
    st.session_state.msg_exito = ""

periodo_actual = st.selectbox("⏱️ PERIODO DE PRÁCTICA", ["SKELL OFENSA", "SKELL DEFENSA", "2DO DOWN RUN FIT", "RED ZONE", "TEAM", "OTRO"])
st.markdown("---")

# --- FILA 1: POSICIÓN ---
st.subheader("📍 1. Posición y Contexto")
col_y, col_d = st.columns([2, 1])

with col_y:
    st.session_state.yarda_actual = st.slider("Línea de Golpeo (Yarda estática)", min_value=1, max_value=50, value=st.session_state.yarda_actual)
    hash_mark = st.radio("➖ Hash", ["L", "M", "R"], horizontal=True)

with col_d:
    d_c1, d_c2 = st.columns(2)
    with d_c1:
        down = st.number_input("⬇️ Down", min_value=1, max_value=4, key="down")
    with d_c2:
        distancia = st.number_input("📏 Distancia", min_value=1, key="distancia")

st.markdown("---")

# --- FILA 2: RESULTADO (COMO BOTONES) ---
st.subheader("🏁 2. Tipo de Jugada")
r1, r2, r3, r4, r5, r6 = st.columns(6)

if r1.button("🏈 Pase", type="primary" if st.session_state.resultado == "Pass" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Pass"; st.rerun()
if r2.button("🏃 Carrera", type="primary" if st.session_state.resultado == "Rush" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Rush"; st.rerun()
if r3.button("🏃‍♂️ Scramble", type="primary" if st.session_state.resultado == "Scramble" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Scramble"; st.rerun()
if r4.button("❌ Incompleto", type="primary" if st.session_state.resultado == "Incompleto" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Incompleto"; st.rerun()
if r5.button("💥 Sack", type="primary" if st.session_state.resultado == "Sack" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Sack"; st.rerun()
if r6.button("🦅 INT", type="primary" if st.session_state.resultado == "Interception" else "secondary", use_container_width=True): 
    st.session_state.resultado = "Interception"; st.rerun()

st.markdown("---")

# --- FILA 3: JUGADORES (Sin Formación/Personal) ---
st.subheader("👥 3. Jugadores Involucrados")

col_ofensa, col_defensa = st.columns(2)
passer, runner, receiver = "N/A", "N/A", "N/A"

with col_ofensa:
    st.write("🏈 **Ofensiva**")
    if st.session_state.resultado in ["Pass", "Incompleto", "Interception"]:
        passer = st.selectbox("🎯 QB", PASADORES)
        receiver = st.selectbox("👐 Receptor", RECEPTORES)
    elif st.session_state.resultado == "Rush":
        runner = st.selectbox("💨 Corredor", CORREDORES)
    elif st.session_state.resultado in ["Scramble", "Sack"]:
        passer = st.selectbox("🎯 QB", PASADORES)

with col_defensa:
    st.write("🛡️ **Defensiva**")
    defensor_1 = st.selectbox("💥 Tackle / Captura / Pase Def.", LISTA_DEFENSA)
    defensor_2 = st.selectbox("🤝 Asistencia (Opcional)", LISTA_DEFENSA)

st.markdown("---")

# --- FILA 4: GUARDADO RÁPIDO ---
st.subheader("⚡ 4. Guardado Rápido")
st.write("Toca un botón para registrar la yarda ganada y guardar la jugada al instante.")

ganancia_final = None

b1, b2, b3, b4, b5 = st.columns(5)
if b1.button("0 Yds", use_container_width=True, type="primary"): ganancia_final = 0
if b2.button("+3 Yds", use_container_width=True, type="primary"): ganancia_final = 3
if b3.button("+5 Yds", use_container_width=True, type="primary"): ganancia_final = 5
# Auto-calcula lo necesario para el 1er down
if b4.button(f"1er Down (+{st.session_state.distancia})", use_container_width=True, type="primary"): ganancia_final = st.session_state.distancia

ganancia_manual = st.number_input("O ingresa yardas manual (Usa '-' para capturas):", value=0, step=1)
if b5.button("✅ Guardar Manual", use_container_width=True, type="primary"):
    ganancia_final = ganancia_manual

# --- MOTOR LÓGICO DE GUARDADO ---
if ganancia_final is not None:
    if st.session_state.resultado == "Incompleto": ganancia_final = 0
    if st.session_state.resultado == "Sack" and ganancia_final > 0: ganancia_final = -ganancia_final 
    
    nueva_jugada = {
        "TITLE": periodo_actual,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "PERSONNEL": "", # Mantenemos la columna en blanco para que Hudl no rompa el CSV
        "HASH": hash_mark,
        "YARD LN": st.session_state.yarda_actual, 
        "DN": st.session_state.down,               
        "DIST": st.session_state.distancia,        
        "OFF FORM": "",
        "OFF PLAY": "",
        "RESULT": st.session_state.resultado, 
        "GAIN/LS": ganancia_final,
        "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "",
        "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
        "PASSER": passer.split(" - ")[0] if passer != "N/A" else "",
        "TACKLER 1": defensor_1.split(" - ")[0] if defensor_1 != "N/A" else "",
        "TACKLER 2": defensor_2.split(" - ")[0] if defensor_2 != "N/A" else ""
    }
    st.session_state.lista_jugadas.append(nueva_jugada)
    
    if st.session_state.resultado == "Interception":
        st.session_state.down = 1
        st.session_state.distancia = 10
    else:
        if ganancia_final >= st.session_state.distancia:
            st.session_state.down = 1
            st.session_state.distancia = 10
        else:
            st.session_state.down += 1
            st.session_state.distancia -= ganancia_final
            if st.session_state.down > 4:
                st.session_state.down = 1
                st.session_state.distancia = 10
                
    st.session_state.msg_exito = f"¡Jugada {len(st.session_state.lista_jugadas)} guardada! Avance: {ganancia_final} yds."
    st.rerun() 

st.markdown("<br><br>", unsafe_allow_html=True) 

# --- SECCIÓN DE CIERRE ---
st.markdown("---")
st.header("🏁 Terminar Entrenamiento")

if st.session_state.lista_jugadas:
    st.info(f"Has registrado un total de {len(st.session_state.lista_jugadas)} jugadas en esta sesión.")
    df_jugadas = pd.DataFrame(st.session_state.lista_jugadas)
    
    c_csv, c_excel = st.columns(2)
    with c_csv:
        csv_data = df_jugadas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV para Hudl", data=csv_data, file_name='hudl_import.csv', mime='text/csv', use_container_width=True)
    with c_excel:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_jugadas.to_excel(writer, index=False, sheet_name='Practica')
        st.download_button("📊 Descargar Tabla Excel", data=excel_buffer.getvalue(), file_name='reporte.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
else:
    st.warning("No hay jugadas registradas en esta sesión.")
