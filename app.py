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
    
    /* Logo en el sidebar (ASEGÚRATE DE HABER SUBIDO logo_app.png A GITHUB) */
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

# --- 2. GESTIÓN DE USUARIOS Y SEGURIDAD TOTAL ---
# Aquí defines quién puede entrar. ¡Copia esta estructura para añadir más atletas!
USER_CREDENTIALS = {
    "carlos": "cafyd2026",   # Tu usuario
    "atleta1": "pala2024",   # Un piragüista
    "atleta2": "gol2024",    # Un futbolista
    "admin": "pro-trainer"   # Tu acceso de superusuario
}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Profesional Privado")
        st.markdown("Por favor, introduce tus credenciales para acceder a tu panel personal.")
        user = st.text_input("Usuario (tu nombre en minúsculas)")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user
                # Definimos el nombre de archivo ÚNICO para este usuario
                st.session_state["personal_db"] = f'database_{user}.csv'
                st.success(f"¡Bienvenido, {user.capitalize()}!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario no autorizado.")
        return False
    return True

if check_password():
    # --- 3. INICIALIZACIÓN DE LA BASE DE DATOS PERSONAL ---
    # Usamos el nombre de archivo específico del usuario autenticado
    MY_FILE = st.session_state["personal_db"]
    USER_NAME = st.session_state["username"]

    if not os.path.exists(MY_FILE):
        cols = ['Fecha', 'Disciplina', 'Duracion', 'RPE', 'Carga', 'Sueno', 'Estres', 'Fatiga']
        pd.DataFrame(columns=cols).to_csv(MY_FILE, index=False)

    # Sidebar con info del usuario
    st.sidebar.markdown(f"## Atleta: **{USER_NAME.upper()}**")
    menu = st.sidebar.radio("Navegación", ["Mi Diario de Entrenamiento", "Análisis de Mi Rendimiento", "Descargar Mis Datos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    # Lista de deportes Omnisport
    DEPORTES = sorted([
        "Tenis", "Fútbol", "Baloncesto", "Balonmano", "Piragüismo", "Ping Pong", 
        "Running", "Gimnasio", "Natación", "Ciclismo", "Pádel", "Voleibol", 
        "Rugby", "Crossfit", "Yoga", "Recuperación", "Otro"
    ])

    # --- 4. DIARIO DE ENTRENAMIENTO (REGISTRO) ---
    if menu == "Mi Diario de Entrenamiento":
        st.header(f"📝 Registrar Nueva Sesión - {USER_NAME.capitalize()}")
        
        # Wellness obligatorio por la mañana (o antes de registrar la carga)
        st.subheader("🧠 Wellness Diario (1=Mal, 5=Genial)")
        c_w1, c_w2, c_w3 = st.columns(3)
        with c_w1: sueno = st.slider("Calidad Sueño", 1, 5, 3, key="s")
        with c_w2: estres = st.slider("Nivel Estrés (5 relax)", 1, 5, 3, key="e")
        with c_w3: fatiga = st.slider("Sensación Energía", 1, 5, 3, key="f")
        st.divider()

        with st.form("carga_form", clear_on_submit=True):
            st.subheader("🏃‍♂️ Sesión de Entrenamiento")
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", value=date.today())
                disciplina = st.selectbox("Deporte / Disciplina", DEPORTES)
            with col2:
                duracion = st.number_input("Duración (minutos)", 0, 480, 60)
                rpe = st.select_slider("Esfuerzo Percibido (RPE 1-10)", options=list(range(1,11)), value=5)
            
            if st.form_submit_button("Guardar Datos del Día ✅"):
                carga = duracion * rpe
                nueva_fila = pd.DataFrame([[fecha, disciplina, duracion, rpe, carga, sueno, estres, fatiga]], 
                                          columns=['Fecha', 'Disciplina', 'Duracion', 'RPE', 'Carga', 'Sueno', 'Estres', 'Fatiga'])
                
                # Leemos SOLO su archivo personal
                df = pd.read_csv(MY_FILE)
                pd.concat([df, nueva_fila], ignore_index=True).to_csv(MY_FILE, index=False)
                st.success(f"¡Datos del {fecha} guardados en tu panel personal!")
                st.balloons()

    # --- 5. PANEL DE ANÁLISIS PERSONAL ---
    elif menu == "Análisis de Mi Rendimiento":
        st.header(f"📊 Panel de Control de {USER_NAME.capitalize()}")
        df = pd.read_csv(MY_FILE)
        
        if df.empty or len(df.groupby('Fecha')) < 7:
            st.info("💡 Necesitas registrar al menos 7 días diferentes de datos para ver tu análisis ACWR.")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            
            # Resumen diario (sumamos carga de todas las disciplinas del día)
            resumen = df.groupby('Fecha').agg({'Carga': 'sum', 'Sueno': 'mean', 'Estres': 'mean', 'Fatiga': 'mean'}).sort_index()
            
            # Rellenamos huecos para que el rolling funcione
            idx = pd.date_range(resumen.index.min(), date.today())
            resumen = resumen.reindex(idx, fill_value=0)

            # Cálculos ACWR y Monotonía
            aguda = resumen['Carga'].rolling(window=7, min_periods=1).sum()
            cronica = resumen['Carga'].rolling(window=28, min_periods=1).sum() / 4
            acwr = aguda / cronica
            
            # Monotonía
            std_7 = resumen['Carga'].rolling(window=7).std()
            monotonia = np.where(std_7 > 0, resumen['Carga'].rolling(window=7).mean() / std_7, 0)

            # --- MÉTRICAS CLAVE ---
            m1, m2, m3 = st.columns(3)
            val_acwr = acwr.iloc[-1]
            m1.metric("Tu Ratio ACWR", f"{val_acwr:.2f}", help="Ideal: 0.8 - 1.3")
            
            val_mono = monotonia[-1]
            m2.metric("Monotonía Semanal", f"{val_mono:.2f}", help="Riesgo si > 2.0")
            
            bienestar_avg = (resumen['Sueno'].iloc[-1] + resumen['Estres'].iloc[-1] + resumen['Fatiga'].iloc[-1]) / 3
            m3.metric("Tu Wellness", f"{bienestar_avg:.1f}/5")

            # --- GRÁFICA ACWR SEMÁFORO ---
            st.subheader("Evolución de Tu Carga (ACWR)")
            fig, ax = plt.subplots(figsize=(12, 4.5), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            
            # Fondos del semáforo
            ax.axhspan(0.8, 1.3, color='green', alpha=0.15) # Sweet spot
            ax.axhspan(1.5, 2.5, color='red', alpha=0.08)   # Riesgo alto
            
            # Puntos y línea
            puntos_col = ['#1E90FF' if v < 0.8 else '#00CC00' if v <= 1.3 else '#FFA500' if v <= 1.5 else '#FF0000' for v in acwr]
            ax.scatter(acwr.index, acwr, c=puntos_col, s=130, zorder=3, edgecolors='white', linewidth=1.5)
            ax.plot(acwr.index, acwr, color='white', linestyle='-', alpha=0.2, linewidth=2)
            
            # Estilo de la gráfica
            ax.set_ylim(0, 2.5)
            ax.set_ylabel("Ratio ACWR", color='white')
            ax.tick_params(colors='white', labelsize=10)
            for spine in ax.spines.values(): spine.set_color('white')
            ax.grid(axis='y', color='gray', linestyle='--', alpha=0.1)
            
            st.pyplot(fig)

    # --- 6. GESTIÓN Y DESCARGA (SUYO) ---
    elif menu == "Descargar Mis Datos":
        st.header("📥 Tus Datos Personales")
        df = pd.read_csv(MY_FILE)
        st.dataframe(df.sort_values(by='Fecha', ascending=False))
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Borrar MI última sesión", help="Solo elimina tu último registro guardado"):
                if not df.empty:
                    df[:-1].to_csv(MY_FILE, index=False)
                    st.warning("Última sesión eliminada de tu panel.")
                    st.rerun()
        with c2:
            st.download_button("📥 Descargar Mi Excel (CSV)", df.to_csv(index=False), f"datos_{USER_NAME}.csv")
