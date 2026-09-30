import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS DE MÁXIMA COMPACTACIÓN ---
st.set_page_config(page_title="Pumas CU Scout", page_icon="🏈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Estilos para Botones normales y Botones de Popover (Menús) */
    div.stButton > button, div[data-testid="stPopover"] > button {
        height: 50px; 
        font-size: 16px !important;
        font-weight: bold;
        border-radius: 8px;
        background-color: #f0f2f6;
        color: black;
        border: 2px solid #dcdcdc;
        padding: 0px 10px !important;
    }
    /* Alinear el texto a la izquierda en los menús para que parezcan selectores reales */
    div[data-testid="stPopover"] > button {
        justify-content: flex-start;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1F4E78;
        color: white;
        border: none;
    }
    .btn-guardar > div > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border: none !important;
    }
    .stTextInput label, .stNumberInput label, .stSlider label {
        font-size: 16px !important;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0px !important;
    }
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

# --- 2. INICIALIZACIÓN DE MEMORIA Y ROSTERS DINÁMICOS ---
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

# Variables de selección de menús
if 'periodo_base' not in st.session_state: st.session_state.periodo_base = "TEAM"
if 'down_drill' not in st.session_state: st.session_state.down_drill = "N/A"
if 'passer_sel' not in st.session_state: st.session_state.passer_sel = "N/A"
if 'receiver_sel' not in st.session_state: st.session_state.receiver_sel = "N/A"
if 'runner_sel' not in st.session_state: st.session_state.runner_sel = "N/A"
if 'd1_sel' not in st.session_state: st.session_state.d1_sel = "N/A"
if 'd2_sel' not in st.session_state: st.session_state.d2_sel = "N/A"

# Inicialización del Roster en memoria
if 'roster_qb' not in st.session_state: st.session_state.roster_qb = ["N/A", "3 - Leonardo Garza", "10 - Emiliano Sánchez", "17 - Jorge Corona"]
if 'roster_rb' not in st.session_state: st.session_state.roster_rb = ["N/A", "23 - Rodrigo Pérez", "26 - Luis Schrader", "32 - Alonso Báez", "34 - Emilio Melo", "35 - Hussein Santillán", "44 - Manlio Hernández"]
if 'roster_wr' not in st.session_state: st.session_state.roster_wr = ["N/A", "1 - Raúl Blanco", "12 - Christopher Cardona", "13 - Javier Vivas", "14 - Luis Medrano", "18 - Jahdiel Ponce", "81 - César Román", "82 - Jonathan Reyes", "83 - Ángel Reyes", "84 - Bruno Granados", "88 - Kin Villafuerte", "98 - Óscar Miranda"]
if 'roster_pb' not in st.session_state: st.session_state.roster_pb = ["5 - Julio Hernández", "25 - Diego Cerda", "80 - Alan Mariano", "87 - Emiliano Zamora"]
if 'roster_def' not in st.session_state: st.session_state.roster_def = [
    "N/A", "0 - Jioshi Morrison", "2 - Aarón Soriano", "4 - Diego Mercado", "6 - Abraham González", "7 - Luis Bañuelos", 
    "8 - Luis Higelin", "9 - Joaquín Carriles", "11 - Raymundo Liceá", "15 - Emiliano Álvarez", "16 - Ian Aguilar", 
    "19 - Jirvan Velasco", "21 - Armando Moreno", "22 - Juan Acosta", "24 - David Ceballos", "27 - Rodrigo Villegas", 
    "28 - Sergio Cervantes", "29 - Santiago Juárez", "30 - Néstor Cabrera", "31 - Juan Arreola", "33 - Diego Bañuelos", 
    "39 - Santiago Saldaña", "40 - Yeshua Ocampo", "42 - Alexis Trejo", "43 - Erick Rodríguez", "52 - Diego Contreras", 
    "59 - Óscar González", "90 - Rafael Saavedra", "91 - Miguel Martínez", "92 - Sergio Bautista", "94 - Juan Soriano", 
    "95 - Saul Bautista", "99 - José Valdéz"
]

WR_LIMPIO = [x for x in st.session_state.roster_wr if x != "N/A"]
RB_LIMPIO = [x for x in st.session_state.roster_rb if x != "N/A"]

PASADORES = st.session_state.roster_qb + ["Otro..."]
CORREDORES = st.session_state.roster_rb + ["Otro..."]
RECEPTORES = st.session_state.roster_wr + RB_LIMPIO + st.session_state.roster_pb + ["Otro..."]
LISTA_DEFENSA = st.session_state.roster_def + ["Otro..."]

# --- 3. HEADER COMPACTO ---
col_tit, col_per, col_dwn, col_num = st.columns([1.2, 1.4, 0.7, 0.7])
with col_tit:
    st.markdown("<h2 style='margin-top:-10px;'>🏈 Pumas CU Scout</h2>", unsafe_allow_html=True)
