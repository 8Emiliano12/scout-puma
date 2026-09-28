import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS DE MÁXIMA COMPACTACIÓN ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Eliminar márgenes para aprovechar el 100% de la pantalla del iPad */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;} /* Oculta la barra superior de Streamlit */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Botones compactos y ágiles */
    div.stButton > button {
        height: 50px; /* Un poco más delgados para que quepa todo */
        font-size: 16px !important;
        font-weight: bold;
        border-radius: 8px;
        background-color: #f0f2f6;
        color: black;
        border: 2px solid #dcdcdc;
        padding: 0px !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1F4E78;
        color: white;
        border: none;
    }
    /* Botones de guardado más llamativos */
    .btn-guardar > div > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border: none !important;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {
        font-size: 16px !important;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0px !important;
    }
    /* Número de jugada gigante en la esquina */
    [data-testid="stMetricValue"] {
        font-size: 45px !important;
        color: #1F4E78;
        line-height: 1 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1.5 SCRIPT PARA BLOQUEAR EL TECLADO VIRTUAL EN TABLETS ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    function disableKeyboard() {
        const inputs = doc.querySelectorAll('div[data-baseweb="select"] input');
        inputs.forEach(inp => {
            inp.setAttribute('inputmode', 'none');
            inp.setAttribute('autocomplete', 'off'); 
        });
    }
    disableKeyboard();
    setInterval(disableKeyboard, 500);
    </script>
    """,
    height=0,
    width=0
)

# --- 2. INICIALIZACIÓN DE MEMORIA ---
if 'lista_jugadas' not in st.session_state: st.session_state.lista_jugadas = []
if 'yarda_actual' not in st.session_state: st.session_state.yarda_actual = 20
if 'territorio' not in st.session_state: st.session_state.territorio = "Propio"
if 'modo_avance' not in st.session_state: st.session_state.modo_avance = "🏈 Drive"
if 'down' not in st.session_state: st.session_state.down = 1
if 'distancia' not in st.session_state: st.session_state.distancia = 10
if 'msg_exito' not in st.session_state: st.session_state.msg_exito = ""
if 'resultado' not in st.session_state: st.session_state.resultado = "Pass"
if 'direccion_actual' not in st.session_state: st.session_state.direccion_actual = "Alberca"
if 'hash_mark' not in st.session_state: st.session_state.hash_mark = "M"

# --- LISTAS DEL ROSTER ---
LISTA_QB = ["N/A", "3 - Garza", "10 - Sánchez", "17 - Corona"]
LISTA_RB = ["N/A", "23 - Pérez", "26 - Schrader", "32 - Báez", "34 - Melo", "35 - Santillán", "44 - Hernández"]
LISTA_WR = ["N/A", "1 - Blanco", "12 - Cardona", "13 - Vivas", "14 - Medrano", "18 - Ponce", "81 - Román", "82 - Reyes", "83 - Reyes", "84 - Granados", "88 - Villafuerte", "98 - Miranda"]
LISTA_DL = ["0 - Morrison", "9 - Carriles", "11 - Liceá", "91 - Martínez", "92 - Bautista", "94 - Soriano", "95 - Bautista", "99 - Valdéz"]
LISTA_OL = ["51 - Nogueda", "53 - Hernández", "54 - Barrientos", "58 - Corona", "68 - Puente", "70 - Aparicio", "71 - Brito", "72 - Trejo", "73 - Inzunza", "74 - Romero", "76 - Sánchez", "77 - Fernández", "89 - Núñez"]
LISTA_PB_K = ["5 - Hernández", "25 - Cerda", "80 - Mariano", "87 - Zamora"]

WR_LIMPIO = [x for x in LISTA_WR if x != "N/A"]
RB_LIMPIO = [x for x in LISTA_RB if x != "N/A"]
QB_LIMPIO = [x for x in LISTA_QB if x != "N/A"]

PASADORES = LISTA_QB + LISTA_PB_K + WR_LIMPIO + RB_LIMPIO
CORREDORES = LISTA_RB + WR_LIMPIO + QB_LIMPIO + LISTA_PB_K
RECEPTORES = LISTA_WR + RB_LIMPIO + LISTA_DL + LISTA_PB_K + LISTA_OL

LISTA_DEFENSA = [
    "N/A", "0 - Morrison", "2 - Soriano", "4 - Mercado", "5 - Hernández", "6 - González", 
    "7 - Bañuelos", "8 - Higelin", "9 - Carriles", "11 - Liceá", "15 - Álvarez", 
    "16 - Aguilar", "19 - Velasco", "21 - Moreno", "22 - Acosta", "24 - Ceballos", 
    "25 - Cerda", "27 - Villegas", "28 - Cervantes", "29 - Juárez", "30 - Cabrera", 
    "31 - Arreola", "33 - Bañuelos", "39 - Saldaña", "40 - Ocampo", "42 - Trejo", 
    "43 - Rodríguez", "52 - Contreras", "59 - González", "80 - Mariano", "87 - Zamora", 
    "90 - Saavedra", "91 - Martínez", "92 - Bautista", "94 - Soriano", "95 - Bautista", "99 - Valdéz"
]

# --- 3. HEADER COMPACTO ---
col_tit, col_per, col_num = st.columns([1.5, 2, 0.5])
with col_tit:
    st.markdown("<h2 style='margin-top:-20px;'>🏈 Pumas CU Scout</h2>", unsafe_allow_html=True)
with col_per:
    periodo_actual = st.selectbox("⏱️ PERIODO", ["TEAM", "SKELL OFENSA", "SKELL DEFENSA", "2DO DOWN RUN FIT", "RED ZONE", "OTRO"], label_visibility="collapsed")
with col_num:
    st.metric("JUGADA", len(st.session_state.lista_jugadas) + 1)

if st.session_state.msg_exito:
    st.success(st.session_state.msg_exito)
    st.session_state.msg_exito = ""

st.markdown("---")

# --- 4. DISEÑO DE 3 COLUMNAS PARA CERO SCROLL ---
col_izq, col_cen, col_der = st.columns([1.2, 1.3, 1])

# ==========================================
# COLUMNA IZQUIERDA: CONTEXTO DEL CAMPO
# ==========================================
with col_izq:
    st.markdown("#### 📍 Contexto")
    
    t1, t2 = st.columns(2)
    if t1.button("📍 Fijo", type="primary" if st.session_state.modo_avance == "📍 Fijo" else "secondary", use_container_width=True):
        st.session_state.modo_avance = "📍 Fijo"; st.rerun()
    if t2.button("🏈 Drive", type="primary" if st.session_state.modo_avance == "🏈 Drive" else "secondary", use_container_width=True):
        st.session_state.modo_avance = "🏈 Drive"; st.rerun()
        
    es_drive = (st.session_state.modo_avance == "🏈 Drive")
    
    t3, t4 = st.columns(2)
    if t3.button("Propio", type="primary" if st.session_state.territorio == "Propio" else "secondary", use_container_width=True, disabled=es_drive):
        st.session_state.territorio = "Propio"; st.rerun()
    if t4.button("Rival", type="primary" if st.session_state.territorio == "Rival" else "secondary", use_container_width=True, disabled=es_drive):
        st.session_state.territorio = "Rival"; st.rerun()
        
    yb1, yb2, yb3, yb4, yb5 = st.columns(5)
    if yb1.button("10", disabled=es_drive, use_container_width=True): st.session_state.yarda_actual = 10; st.rerun()
    if yb2.button("20", disabled=es_drive, use_container_width=True): st.session_state.yarda_actual = 20; st.rerun()
    if yb3.button("30", disabled=es_drive, use_container_width=True): st.session_state.yarda_actual = 30; st.rerun()
    if yb4.button("40", disabled=es_drive, use_container_width=True): st.session_state.yarda_actual = 40; st.rerun()
    if yb5.button("50", disabled=es_drive, use_container_width=True): st.session_state.yarda_actual = 50; st.rerun()

    st.session_state.yarda_actual = st.slider("Yarda exacta", min_value=1, max_value=50, value=st.session_state.yarda_actual, disabled=es_drive, label_visibility="collapsed")
    
    dw1, dw2, dw3, dw4 = st.columns(4)
    if dw1.button("1D", type="primary" if st.session_state.down == 1 else "secondary", use_container_width=True, disabled=es_drive): st.session_state.down = 1; st.rerun()
    if dw2.button("2D", type="primary" if st.session_state.down == 2 else "secondary", use_container_width=True, disabled=es_drive): st.session_state.down = 2; st.rerun()
    if dw3.button("3D", type="primary" if st.session_state.down == 3 else "secondary", use_container_width=True, disabled=es_drive): st.session_state.down = 3; st.rerun()
    if dw4.button("4D", type="primary" if st.session_state.down == 4 else "secondary", use_container_width=True, disabled=es_drive): st.session_state.down = 4; st.rerun()
    
    dist_val = st.number_input("Distancia", min_value=1, value=st.session_state.distancia, disabled=es_drive)
    if not es_drive: st.session_state.distancia = dist_val

    h1, h2, h3, h4, h5 = st.columns([1,1,1, 1.2,1.2])
    if h1.button("L", type="primary" if st.session_state.hash_mark == "L" else "secondary", use_container_width=True): st.session_state.hash_mark = "L"; st.rerun()
    if h2.button("M", type="primary" if st.session_state.hash_mark == "M" else "secondary", use_container_width=True): st.session_state.hash_mark = "M"; st.rerun()
    if h3.button("R", type="primary" if st.session_state.hash_mark == "R" else "secondary", use_container_width=True): st.session_state.hash_mark = "R"; st.rerun()
    if h4.button("Alberca", type="primary" if st.session_state.direccion_actual == "Alberca" else "secondary", use_container_width=True): st.session_state.direccion_actual = "Alberca"; st.rerun()
    if h5.button("Canchas", type="primary" if st.session_state.direccion_actual == "Canchas" else "secondary", use_container_width=True): st.session_state.direccion_actual = "Canchas"; st.rerun()

# ==========================================
# COLUMNA CENTRAL: JUGADA Y JUGADORES
# ==========================================
with col_cen:
    st.markdown("#### 🏁 Desarrollo")
    
    r1, r2 = st.columns(2)
    with r1:
        if st.button("🏈 Pase", type="primary" if st.session_state.resultado == "Pass" else "secondary", use_container_width=True): st.session_state.resultado = "Pass"; st.rerun()
        if st.button("🏃‍♂️ Scramble", type="primary" if st.session_state.resultado == "Scramble" else "secondary", use_container_width=True): st.session_state.resultado = "Scramble"; st.rerun()
        if st.button("💥 Sack", type="primary" if st.session_state.resultado == "Sack" else "secondary", use_container_width=True): st.session_state.resultado = "Sack"; st.rerun()
    with r2:
        if st.button("🏃 Carrera", type="primary" if st.session_state.resultado == "Rush" else "secondary", use_container_width=True): st.session_state.resultado = "Rush"; st.rerun()
        if st.button("❌ Incompleto", type="primary" if st.session_state.resultado == "Incompleto" else "secondary", use_container_width=True): st.session_state.resultado = "Incompleto"; st.rerun()
        if st.button("🦅 INT", type="primary" if st.session_state.resultado == "Interception" else "secondary", use_container_width=True): st.session_state.resultado = "Interception"; st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    passer, runner, receiver = "N/A", "N/A", "N/A"
    
    if st.session_state.resultado in ["Pass", "Incompleto", "Interception"]:
        passer = st.selectbox("🎯 QB", PASADORES)
        receiver = st.selectbox("👐 Receptor", RECEPTORES)
    elif st.session_state.resultado == "Rush":
        runner = st.selectbox("💨 Corredor", CORREDORES)
        st.write("") 
    elif st.session_state.resultado in ["Scramble", "Sack"]:
        passer = st.selectbox("🎯 QB", PASADORES)
        st.write("")

    defensor_1 = st.selectbox("💥 Tackle principal / Pase Def.", LISTA_DEFENSA)
    defensor_2 = st.selectbox("🤝 Asistencia (Opcional)", LISTA_DEFENSA)

# ==========================================
# COLUMNA DERECHA: CIERRE Y GUARDADO
# ==========================================
with col_der:
    st.markdown("#### ⚡ Resultado y Guardar")
    ganancia_final = None
    distancia_al_td = (100 - st.session_state.yarda_actual) if st.session_state.territorio == "Propio" else st.session_state.yarda_actual

    st.markdown('<div class="btn-guardar">', unsafe_allow_html=True)
    if st.button("❌ 0 Yds (Incompleto/Línea)", use_container_width=True): ganancia_final = 0
    if st.button("➕ +3 Yds", use_container_width=True): ganancia_final = 3
    if st.button("➕ +5 Yds", use_container_width=True): ganancia_final = 5
    if st.button(f"🚀 1er Down (+{st.session_state.distancia})", use_container_width=True): ganancia_final = st.session_state.distancia
    if st.button("🔥 TOUCHDOWN", use_container_width=True): ganancia_final = distancia_al_td
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c_m1, c_m2 = st.columns([1, 1.5])
    with c_m1:
        ganancia_manual = st.number_input("Manual", value=0, step=1, label_visibility="collapsed")
    with c_m2:
        if st.button("✅ Guardar", use_container_width=True, type="primary"):
            ganancia_final = ganancia_manual

# --- MOTOR LÓGICO Y MATEMÁTICO (Oculto de la UI) ---
if ganancia_final is not None:
    if st.session_state.resultado == "Incompleto": ganancia_final = 0
    if st.session_state.resultado == "Sack" and ganancia_final > 0: ganancia_final = -ganancia_final 
    
    is_td = False
    if ganancia_final >= distancia_al_td and st.session_state.resultado in ["Pass", "Rush", "Scramble"]:
        is_td = True
        ganancia_final = distancia_al_td 
        
    resultado_str = st.session_state.resultado + (" TD" if is_td else "")
    yard_str = "50" if st.session_state.yarda_actual == 50 else f"{st.session_state.territorio[0]}{st.session_state.yarda_actual}"
    
    nueva_jugada = {
        "TITLE": periodo_actual,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "DIRECTION": st.session_state.direccion_actual, 
        "HASH": st.session_state.hash_mark, 
        "YARD LN": yard_str, 
        "DN": st.session_state.down,               
        "DIST": st.session_state.distancia,        
        "RESULT": resultado_str, 
        "GAIN/LS": ganancia_final,
        "RUNNER": runner.split(" - ")[0] if runner != "N/A" else "",
        "RECEIVER": receiver.split(" - ")[0] if receiver != "N/A" else "",
        "PASSER": passer.split(" - ")[0] if passer != "N/A" else "",
        "TACKLER 1": defensor_1.split(" - ")[0] if defensor_1 != "N/A" else "",
        "TACKLER 2": defensor_2.split(" - ")[0] if defensor_2 != "N/A" else ""
    }
    st.session_state.lista_jugadas.append(nueva_jugada)
    
    if st.session_state.modo_avance == "🏈 Drive":
        if st.session_state.resultado == "Interception" or is_td:
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
                    
        abs_yard = st.session_state.yarda_actual if st.session_state.territorio == "Propio" else 100 - st.session_state.yarda_actual
        new_abs = abs_yard + ganancia_final
        
        if new_abs >= 100 or new_abs <= 0:
            st.session_state.territorio = "Propio"
            st.session_state.yarda_actual = 20 
        else:
            if new_abs <= 50:
                st.session_state.territorio = "Propio"
                st.session_state.yarda_actual = new_abs
            else:
                st.session_state.territorio = "Rival"
                st.session_state.yarda_actual = 100 - new_abs
                
    st.session_state.msg_exito = f"¡Jugada {len(st.session_state.lista_jugadas)} guardada! Avance: {ganancia_final} yds."
    st.rerun() 

st.markdown("---")

# --- DESCARGAS (Ocultas hasta que haya jugadas para ahorrar espacio visual) ---
if st.session_state.lista_jugadas:
    with st.expander("📥 Exportar Práctica o Borrar Sesión", expanded=False):
        df_jugadas = pd.DataFrame(st.session_state.lista_jugadas)
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        nombre_practica = periodo_actual.replace(" ", "_")
        
        c_csv, c_excel, c_del = st.columns(3)
        with c_csv:
            csv_data = df_jugadas.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar CSV (Hudl)", data=csv_data, file_name=f"PumasCU_{nombre_practica}_{fecha_hoy}.csv", mime='text/csv', use_container_width=True)
        with c_excel:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_jugadas.to_excel(writer, index=False, sheet_name='Practica')
            st.download_button("Descargar Excel", data=excel_buffer.getvalue(), file_name=f"PumasCU_{nombre_practica}_{fecha_hoy}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
        with c_del:
            if st.button("🗑️ Borrar Práctica", use_container_width=True):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()
