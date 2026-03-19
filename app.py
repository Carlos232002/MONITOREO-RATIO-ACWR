import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="ACWR Visual AMS", page_icon="📸", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3 { color: #1E90FF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. USUARIOS Y GRUPOS (REORGANIZADOS) ---
# Estructura: "usuario": ["contraseña", "Nombre Real", "Grupo"]
USERS = {
    "carlos": ["cafyd2026", "Carlos (Coach)", "Staff"],
    "admin": ["pro-trainer", "Admin", "Staff"],
    "vanessa": ["100618", "Vanessa Carrascal", "Familia"],
    "alejandrop": ["Prade2004", "Alejandro de Prádena", "Tigres"],
    "manuel": ["Camavinga8", "Manuel Benito", "Tigres"],
    "alejandror": ["Rome3+1", "Alejandro Romero", "Tigres"],
    "quique": ["Chocotatrejo", "Quique", "Tigres"]
}

REAL_NAMES = {
    "carlos": "Carlos",
    "vanessa": "Vanessa Carrascal",
    "alejandrop": "Alejandro de Prádena",
    "manuel": "Manuel Benito",
    "alejandror": "Alejandro Romero",
    "quique": "Quique",
    "admin": "Administrador"
}

# --- 3. FUNCIONES AUXILIARES ---
def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Plataforma ACWR")
        u = st.text_input("Usuario").lower()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "group": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error de acceso.")
        return False
    return True

def image_to_base64(image_file):
    if image_file is not None:
        try:
            img = Image.open(image_file)
            img.thumbnail((400, 400))
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=70)
            return base64.b64encode(buffered.getvalue()).decode()
        except: return None
    return None

def base64_to_image(base64_string):
    if base64_string and pd.notna(base64_string):
        try:
            return Image.open(BytesIO(base64.b64decode(base64_string)))
        except: return None
    return None

# --- 4. LÓGICA PRINCIPAL ---
if check_password():
    USER, NAME, GROUP, DB = st.session_state.user, st.session_state.name, st.session_state.group, st.session_state.db
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=['Fecha','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']).to_csv(DB, index=False)

    st.sidebar.title(f"👤 {NAME}")
    st.sidebar.info(f"Grupo: {GROUP}")
    menu = st.sidebar.radio("Navegación", ["Registrar Sesión", "Mi Rendimiento Pro", "Ranking y Fotos", "Descargas"])
    
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    # --- REGISTRO ---
    if menu == "Registrar Sesión":
        st.header("📝 Nueva Entrada")
        with st.form("reg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                fecha = st.date_input("Fecha", value=date.today())
                deporte = st.selectbox("Deporte", ["Tenis", "Fútbol", "Balonmano", "Piragüismo", "Running", "Gimnasio", "Otro"])
                minutos = st.number_input("Minutos", 0, 400, 60)
                rpe = st.select_slider("Esfuerzo (1-10)", options=list(range(1,11)), value=5)
            with c2:
                s, e, f = st.slider("Sueño",1,5,3), st.slider("Estrés",1,5,3), st.slider("Energía",1,5,3)
            
            c3, c4 = st.columns([2, 1])
            with c3: notas = st.text_area("📓 Notas/Molestias")
            with c4: foto_file = st.file_uploader("📸 Añadir Foto", type=['jpg','jpeg','png'])
            
            if st.form_submit_button("Guardar ✅"):
                foto_b64 = image_to_base64(foto_file)
                df_new = pd.DataFrame([[fecha, deporte, minutos, rpe, minutos*rpe, s, e, f, notas, foto_b64]], columns=['Fecha','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto'])
                pd.concat([pd.read_csv(DB), df_new], ignore_index=True).to_csv(DB, index=False)
                st.success("¡Datos guardados!")

    # --- ANÁLISIS ---
    elif menu == "Mi Rendimiento Pro":
        df = pd.read_csv(DB)
        if len(df) < 7: st.info("Faltan datos para el análisis (necesitas 7 días).")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            res = df.groupby('Fecha').agg({'Carga':'sum','Sueno':'mean','Estres':'mean','Fatiga':'mean'}).sort_index()
            res = res.reindex(pd.date_range(res.index.min(), date.today()), fill_value=0)
            aguda = res['Carga'].rolling(7).sum()
            cronica = res['Carga'].rolling(28).sum()/4
            acwr = aguda/cronica
            
            st.subheader("📈 Ratio ACWR")
            fig, ax = plt.subplots(figsize=(12,3.5), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            ax.axhspan(0.8, 1.3, color='green', alpha=0.1)
            ax.plot(acwr.index, acwr, color='white', alpha=0.2)
            ax.scatter(acwr.index, acwr, c=['#1E90FF' if v<0.8 else '#00CC00' if v<=1.3 else '#FFA500' if v<=1.5 else '#FF0000' for v in acwr.fillna(0)], s=100)
            ax.tick_params(colors='white')
            st.pyplot(fig)

    # --- RANKING DE GRUPO ---
    elif menu == "Ranking y Fotos":
        st.header(f"🏆 Panel del Grupo: {GROUP}")
        ranking_data = []
        for u, info in USERS.items():
            if info[2] == GROUP:
                path = f'database_{u}.csv'
                if os.path.exists(path):
                    temp_df = pd.read_csv(path)
                    if not temp_df.empty:
                        temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha'])
                        hace_7 = pd.Timestamp(date.today() - timedelta(days=7))
                        carga_7 = temp_df[temp_df['Fecha'] >= hace_7]['Carga'].sum()
                        ranking_data.append({"Atleta": info[1], "Carga Semanal": int(carga_7)})
        
        if ranking_data:
            st.subheader("Ranking de Esfuerzo (Últimos 7 días)")
            st.table(pd.DataFrame(ranking_data).sort_values(by="Carga Semanal", ascending=False))
        
        st.divider()
        st.subheader("📸 Galería Visual del Grupo")
        # Aquí la app busca fotos de todos los que pertenecen al mismo grupo que tú
