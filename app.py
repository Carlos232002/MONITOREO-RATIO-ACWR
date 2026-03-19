import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rendimiento ACWR", page_icon="📈", layout="wide")

# URL del logo (Ruta directa de GitHub)
LOGO_URL = "https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png"

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
        width: 100px;
        height: 100px;
        background-image: url("{LOGO_URL}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
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

def image_to_base64(image_file):
    if image_file:
        try:
            img = Image.open(image_file)
            img.thumbnail((400, 400))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=70)
            return base64.b64encode(buf.getvalue()).decode()
        except: return ""
    return ""

# --- 3. LÓGICA PRINCIPAL ---
if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.title(f"👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    # --- WELLNESS ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Registro de Wellness")
        with st.form("w_form", clear_on_submit=True):
            fecha_w = st.date_input("Fecha", value=date.today())
            c1, c2, c3 = st.columns(3)
            with c1: s = st.slider("Sueño", 1, 5, 3)
            with c2: e = st.slider("Estrés", 1, 5, 3)
            with c3: f = st.slider("Energía", 1, 5, 3)
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                fecha_s = str(fecha_w)
                df = df.drop(df[(df['Fecha'] == fecha_s) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[fecha_s, 'WELLNESS', '-', 0, 0, 0, s, e, f, 'Basal', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Wellness actualizado.")

    # --- SESIÓN ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("s_form", clear_on_submit=True):
            fecha_ses = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            dur = st.number_input("Minutos", 1, 400, 60)
            rpe = st.select_slider("RPE", options=list(range(1,11)), value=5)
            foto = st.file_uploader("Foto", type=['jpg', 'png'])
            if st.form_submit_button("Guardar Sesión ✅"):
                f_b64 = image_to_base64(foto)
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(fecha_ses), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, '', f_b64]], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Sesión guardada.")

    # --- RANKING ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación")
        g_sel = st.selectbox("Grupo:", GROUPS) if len(GROUPS) > 1 else GROUPS[0]
        res = []
        hace_7 = date.today() - timedelta(days=7)
        for u, info in USERS.items():
            if g_sel in info[2]:
                path = f'database_{u}.csv'
                if os.path.exists(path):
                    d = pd.read_csv(path)
                    if not d.empty:
                        d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                        d7 = d[d['Fecha'] >= hace_7]
                        c = d7['Carga'].sum()
                        w_df = d7[d7['Tipo'] == 'WELLNESS']
                        w = ((w_df['Sueno'] + w_df['Estres'] + w_df['Fatiga']) / 3).mean() if not w_df.empty else 0
                        res.append({"Atleta": info[1], "Carga": int(c), "Wellness": round(w, 1)})
        if res: st.table(pd.DataFrame(res).sort_values("Carga", ascending=False))

    # --- ANÁLISIS ---
    elif menu == "📊 Mi Análisis Pro":
        st.header("📊 Evolución")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            ana = df.groupby('Fecha').agg({'Carga': 'sum', 'Sueno': lambda x: x[x>0].mean()}).fillna(0)
            st.line_chart(ana['Carga'])
