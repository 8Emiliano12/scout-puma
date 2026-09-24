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
# --- PASO 3: FORMACIÓN, JUGADORES Y RESULTADO ---
st.subheader("🏈 2. Formación y Desarrollo")

# 1. Cargamos tu Roster como una lista de opciones
# Agregamos "N/A" al principio por si en una jugada no hay corredor o pasador
ROSTER = [
    "N/A",
    "0 - Jioshi Alexander Morrison González (DL)", "1 - Raúl Rodrigo Blanco Ruiz (WR)", 
    "2 - Aarón Soriano Vacaseydel (DB)", "3 - Leonardo David Garza Peña Villamil (QB)", 
    "4 - Diego Mercado Sánchez (LB)", "5 - Julio César Hernández Hernández (PB)", 
    "6 - Abraham González López (LB)", "7 - Luis Miguel Bañuelos Medina (DB)", 
    "8 - Luis Higelin Castañón (DB)", "9 - Joaquín Aramis Carriles Palma (DL)", 
    "10 - Emiliano Sánchez Hernández (QB)", "11 - Raymundo Liceá Solano (DL)", 
    "12 - Christopher Bryan Cardona Padrón (WR)", "13 - Javier Santiago Vivas Rodríguez (WR)", 
    "14 - Luis Mario Medrano Silva (WR)", "15 - Emiliano Álvarez Reyes (CB)", 
    "16 - Ian Jeyden Aguilar Rodríguez (LB)", "17 - Jorge Emilio Corona Sandoval (QB)", 
    "18 - Jahdiel Alejandro Ponce Hernández (WR)", "19 - Jirvan Velasco González (LB)", 
    "21 - Armando Moreno Martínez (DB)", "22 - Juan Pablo Acosta Gutiérrez (LB)", 
    "23 - Rodrigo Pérez Rivera (RB)", "24 - David Ceballos Gutiérrez (CB)", 
    "25 - Diego Jack Cerda Álvarez (PB)", "26 - Luis Antonio Schrader Rodríguez (RB)", 
    "27 - Rodrigo Eugenio Villegas Delgado (LB)", "28 - Sergio Alejandro Cervantes Franzoni (LB)", 
    "29 - Santiago Yael Juárez González (CB)", "30 - Néstor Milan Cabrera Botello (CB)", 
    "31 - Juan Carlos Arreola Ramírez (LB)", "32 - Alonso Báez Jimarez (RB)", 
    "33 - Diego Ángel Bañuelos Medina (LB)", "34 - Emilio Melo Robles (RB)", 
    "35 - Hussein Manzur Santillán Ríos (RB)", "39 - Santiago de Cristo Saldaña Sarabia (LB)", 
    "40 - Yeshua Ocampo García (LB)", "42 - Alexis Trejo Caudillo (LB)", 
    "43 - Erick Yael Rodríguez Pérez (CB)", "44 - Manlio Fabio Hernández Hernández (RB)", 
    "51 - Francisco Nogueda Carmona (OL)", "52 - Diego Eliel Contreras Cervantez (LB)", 
    "53 - Jesús Hernández Álvarez (OL)", "54 - Victor Barrientos García (OL)", 
    "58 - Luis Vadhir Corona Torices (OL)", "59 - Óscar González Real (LB)", 
    "68 - Jesús Gael Puente Basañez (OL)", "70 - Carlos Eduardo Aparicio Gasca (OL)", 
    "71 - Pedro Brito Almaguer (OL)", "72 - Jesús Eduardo Trejo López (OL)", 
    "73 - Jesús Fernando Inzunza López (OL)", "74 - Daniel Romero Quezada (OL)", 
    "76 - Andrik Sánchez Benítez (OL)", "77 - Luis Enrique Fernández Vera (OL)", 
    "80 - Alan Andrés Mariano Malagón (PB)", "81 - César Adonai Román Castrejón (WR)", 
    "82 - Jonathan Michel Reyes Pérez (WR)", "83 - Ángel Santiago Reyes Pérez (WR)", 
    "84 - Bruno Said Granados Almeida (WR)", "87 - Emiliano Zamora Jerónimo (K)", 
    "88 - Kin Xanhun Villafuerte Rodríguez (WR)", "89 - Ollin Núñez Solano (OL)", 
    "90 - Rafael Uriel Saavedra Mendoza (LB)", "91 - Miguel Martínez Ayala (DL)", 
    "92 - Sergio Paul Bautista Balderrama (DL)", "94 - Juan Maximiliano Soriano Silva (DL)", 
    "95 - Saul Bautista Balderrama (DL)", "98 - Óscar Alan Miranda Becerril (WR)", 
    "99 - José Manuel Valdéz Orea (DL)"
]

col3, col4 = st.columns(2)

with col3:
    # Agrupamos lo previo al centro
    personnel = st.selectbox("Personal (PERSONNEL)", ["10", "11", "12", "20", "21", "22", "Otro"])
    off_form = st.text_input("Formación (OFF FORM)", placeholder="Ej. Trips Right")
    motion = st.text_input("Movimiento (MOTION)", placeholder="Ej. Jet")
    off_play = st.text_input("Jugada (OFF PLAY)", placeholder="Ej. Zone Right")

with col4:
    # Agrupamos resultado y jugadores
    resultado = st.radio("Resultado (RESULT)", ["Rush", "Pass", "Drop", "Inter."], horizontal=True)
    ganancia = st.number_input("Yardas Ganadas / Perdidas (GAIN/LS)", value=0, step=1)
    
    # Aquí usamos los selectbox con el Roster. ¡Tienen autocompletado nativo!
    passer = st.selectbox("QB (PASSER)", ROSTER, index=0)
    runner = st.selectbox("RB (RUNNER)", ROSTER, index=0)
    receiver = st.selectbox("WR (RECEIVER)", ROSTER, index=0)

st.markdown("---")

# --- PASO 4: GUARDAR LA JUGADA ---
if st.button("📝 GUARDAR JUGADA", use_container_width=True, type="primary"):
    
    nueva_jugada = {
        "TITLE": periodo_actual,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "PERSONNEL": personnel,
        "HASH": hash_mark,        
        "YARD LN": st.session_state.yarda_actual, 
        "DN": down,               
        "DIST": distancia,        
        "OFF FORM": off_form,
        "MOTION": motion,
        "OFF PLAY": off_play,
        "RESULT": resultado,
        "GAIN/LS": ganancia,
        "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "", # Extrae solo el número
        "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
        "PASSER": passer.split(" - ")[0] if passer != "N/A" else ""
    }
    
    st.session_state.lista_jugadas.append(nueva_jugada)
    st.success(f"¡Jugada {len(st.session_state.lista_jugadas)} guardada correctamente en la yarda {st.session_state.yarda_actual}!")