with col_per:
    with st.popover(f"⏱️ {st.session_state.periodo_base}", use_container_width=True):
        st.session_state.periodo_base = st.radio("Periodo", ["TEAM", "BATTLE DOWN", "SKELL OFENSA", "SKELL DEFENSA", "2DO DOWN RUN FIT", "RED ZONE", "OTRO"], label_visibility="collapsed")
        if st.session_state.periodo_base == "OTRO":
            periodo_actual = st.text_input("Nombre de la práctica", key="per_otro", placeholder="Ej: Especiales")
            if not periodo_actual: periodo_actual = "OTRO"
        else:
            periodo_actual = st.session_state.periodo_base

with col_dwn:
    with st.popover(f"🎯 {st.session_state.down_drill}", use_container_width=True):
        st.session_state.down_drill = st.radio("Drill", ["N/A", "1D", "2D", "3D", "4D"], label_visibility="collapsed")

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
        if st.button("👐 Drop", type="primary" if st.session_state.resultado == "Drop" else "secondary", use_container_width=True): st.session_state.resultado = "Drop"; st.rerun()
    with r2:
        if st.button("🏃 Carrera", type="primary" if st.session_state.resultado == "Rush" else "secondary", use_container_width=True): st.session_state.resultado = "Rush"; st.rerun()
        if st.button("❌ Incompleto", type="primary" if st.session_state.resultado == "Incompleto" else "secondary", use_container_width=True): st.session_state.resultado = "Incompleto"; st.rerun()
        if st.button("🦅 INT", type="primary" if st.session_state.resultado == "Interception" else "secondary", use_container_width=True): st.session_state.resultado = "Interception"; st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # MENÚS CON POPOVER (Botones 100% inmunes al teclado del iPad)
    if st.session_state.resultado in ["Pass", "Incompleto", "Interception", "Drop"]:
        with st.popover(f"🎯 QB: {st.session_state.passer_sel}", use_container_width=True):
            st.session_state.passer_sel = st.radio("QB", PASADORES, label_visibility="collapsed")
            if st.session_state.passer_sel == "Otro...":
                st.text_input("Ingresa el QB", key="qb_otro")
                
        with st.popover(f"👐 Rec: {st.session_state.receiver_sel}", use_container_width=True):
            st.session_state.receiver_sel = st.radio("Receptor", RECEPTORES, label_visibility="collapsed")
            if st.session_state.receiver_sel == "Otro...":
                st.text_input("Ingresa Receptor", key="rec_otro")
            
    elif st.session_state.resultado == "Rush":
        with st.popover(f"💨 RB: {st.session_state.runner_sel}", use_container_width=True):
            st.session_state.runner_sel = st.radio("Corredor", CORREDORES, label_visibility="collapsed")
            if st.session_state.runner_sel == "Otro...":
                st.text_input("Ingresa el Corredor", key="run_otro")
        st.write("") 
        
    elif st.session_state.resultado in ["Scramble", "Sack"]:
        with st.popover(f"🎯 QB: {st.session_state.passer_sel}", use_container_width=True):
            st.session_state.passer_sel = st.radio("QB", PASADORES, label_visibility="collapsed")
            if st.session_state.passer_sel == "Otro...":
                st.text_input("Ingresa el QB", key="qb_otro")
        st.write("")

    with st.popover(f"💥 TKL 1: {st.session_state.d1_sel}", use_container_width=True):
        st.session_state.d1_sel = st.radio("Tackle 1", LISTA_DEFENSA, label_visibility="collapsed")
        if st.session_state.d1_sel == "Otro...":
            st.text_input("Ingresa Tackle 1", key="d1_otro")
            
    with st.popover(f"🤝 TKL 2: {st.session_state.d2_sel}", use_container_width=True):
        st.session_state.d2_sel = st.radio("Tackle 2", LISTA_DEFENSA, label_visibility="collapsed")
        if st.session_state.d2_sel == "Otro...":
            st.text_input("Ingresa Tackle 2", key="d2_otro")

# ==========================================
# COLUMNA DERECHA: CIERRE Y GUARDADO
# ==========================================
with col_der:
    st.markdown("#### ⚡ Resultado y Guardar")
    ganancia_final = None
    distancia_al_td = (100 - st.session_state.yarda_actual) if st.session_state.territorio == "Propio" else st.session_state.yarda_actual

    st.markdown('<div class="btn-guardar">', unsafe_allow_html=True)
    if st.button("❌ 0 Yds (Incompleto/Drop/Línea)", use_container_width=True): ganancia_final = 0
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

