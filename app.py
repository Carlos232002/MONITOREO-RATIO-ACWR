import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN VISUAL (ESTILO MEJORADO PARA LOGO) ---
st.set_page_config(page_title="Rendimiento ACWR", page_icon="📈", layout="wide")

# Intentamos cargar el logo localmente para mayor estabilidad
logo_path = "logo_app.png"
logo_url = "https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png"

st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: #ffffff; }}
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    h1, h2, h3 {{ color: #1E90FF; }}
    
    /* LOGO EN SIDEBAR: Forzamos visualización en móviles */
    [data-testid="stSidebarNav"]::before {{
        content: "";
        display: block;
        margin: 20px auto;
        width: 150px; /* Un poco más grande para que se vea bien */
        height: 150px;
        background-image: url("{logo_url}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    /* Ajuste para que el menú no pise el logo en el móvil */
    [data-testid="stSidebarNav"] {{
        padding-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. USUARIOS ---
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
        # Título neutro para todos los grupos
        st.title("🔐 Acceso Plataforma de Rendimiento")
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos.")
        return False
    return True

# --- REPETIR FUNCIONES DE IMAGEN Y LÓGICA DE NAVEGACIÓN ---
if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    # Mostrar logo también en la parte superior del móvil si no carga el sidebar
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    st.sidebar.markdown(f"## **{NAME}**")
    menu = st.sidebar.radio("Menú Principal", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    # (El resto del código de registro y análisis se mantiene igual que en el paso anterior)
    # ... (Copiar las funciones de Wellness con calendario y Registro de sesión aquí)
