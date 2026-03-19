import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os

# --- 1. CONFIGURACIÓN VISUAL Y LOGO ---
st.set_page_config(page_title="ACWR Performance Suite", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1E90FF; color: white; border-radius: 8px; border: none; width: 100%; }
    .stDownloadButton>button { background-color: #00CC00; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3 { color: #1E90FF; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    [data-testid="stSidebarNav"]::before {
        content: "";
        display: block;
        margin: 20px auto;
        width: 120px;
        height: 120px;
        background-image: url("https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS (TUS CLIENTES) ---
USER_CREDENTIALS = {
    "carlos": "cafyd2026",
    "vanessa": "100618",
    "alejandrop": "Prade2004",
    "manuel": "Camavinga8",
    "alejandror": "Rome3+1",
    "admin": "pro-trainer"
}

# Nombres reales para la interfaz
REAL_NAMES = {
    "carlos": "Carlos",
    "vanessa": "Vanessa Carrascal",
    "alejandrop": "Alejandro de Prádena",
    "manuel": "Manuel Benito",
    "alejandror": "Alejandro Romero",
    "admin": "Administrador"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Profesional Privado")
        st.info("Introduce tus credenciales de atleta para acceder a tu panel.")
        user = st.text_input("Usuario (en minúsculas)").lower()
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user
                st.session_state["full_name"] = REAL_NAMES.get(user, user.capitalize())
                st.session_state["personal_db"] = f'database_{user}.csv'
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Contacta con tu coach.")
        return False
    return True

if check_password():
    MY_FILE = st.session_state["personal_db"]
    USER_NAME = st.session_state["username"]
    FULL_NAME = st.session_state["full_name"]

    if not os.path.exists(MY_FILE):
        cols = ['Fecha', 'Disciplina', 'Duracion', 'RPE', 'Carga', 'Sueno', 'Estres', 'Fatiga']
        pd.DataFrame(columns=cols).to_csv(MY_FILE, index=False)

    # Sidebar personalizada
    st.sidebar.markdown(f"### Atleta:\n## **{FULL_NAME}**")
    st.sidebar.divider()
    menu = st.sidebar.radio("Navegación", ["Mi Diario", "Análisis Pro", "Mis Datos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    DEPORTES = sorted(["Tenis", "Fútbol", "Baloncesto", "Balonmano", "Piragüismo", "Ping Pong", "Running", "Gimnasio", "Natación", "Ciclismo", "Pádel", "Voleibol", "Rugby", "Crossfit", "Yoga", "Recuperación", "Otro"])

    # --- REGISTRO ---
    if menu == "Mi Diario":
        st.header(f"📝 Registro de Sesión")
        st.subheader("🧠 Wellness (1=Mal, 5=Genial)")
        cw1, cw2, cw3 = st.columns(3)
        with cw1: sueno = st.slider("Sueño", 1, 5, 3)
        with cw2: estres = st.slider("Estrés", 1, 5, 3)
        with cw3: fatiga = st.slider("Energía", 1, 5, 3)
        
        with st.form("f1", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                fecha = st.date_input("Fecha", value=date.today())
                disciplina = st.selectbox("Deporte", DEPORTES)
            with c2:
                duracion = st.number_
