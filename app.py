import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    div.stButton > button {
        height: 60px;
        font-size: 20px !important;
        font-weight: bold;
        border-radius: 10px;
        background-color: #1F4E78;
        color: white;
    }
    div.stDownloadButton > button {
        height: 80px;
        font-size: 20px !important;
        background-color: #2E7D32;
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
if 'personnel' not in st.session_state: st.session_state.personnel = "10"
if 'off_form' not in st.session_state: st.session_state.off_form = ""
if 'msg_exito' not in st.session_state: st.session_state.msg_exito = ""

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

# Mostrar mensaje de éxito tras un recargo rápido
if st.session_state.msg_exito:
    st.success(st.session_state.msg_exito)
    st.session_state.msg_exito = ""

periodo_actual = st.selectbox("⏱️ PERIODO DE PRÁCTICA", ["SKELL OFENSA", "2DO DOWN RUN FIT", "RED ZONE", "TEAM", "OTRO"])
st.markdown("---")

# --- FILA 1: POSICIÓN Y CONTEXTO (Automático) ---
st.subheader("📍 1. Posición y Contexto")
col_y, col_d = st.columns([2, 1])

with col_y:
    st.session_state.yarda_actual = st.slider("Línea de Golpeo (Yarda estática)", min_value=1, max_value=50, value=st.session_state.yarda_actual)
    hash_mark = st.radio("➖ Hash", ["L", "M", "R"], horizontal=True)

with col_d:
    d_c1, d_c2 = st.columns(2)
    # Los widgets toman su valor directamente de la memoria, lo que permite el auto-cálculo
    with d_c1:
        down = st.number_input("⬇️ Down", min_value=1, max_value=4, key="down")
    with d_c2:
        distancia = st.number_input("📏 Distancia", min_value=1, key="distancia")

st.markdown("---")

# --- FILA 2: RENDERIZADO CONDICIONAL ---
st.subheader("📋 2. Desarrollo de la Jugada")

# Elegir primero el resultado limpia visualmente la pantalla
resultado = st.radio("🏁 Resultado (Define qué jugadores se muestran)", 
                     ["Pass (Pase)", "Rush (Carrera)", "Scramble", "Incompleto", "Sack", "Interception"], 
                     horizontal=True)

col_ofensa, col_defensa = st.columns(2)
passer, runner, receiver = "N/A", "N/A", "N/A"

with col_ofensa:
    # Memoria persistente para Formación y Personal
    o_c1, o_c2 = st.columns(2)
    with o_c1:
        personnel = st.selectbox("👥 Personal", ["10", "11", "12", "20", "21", "22", "Otro"], key="personnel")
    with o_c2:
        off_form = st.text_input("📝 Formación", key="off_form")
        
    off_play = st.text_input("🏃 Jugada")
    
    st.write("🏈 **Involucrados**")
    # LÓGICA DE CONDICIONALES: Oculta a los jugadores que no participan en el tipo de jugada
    if resultado in ["Pass (Pase)", "Incompleto", "Interception"]:
        passer = st.selectbox("🎯 QB", PASADORES)
        receiver = st.selectbox("👐 Receptor", RECEPTORES)
    elif resultado == "Rush (Carrera)":
        runner = st.selectbox("💨 Corredor", CORREDORES)
    elif resultado in ["Scramble", "Sack"]:
        passer = st.selectbox("🎯 QB", PASADORES)

with col_defensa:
    st.write("🛡️ **Defensiva**")
    defensor_1 = st.selectbox("💥 Tackle / Captura / Pase Def.", LISTA_DEFENSA)
    defensor_2 = st.selectbox("🤝 Asistencia (Opcional)", LISTA_DEFENSA)

st.markdown("---")

# --- FILA 3: BOTONES DE GUARDADO RÁPIDO Y CÁLCULO ---
st.subheader("⚡ 3. Guardado Rápido")
st.write("Toca un botón para registrar la yarda ganada y avanzar al siguiente Down automáticamente.")

# Variables para procesar la jugada
ganancia_final = None

b1, b2, b3, b4, b5 = st.columns(5)
if b1.button("Incompleto (0)", use_container_width=True): ganancia_final = 0
if b2.button("+3 Yds", use_container_width=True): ganancia_final = 3
if b3.button("+5 Yds", use_container_width=True): ganancia_final = 5
if b4.button("1er Down (+10)", use_container_width=True): ganancia_final = 10

ganancia_manual = st.number_input("O ingresa yardas manual (Usa '-' para capturas):", value=0, step=1)
if b5.button("✅ Guardar Manual", use_container_width=True):
    ganancia_final = ganancia_manual

# --- MOTOR LÓGICO DE LA APLICACIÓN ---
if ganancia_final is not None:
    # 1. Reglas forzadas según el resultado
    if resultado == "Incompleto": ganancia_final = 0
    if resultado == "Sack" and ganancia_final > 0: ganancia_final = -ganancia_final # Forzar negativo
    
    # 2. Registrar la jugada
    nueva_jugada = {
        "TITLE": periodo_actual,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "PERSONNEL": st.session_state.personnel,
        "HASH": hash_mark,
        "YARD LN": st.session_state.yarda_actual, 
        "DN": st.session_state.down,               
        "DIST": st.session_state.distancia,        
        "OFF FORM": st.session_state.off_form,
        "OFF PLAY": off_play,
        "RESULT": resultado.split(" ")[0], 
        "GAIN/LS": ganancia_final,
        "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "",
        "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
        "PASSER": passer.split(" - ")[0] if passer != "N/A" else "",
        "TACKLER 1": defensor_1.split(" - ")[0] if defensor_1 != "N/A" else "",
        "TACKLER 2": defensor_2.split(" - ")[0] if defensor_2 != "N/A" else ""
    }
    st.session_state.lista_jugadas.append(nueva_jugada)
    
    # 3. Calcular el próximo Down y Distancia
    if resultado == "Interception":
        st.session_state.down = 1
        st.session_state.distancia = 10
    else:
        if ganancia_final >= st.session_state.distancia:
            st.session_state.down = 1
            st.session_state.distancia = 10
        else:
            st.session_state.down += 1
            st.session_state.distancia -= ganancia_final
            # Si superó el 4to down, se resetea la serie
            if st.session_state.down > 4:
                st.session_state.down = 1
                st.session_state.distancia = 10
                
    # 4. Mensaje y Recarga instantánea
    st.session_state.msg_exito = f"¡Jugada {len(st.session_state.lista_jugadas)} guardada! Avance: {ganancia_final} yds."
    st.rerun() # Esto refresca la pantalla para mostrar el nuevo Down calculado

st.markdown("<br><br><br>", unsafe_allow_html=True) # Espacio en blanco al final

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
    st.warning("No hay jugadas registradas en esta sesión. Comienza a registrar arriba para habilitar las descargas.")
