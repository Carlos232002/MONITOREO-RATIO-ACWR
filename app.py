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

# URL del logo (Asegúrate de que el nombre coincida en tu GitHub)
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
        u = st.text_input("Usuario").lower()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Credenciales incorrectas.")
        return False
    return True

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
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.title(f"👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    # --- 🌅 WELLNESS (CON CALENDARIO Y MODIFICACIÓN) ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Registro de Wellness")
        st.write("Selecciona el día y registra tu estado basal.")
        
        with st.form("wellness_form", clear_on_submit=True):
            fecha_w = st.date_input("Fecha del registro", value=date.today())
            c1, c2, c3 = st.columns(3)
            with c1: s = st.slider("Sueño (1-5)", 1, 5, 3)
            with c2: e = st.slider("Estrés (1-5)", 1, 5, 3)
            with c3: f = st.slider("Energía (1-5)", 1, 5, 3)
            
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                fecha_str = str(fecha_w)
                
                # Lógica para evitar duplicados: si existe WELLNESS en esa fecha, lo borramos antes de añadir el nuevo
                df = df.drop(df[(df['Fecha'] == fecha_str) & (df['Tipo'] == 'WELLNESS')].index)
                
                nueva_fila = pd.DataFrame([[fecha_str, 'WELLNESS', '-', 0, 0, 0, s, e, f, 'Registro diario', '']], columns=COLUMNAS)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(DB, index=False)
                st.success(f"Wellness del día {fecha_w} guardado/actualizado correctamente.")

    # --- 🏃‍♂️ SESIÓN ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("session_form", clear_on_submit=True):
            fecha_s = st.date_input("Fecha del entrenamiento", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            c1, c2 = st.columns(2)
            with c1: dur = st.number_input("Minutos", 1, 400, 60)
            with c2: rpe = st.select_slider("RPE (1-10)", options=list(range(1,11)), value=5)
            notx = st.text_area("Notas")
            foto = st.file_uploader("Foto de la sesión", type=['jpg', 'png'])
            
            if st.form_submit_button("Guardar Entrenamiento ✅"):
                f_b64 = image_to_base64(foto)
                df = pd.read_csv(DB)
                nueva_fila = pd.DataFrame([[str(fecha_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, notx, f_b64]], columns=COLUMNAS)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(DB, index=False)
                st.success("Sesión guardada exitosamente.")

    # --- 🏆 RANKING ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación Semanal")
        grupo_sel = st.selectbox("Selecciona grupo:", GROUPS) if len(GROUPS) > 1 else GROUPS[0]
        
        res_list = []
        hoy = date.today()
        hace_7 = pd.Timestamp(hoy - timedelta(days=7))
        
        for u, info in USERS.items():
            if grupo_sel in info[2]:
                p = f'database_{u}.csv'
                if os.path.exists(p):
                    d = pd.read_csv(p)
                    if not d.empty:
                        d['Fecha'] = pd.to_datetime(d['Fecha'])
                        # Solo datos de los últimos 7 días
                        d7 = d[d['Fecha'].dt.date >= (hoy - timedelta(days=7))]
                        c_sum = d7['Carga'].sum()
                        # Calcular wellness solo de las filas que tengan datos (>0)
                        w_df = d7[d7['Tipo'] == 'WELLNESS']
                        w_avg = ((w_df['Sueno'] + w_df['Estres'] + w_df['Fatiga']) / 3).mean() if not w_df.empty else 0
                        
                        res_list.append({
                            "Atleta": info[1], 
                            "Carga Semanal (UA)": int(c_sum), 
                            "Wellness Medio": round(w_avg, 1)
                        })
        
        if res_list:
            df_r = pd.DataFrame(res_list).sort_values("Carga Semanal (UA)", ascending=False)
            st.table(df_r)
        else:
            st.info("No hay registros en este grupo para los últimos 7 días.")

    # --- 📊 ANÁLISIS ---
    elif menu == "📊 Mi Análisis Pro":
        st.header("📊 Análisis de Carga y Fatiga")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            analisis = df.groupby('Fecha').agg({
                'Carga': 'sum',
                'Sueno': lambda x: x[x>0].mean(),
                'Estres': lambda x: x[x>0].mean(),
                'Fatiga': lambda x: x[x>0].mean()
            }).fillna(0)
            
            st.subheader("Carga diaria (UA)")
            st.bar_chart(analisis['Carga'])
            
            st.subheader("Evolución de Wellness")
            st.line_chart(analisis[['Sueno', 'Estres', 'Fatiga']])
