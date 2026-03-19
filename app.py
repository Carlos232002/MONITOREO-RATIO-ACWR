import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os

# --- 1. CONFIGURACIÓN VISUAL Y ESTILO (CSS) ---
st.set_page_config(page_title="ACWR Performance Suite", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1E90FF; color: white; border-radius: 8px; border: none; width: 100%; }
    .stDownloadButton>button { background-color: #00CC00; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3 { color: #1E90FF; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SEGURIDAD ---
USER_CREDENTIALS = {"carlos": "cafyd2026", "admin": "pro-trainer"}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Profesional")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        return False
    return True

if check_password():
    FILE_NAME = 'database_pro.csv'
    if not os.path.exists(FILE_NAME):
        cols = ['Fecha', 'Atleta', 'Disciplina', 'Duracion', 'RPE', 'Carga', 'Sueno', 'Estres', 'Fatiga']
        pd.DataFrame(columns=cols).to_csv(FILE_NAME, index=False)

    st.sidebar.title(f"📊 {st.session_state['username'].upper()}")
    menu = st.sidebar.radio("Navegación", ["Registrar Sesión", "Panel de Análisis", "Gestión de Datos"])
    
    # --- 3. LISTA DE DEPORTES AMPLIADA ---
    DEPORTES = sorted([
        "Tenis", "Fútbol", "Baloncesto", "Balonmano", "Piragüismo", "Ping Pong", 
        "Running", "Gimnasio", "Natación", "Ciclismo", "Pádel", "Voleibol", 
        "Rugby", "Crossfit", "Yoga", "Recuperación", "Otro"
    ])

    if menu == "Registrar Sesión":
        st.header("📝 Registro de Actividad")
        with st.form("main_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                atleta = st.text_input("Atleta", value=st.session_state['username'])
                fecha = st.date_input("Fecha", value=date.today())
                disciplina = st.selectbox("Deporte / Disciplina", DEPORTES)
                duracion = st.number_input("Minutos", 0, 480, 60)
                rpe = st.select_slider("Esfuerzo (RPE 1-10)", options=list(range(1,11)), value=5)
            with c2:
                st.markdown("### Wellness")
                sueno = st.slider("Calidad Sueño", 1, 5, 3)
                estres = st.slider("Nivel Estrés", 1, 5, 3)
                fatiga = st.slider("Nivel Fatiga", 1, 5, 3)
            
            if st.form_submit_button("Guardar Sesión ✅"):
                carga = duracion * rpe
                nueva_fila = pd.DataFrame([[fecha, atleta, disciplina, duracion, rpe, carga, sueno, estres, fatiga]], 
                                          columns=['Fecha', 'Atleta', 'Disciplina', 'Duracion', 'RPE', 'Carga', 'Sueno', 'Estres', 'Fatiga'])
                df = pd.read_csv(FILE_NAME)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(FILE_NAME, index=False)
                st.success(f"¡Sesión de {disciplina} guardada!")

    elif menu == "Panel de Análisis":
        df = pd.read_csv(FILE_NAME)
        if not df.empty:
            atleta_sel = st.selectbox("Seleccionar Atleta", df['Atleta'].unique())
            df_atleta = df[df['Atleta'] == atleta_sel].copy()
            df_atleta['Fecha'] = pd.to_datetime(df_atleta['Fecha'])
            
            resumen = df_atleta.groupby('Fecha').agg({'Carga': 'sum', 'Sueno': 'mean', 'Estres': 'mean', 'Fatiga': 'mean'}).sort_index()
            resumen = resumen.reindex(pd.date_range(resumen.index.min(), date.today()), fill_value=0)

            aguda = resumen['Carga'].rolling(window=7, min_periods=1).sum()
            cronica = resumen['Carga'].rolling(window=28, min_periods=1).sum() / 4
            acwr = aguda / cronica
            
            # Monotonía (evitando división por cero)
            std_7 = resumen['Carga'].rolling(window=7).std()
            monotonia = np.where(std_7 > 0, resumen['Carga'].rolling(window=7).mean() / std_7, 0)

            m1, m2, m3 = st.columns(3)
            m1.metric("Ratio ACWR", f"{acwr.iloc[-1]:.2f}")
            m2.metric("Monotonía", f"{monotonia[-1]:.2f}")
            m3.metric("Wellness", f"{(resumen['Sueno'].iloc[-1]+resumen['Estres'].iloc[-1]+resumen['Fatiga'].iloc[-1])/3:.1f}/5")

            st.subheader(f"Gráfica de Rendimiento: {atleta_sel}")
            fig, ax = plt.subplots(figsize=(12, 4), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            ax.axhspan(0.8, 1.3, color='green', alpha=0.15)
            
            puntos_col = ['#1E90FF' if v < 0.8 else '#0
