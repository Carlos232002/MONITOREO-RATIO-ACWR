import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="TIGRES Hub", page_icon="🐯", layout="wide")

# (Mantengo tu CSS y Diccionario de USERS igual que antes)
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
        st.title("🔐 Acceso TIGRES Hub")
        u = st.text_input("Usuario").lower()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error de acceso.")
        return False
    return True

if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    
    # Aseguramos que el CSV tenga todas las columnas necesarias (incluyendo Wellness y Carga por separado)
    if not os.path.exists(DB):
        pd.DataFrame(columns=['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']).to_csv(DB, index=False)

    st.sidebar.title(f"👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Buenos Días (Wellness)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro"])

    # --- 2. PESTAÑA WELLNESS (Solo una vez al día recomendado) ---
    if menu == "🌅 Buenos Días (Wellness)":
        st.header("🌅 Estado de Salud Matutino")
        st.write("Registra cómo te sientes hoy antes de empezar a entrenar.")
        
        with st.form("wellness_form"):
            col1, col2, col3 = st.columns(3)
            with col1: s = st.slider("Calidad del Sueño", 1, 5, 3)
            with col2: e = st.slider("Nivel de Estrés", 1, 5, 3)
            with col3: f = st.slider("Nivel de Energía", 1, 5, 3)
            
            if st.form_submit_button("Guardar Wellness Diario ✅"):
                df_new = pd.DataFrame([[date.today(), 'WELLNESS', '-', 0, 0, s, e, f, 'Registro matutino', '']], 
                                      columns=['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto'])
                pd.concat([pd.read_csv(DB), df_new], ignore_index=True).to_csv(DB, index=False)
                st.success("¡Wellness registrado! A por el día, Tigre. 🐯")

    # --- 3. PESTAÑA SESIÓN (Se puede usar varias veces al día) ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("session_form"):
            c1, c2 = st.columns(2)
            with c1:
                fecha = st.date_input("Fecha", value=date.today())
                deporte = st.selectbox("Disciplina", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            with c2:
                mins = st.number_input("Duración (min)", 0, 500, 60)
                rpe = st.select_slider("Esfuerzo (RPE 1-10)", options=list(range(1,11)), value=5)
            
            notas = st.text_area("Notas / Molestias / Sensaciones")
            foto = st.file_uploader("Foto de la sesión", type=['jpg', 'png'])
            
            if st.form_submit_button("Guardar Sesión ✅"):
                # (Aquí iría tu función de image_to_base64 que ya tenemos)
                df_new = pd.DataFrame([[fecha, 'ENTRENO', deporte, mins, rpe, mins*rpe, 0, 0, 0, notas, '']], 
                                      columns=['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto'])
                pd.concat([pd.read_csv(DB), df_new], ignore_index=True).to_csv(DB, index=False)
                st.success(f"Sesión de {deporte} añadida correctamente.")

    # --- 4. ANÁLISIS (Cruza ambos datos) ---
    elif menu == "📊 Mi Análisis Pro":
        st.header("📊 Tu Rendimiento Integrado")
        df = pd.read_csv(DB)
        if len(df) > 0:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            # Agrupamos por fecha: Sumamos Carga y hacemos media del Wellness
            diario = df.groupby('Fecha').agg({
                'Carga': 'sum',
                'Sueno': lambda x: x[x > 0].mean(),
                'Estres': lambda x: x[x > 0].mean(),
                'Fatiga': lambda x: x[x > 0].mean()
            }).fillna(0)
            
            st.subheader("Tu evolución")
            st.line_chart(diario['Carga'])
            st.write("Aquí el sistema ya sabe diferenciar qué fue Wellness y qué fue Entreno.")
