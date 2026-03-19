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

# URL de tu logo (Asegúrate de que el nombre en GitHub sea logo_app.png)
LOGO_URL = "https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png"

st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: #ffffff; }}
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    h1, h2, h3 {{ color: #1E90FF; }}
    
    /* Logo en el sidebar */
    [data-testid="stSidebarNav"]::before {{
        content: "";
        display: block;
        margin: 20px auto;
        width: 120px;
        height: 120px;
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
        u = st.text_input("Usuario").lower()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos.")
        return False
    return True

# Funciones de imagen
def image_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img.thumbnail((400, 400))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=70)
        return base64.b64encode(buf.getvalue()).decode()
    return ""

if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    
    # Columnas actualizadas
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.title(f"👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Buenos Días (Wellness)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    # --- WELLNESS ---
    if menu == "🌅 Buenos Días (Wellness)":
        st.header("🌅 Estado de Salud Matutino")
        with st.form("w_form", clear_on_submit=True):
            s = st.slider("Sueño", 1, 5, 3)
            e = st.slider("Estrés", 1, 5, 3)
            f = st.slider("Energía", 1, 5, 3)
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                # Creamos fila con ceros en lo que no es wellness
                nueva_fila = pd.DataFrame([[str(date.today()), 'WELLNESS', '-', 0, 0, 0, s, e, f, '', '']], columns=COLUMNAS)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(DB, index=False)
                st.success("Wellness guardado correctamente.")

    # --- SESIÓN ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("s_form", clear_on_submit=True):
            fecha = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            dur = st.number_input("Minutos", 1, 400, 60)
            rpe = st.select_slider("RPE (1-10)", options=list(range(1,11)), value=5)
            notx = st.text_area("Notas")
            foto = st.file_uploader("Foto", type=['jpg', 'png'])
            
            if st.form_submit_button("Guardar Sesión ✅"):
                f_b64 = image_to_base64(foto)
                df = pd.read_csv(DB)
                nueva_fila = pd.DataFrame([[str(fecha), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, notx, f_b64]], columns=COLUMNAS)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(DB, index=False)
                st.success("Sesión guardada.")

    # --- RANKING ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación")
        grupo_sel = st.selectbox("Ver grupo:", GROUPS) if len(GROUPS) > 1 else GROUPS[0]
        
        res_list = []
        hace_7 = pd.Timestamp(date.today() - timedelta(days=7))
        
        for u, info in USERS.items():
            if grupo_sel in info[2]:
                p = f'database_{u}.csv'
                if os.path.exists(p):
                    d = pd.read_csv(p)
                    if not d.empty:
                        d['Fecha'] = pd.to_datetime(d['Fecha'])
                        d7 = d[d['Fecha'] >= hace_7]
                        c = d7['Carga'].sum()
                        w = ((d7['Sueno'] + d7['Estres'] + d7['Fatiga']).replace(0, np.nan)).mean()
                        res_list.append({"Atleta": info[1], "Carga Semanal": int(c), "Wellness": round(w, 1) if not np.isnan(w) else 0})
        
        if res_list:
            st.table(pd.DataFrame(res_list).sort_values("Carga Semanal", ascending=False))

    # --- ANÁLISIS ---
    elif menu == "📊 Mi Análisis Pro":
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            # Agrupar para ver carga total día y wellness medio día
            analisis = df.groupby('Fecha').agg({
                'Carga': 'sum',
                'Sueno': lambda x: x[x>0].mean(),
                'Estres': lambda x: x[x>0].mean(),
                'Fatiga': lambda x: x[x>0].mean()
            }).fillna(0)
            st.line_chart(analisis['Carga'])