# --- MOTOR LÓGICO Y MATEMÁTICO ---
if ganancia_final is not None:
    # 1. Recuperar valores finales de jugadores
    p_sel = st.session_state.passer_sel
    r_sel = st.session_state.receiver_sel
    rn_sel = st.session_state.runner_sel
    d1_s = st.session_state.d1_sel
    d2_s = st.session_state.d2_sel

    p_val = st.session_state.get('qb_otro', '') if p_sel == "Otro..." else p_sel
    r_val = st.session_state.get('rec_otro', '') if r_sel == "Otro..." else r_sel
    rn_val = st.session_state.get('run_otro', '') if rn_sel == "Otro..." else rn_sel
    d1_val = st.session_state.get('d1_otro', '') if d1_s == "Otro..." else d1_s
    d2_val = st.session_state.get('d2_otro', '') if d2_s == "Otro..." else d2_s

    # 2. Agregar al roster en memoria si son nuevos
    if p_sel == "Otro..." and p_val and p_val not in st.session_state.roster_qb: st.session_state.roster_qb.append(p_val)
    if r_sel == "Otro..." and r_val and r_val not in st.session_state.roster_wr: st.session_state.roster_wr.append(r_val)
    if rn_sel == "Otro..." and rn_val and rn_val not in st.session_state.roster_rb: st.session_state.roster_rb.append(rn_val)
    if d1_s == "Otro..." and d1_val and d1_val not in st.session_state.roster_def: st.session_state.roster_def.append(d1_val)
    if d2_s == "Otro..." and d2_val and d2_val not in st.session_state.roster_def: st.session_state.roster_def.append(d2_val)

    # 3. Lógica de ganancia
    if st.session_state.resultado in ["Incompleto", "Drop"]: 
        ganancia_final = 0
    if st.session_state.resultado == "Sack" and ganancia_final > 0: 
        ganancia_final = -ganancia_final 
    
    is_td = False
    if ganancia_final >= distancia_al_td and st.session_state.resultado in ["Pass", "Rush", "Scramble"]:
        is_td = True
        ganancia_final = distancia_al_td 
        
    resultado_str = st.session_state.resultado + (" TD" if is_td else "")
    
    # 4. Yardas formato negativo en Propia, normal en Rival (Hudl format)
    if st.session_state.yarda_actual == 50:
        yard_str = "50"
    else:
        yard_str = f"-{st.session_state.yarda_actual}" if st.session_state.territorio == "Propio" else f"{st.session_state.yarda_actual}"
    
    # 5. Columna PLAY TYPE
    play_type_str = "Run" if st.session_state.resultado == "Rush" else "Pass"
    
    titulo_exportacion = f"{periodo_actual} {st.session_state.down_drill}" if st.session_state.down_drill != "N/A" else periodo_actual
    
    def get_num(name):
        return name.split(" - ")[0] if name not in ["N/A", ""] else ""
    
    nueva_jugada = {
        "TITLE": titulo_exportacion,  
        "PLAY #": len(st.session_state.lista_jugadas) + 1,
        "PLAY TYPE": play_type_str,
        "DIRECTION": st.session_state.direccion_actual, 
        "HASH": st.session_state.hash_mark, 
        "YARD LN": yard_str, 
        "DOWN": st.session_state.down,
        "DIST": st.session_state.distancia,        
        "RESULT": resultado_str, 
        "GAIN/LS": ganancia_final,
        "RUNNER": get_num(rn_val),
        "RECEIVER": get_num(r_val),
        "PASSER": get_num(p_val),
        "TACKLER 1": get_num(d1_val),
        "TACKLER 2": get_num(d2_val)
    }
    st.session_state.lista_jugadas.append(nueva_jugada)
    
    # 6. Modo Drive automático
    if st.session_state.modo_avance == "🏈 Drive":
        if st.session_state.resultado in ["Interception", "Drop", "Incompleto"] or is_td:
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
    
    # 7. REINICIO DE MENÚS AL GUARDAR (Autolavado)
    st.session_state.passer_sel = "N/A"
    st.session_state.receiver_sel = "N/A"
    st.session_state.runner_sel = "N/A"
    st.session_state.d1_sel = "N/A"
    st.session_state.d2_sel = "N/A"
    
    st.rerun() 

st.markdown("---")

# --- DESCARGAS ---
if st.session_state.lista_jugadas:
    with st.expander("📥 Exportar Práctica o Borrar Sesión", expanded=False):
        df_jugadas = pd.DataFrame(st.session_state.lista_jugadas)
        fecha_hoy = datetime.now().strftime("%d-%m-%Y")
        
        str_down = st.session_state.down_drill.replace("D", "down") if st.session_state.down_drill != "N/A" else ""
        nombre_descarga = f"{periodo_actual} {str_down} {fecha_hoy}".strip().replace("  ", " ")
        
        c_csv, c_excel, c_del = st.columns(3)
        with c_csv:
            csv_data = df_jugadas.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar CSV (Hudl)", data=csv_data, file_name=f"{nombre_descarga}.csv", mime='text/csv', use_container_width=True)
        with c_excel:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_jugadas.to_excel(writer, index=False, sheet_name='Practica')
            st.download_button("Descargar Excel", data=excel_buffer.getvalue(), file_name=f"{nombre_descarga}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
        with c_del:
            if st.button("🗑️ Borrar Práctica", use_container_width=True):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()
