import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN Y LOGO ---
st.set_page_config(page_title="Rendimiento ACWR", page_icon="📈", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("logo_app.png")
logo_style = f'url("data:image/png;base64,{logo_b64}")' if logo_b64 else 'url("https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png")'

st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: #ffffff; }}
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    h1, h2, h3 {{ color: #1E90FF; }}
    [data-testid="stSidebarNav"]::before {{
        content: ""; display: block; margin: 20px auto; width: 120px; height: 120px;
        background-image: {logo_style}; background-size: contain; background-repeat: no-repeat; background-position: center;
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
        st.title("🔐 Acceso Plataforma")
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error de acceso.")
        return False
    return True

if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.markdown(f"### 👤 {NAME}")
    st.sidebar.info(f"Grupos: {', '.join(GROUPS)}")
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    # --- WELLNESS & SESIÓN (Igual que antes, funcionando ok) ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Wellness")
        with st.form("w"):
            f_w = st.date_input("Fecha", value=date.today())
            s, e, f = st.slider("Sueño",1,5,3), st.slider("Estrés",1,5,3), st.slider("Energía",1,5,3)
            if st.form_submit_button("Guardar"):
                df = pd.read_csv(DB)
                df = df.drop(df[(df['Fecha'] == str(f_w)) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[str(f_w), 'WELLNESS', '-', 0, 0, 0, s, e, f, '', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Guardado.")

    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Sesión")
        with st.form("s"):
            f_s = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            dur = st.number_input("Minutos", 1, 400, 60)
            rpe = st.select_slider("RPE", options=list(range(1,11)), value=5)
            if st.form_submit_button("Guardar"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, '', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Registrado.")

    # --- RANKING CORREGIDO (Sin errores de carga) ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación")
        g_sel = st.selectbox("Selecciona Grupo", GROUPS)
        
        ranking_list = []
        hoy = date.today()
        hace_7 = hoy - timedelta(days=7)
        
        for u, info in USERS.items():
            if g_sel in info[2]:
                p = f'database_{u}.csv'
                if os.path.exists(p):
                    try:
                        d = pd.read_csv(p)
                        if not d.empty:
                            d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                            # Filtrar solo última semana y tipo ENTRENO
                            mask = (d['Fecha'] >= hace_7) & (d['Tipo'] == 'ENTRENO')
                            carga_total = d.loc[mask, 'Carga'].sum()
                            ranking_list.append({"Atleta": info[1], "Carga Semanal": int(carga_total)})
                    except:
                        continue # Si el archivo de un usuario está corrupto, saltar al siguiente
        
        if ranking_list:
            df_r = pd.DataFrame(ranking_list).sort_values("Carga Semanal", ascending=False)
            st.table(df_r)
        else:
            st.info("Aún no hay datos de entrenamiento esta semana.")

    # --- ANÁLISIS PRO (Con Aviso de Monotonía) ---
    elif menu == "📊 Mi Análisis Pro":
        st.header(f"📊 Análisis de {NAME}")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            # Monotonía de los últimos 7 días
            diario = df[df['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
            serie_7 = diario.reindex(pd.date_range(date.today()-timedelta(days=6), date.today()).date, fill_value=0)
            
            std = serie_7.std()
            mono = serie_7.mean() / std if std > 0 else 0
            
            if mono > 2.0:
                st.error(f"🚨 ¡Cuidado **{NAME.split(' ')[0]}**! Te pasas de monótono.")
            
            st.metric("Monotonía", f"{mono:.2f}")
            st.bar_chart(serie_7)
