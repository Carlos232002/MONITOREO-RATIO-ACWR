import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN Y LOGO (MÉTODO BASE64 LOCAL) ---
st.set_page_config(page_title="Rendimiento ACWR", page_icon="📈", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("logo_app.png")
logo_style = ""
if logo_b64:
    logo_style = f'url("data:image/png;base64,{logo_b64}")'
else:
    # URL de respaldo si el archivo local no carga
    logo_style = 'url("https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png")'

st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: #ffffff; }}
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    h1, h2, h3 {{ color: #1E90FF; }}
    
    [data-testid="stSidebarNav"]::before {{
        content: "";
        display: block;
        margin: 20px auto;
        width: 120px;
        height: 120px;
        background-image: {logo_style};
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. USUARIOS (SISTEMA MULTIGRUPO) ---
USERS = {
    "carlos": ["cafyd2026", "Carlos (Coach)", ["Staff", "Tigres"]],
    "admin": ["pro-trainer", "Admin", ["Staff"]],
    "vanessa": ["100618", "Vanessa Carrascal", ["Familia"]],
    "alejandrop": ["Prade2004", "Alejandro de Prádena", ["Tigres"]],
    "manuel": ["Camavinga8", "Manuel Benito", ["Tigres"]],
    "alejandror": ["Rome3+1", "Alejandro Romero", ["Tigres"]],
    "quique": ["Chocotatrejo", "Quique", ["Tigres"]],
    "fran": ["AtmAlcorcon", "Fran Fernández", ["Tigres"]]
}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Plataforma de Rendimiento")
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({
                    "authenticated": True, 
                    "user": u, 
                    "name": USERS[u][1], 
                    "groups": USERS[u][2], 
                    "db": f'database_{u}.csv'
                })
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos.")
        return False
    return True

# --- 3. LÓGICA DE APLICACIÓN ---
if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    # Sidebar con Info Multigrupo
    st.sidebar.markdown(f"### 👤 {NAME}")
    st.sidebar.info(f"**Tus Grupos:** {', '.join(GROUPS)}")
    
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    # --- WELLNESS ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Estado Matutino")
        with st.form("w_form", clear_on_submit=True):
            fecha_w = st.date_input("Selecciona Fecha", value=date.today())
            c1, c2, c3 = st.columns(3)
            with c1: s = st.slider("Sueño", 1, 5, 3)
            with c2: e = st.slider("Estrés", 1, 5, 3)
            with c3: f = st.slider("Energía", 1, 5, 3)
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                df = df.drop(df[(df['Fecha'] == str(fecha_w)) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[str(fecha_w), 'WELLNESS', '-', 0, 0, 0, s, e, f, 'Basal', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success(f"Wellness del {fecha_w} guardado.")

    # --- REGISTRO SESIÓN ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Nueva Sesión de Entrenamiento")
        with st.form("s_form", clear_on_submit=True):
            f_s = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            dur = st.number_input("Duración (min)", 1, 480, 60)
            rpe = st.select_slider("Esfuerzo (RPE 1-10)", options=list(range(1,11)), value=5)
            if st.form_submit_button("Guardar Sesión ✅"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, '', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Entrenamiento registrado.")

    # --- ANÁLISIS PRO + ALERTA MONOTONÍA ---
    elif menu == "📊 Mi Análisis Pro":
        st.header(f"📊 Análisis de Rendimiento: {NAME}")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            hoy = date.today()
            hace_7 = hoy - timedelta(days=6)
