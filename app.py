import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import base64
from datetime import date, timedelta
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN Y LOGO (MÉTODO BLINDADO) ---
st.set_page_config(page_title="Rendimiento ACWR", page_icon="🐯", layout="wide")

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
        content: ""; display: block; margin: 20px auto; width: 100px; height: 100px;
        background-image: {logo_style}; background-size: contain; background-repeat: no-repeat; background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DICCIONARIO DE USUARIOS (TODOS INCLUIDOS) ---
USERS = {
    "carlos": ["cafyd2026", "Carlos (Coach)", ["Staff", "Tigres"]],
    "admin": ["pro-trainer", "Admin", ["Staff"]],
    "vanessa": ["100618", "Vanessa Carrascal", ["Familia"]],
    "alejandrop": ["Prade2004", "Alejandro de Prádena", ["Tigres"]],
    "manuel": ["Camavinga8", "Manuel Benito", ["Tigres"]],
    "alejandror": ["Rome3+1", "Alejandro Romero", ["Tigres"]],
    "quique": ["Chocotatrejo", "Quique", ["Tigres"]],
    "fran": ["AtmAlcorcon", "Fran Fernández", ["Tigres"]],
    "marcoscalzado": ["Madridcfusera", "Marcos Calzado", ["Tigres"]],
    "alexrdrgz": ["AvilaAnse", "Alex Rodríguez", ["Tigres"]],
    "jorgerdrgz": ["Alcorconedp", "Jorge Rodríguez", ["Tigres"]]
}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Plataforma de Rendimiento")
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "groups": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error de acceso.")
        return False
    return True

# --- 3. LÓGICA PRINCIPAL ---
if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    # Columnas extendidas para incluir todos los items de Hooper
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Muscular','Animo','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.markdown(f"### 👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro", "📥 Exportar mis Datos"])

    # --- 🌅 WELLNESS PRO (5 ÍTEMS HOOPER) ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Cuestionario Wellness (Hooper)")
        with st.form("w_form"):
            f_w = st.date_input("Fecha", value=date.today())
            st.info("Puntúa de 1 (Fatal) a 5 (Excelente)")
            s = st.slider("Calidad del Sueño", 1, 5, 3)
            e = st.slider("Nivel de Estrés (Relajación)", 1, 5, 3)
            f = st.slider("Fatiga Percibida (Frescura)", 1, 5, 3)
            m = st.slider("Dolor Muscular (DOMS)", 1, 5, 3, help="5 es sin dolores")
            a = st.slider("Estado de Ánimo (Energía)", 1, 5, 3)
            
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                df = df.drop(df[(df['Fecha'] == str(f_w)) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[str(f_w), 'WELLNESS', '-', 0, 0, 0, s, e, f, m, a, 'Basal', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Wellness guardado correctamente.")

    # --- 🏃‍♂️ REGISTRAR SESIÓN (CON DIARIO/NOTAS) ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("s_form"):
            f_s = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Tenis", "Fútbol", "Gimnasio", "Running", "Pádel", "Otro"])
            dur = st.number_input("Duración (minutos)", 1, 400, 60)
            rpe = st.select_slider("Esfuerzo Percibido (RPE 1-10)", options=list(range(1,11)), value=5)
            notas = st.text_area("📓 Diario de entrenamiento (sensaciones, molestias...)", placeholder="Hoy me he sentido...")
            
            if st.form_submit_button("Guardar Sesión ✅"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, 0, 0, notas, '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Sesión guardada en tu diario.")

    # --- 🏆 RANKING MULTIMÉTRICA ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación de la Manada")
        g_sel = st.selectbox("Ver Grupo:", GROUPS)
        res = []
        hace_7 = date.today() - timedelta(days=7)
        for u, info in USERS.items():
            if g_sel in info[2] and os.path.exists(f'database_{u}.csv'):
                try:
                    d = pd.read_csv(f'database_{u}.csv')
                    if not d.empty:
                        d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                        d7 = d[d['Fecha'] >= hace_7]
                        c = d7['Carga'].sum()
                        w_df = d7[d7['Tipo'] == 'WELLNESS']
                        # Media de los 5 items de Wellness
                        well = w_df[['Sueno','Estres','Fatiga','Muscular','Animo']].mean(axis=1).mean() if not w_df.empty else 0
                        diario = d7[d7['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
                        serie_7 = diario.reindex(pd.date_range(hace_7, date.today()).date, fill_value=0)
                        mono = serie_7.mean() / serie_7.std() if serie_7.std() > 0 else 0
                        res.append({"Atleta": info[1], "Carga": int(c), "Wellness": round(well,1), "Monotonía": round(mono,2)})
                except: continue
        if res:
            df_rank = pd.DataFrame(res).sort_values("Carga", ascending=False)
            st.dataframe(df_rank.style.background_gradient(cmap='RdYlGn', subset=['Wellness'], vmin=1, vmax=5), use_container_width=True)

    # --- 📊 ANÁLISIS PRO (ACWR SEMÁFORO + GRÁFICO AGUDA/CRÓNICA) ---
    elif menu == "📊 Mi Análisis Pro":
        st.header(f"📊 Panel de Rendimiento: {NAME}")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            hoy = date.today()
            
            # Carga Aguda (7d) y Crónica (28d)
            diario = df[df['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
            aguda_serie = diario.reindex(pd.date_range(hoy-timedelta(days=6), hoy).date, fill_value=0)
            cronica_serie = diario.reindex(pd.date_range(hoy-timedelta(days=27), hoy).date, fill_value=0)
            
            aguda = aguda_serie.mean()
            cronica = cronica_serie.mean()
            acwr = aguda / cronica if cronica > 0 else 1.0
            
            # Monotonía
            mono = aguda_serie.mean() / aguda_serie.std() if aguda_serie.std() > 0 else 0
            
            # Semáforo ACWR
            if acwr > 1.5: color_acwr = "inverse" # Rojo
            elif acwr > 1.3: color_acwr = "normal" # Amarillo/Naranja
            else: color_acwr = "off" # Verde/Neutro

            c1, c2, c3 = st.columns(3)
            c1.metric("Monotonía", f"{mono:.2f}", delta="ALTA" if mono > 2.0 else "OK", delta_color="inverse" if mono > 2.0 else "normal")
            c2.metric("Ratio ACWR", f"{acwr:.2f}", help="0.8-1.3: Óptimo | >1.5: Riesgo", delta_color=color_acwr)
            c3.metric("Carga Semanal", f"{int(aguda_serie.sum())} UA")
            
            if mono > 2.0: st.error(f"🚨 ¡Cuidado **{NAME.split(' ')[0]}**! Te pasas de monótono.")

            # Gráfico Aguda vs Crónica
            st.subheader("Gráfico Aguda vs Crónica (Control de Fatiga)")
            fig_acwr, ax_acwr = plt.subplots(figsize=(10, 4))
            ax_acwr.plot(aguda_serie.index, [aguda]*len(aguda_serie), label="Carga Aguda (Hoy)", color='red', linestyle='--')
            ax_acwr.plot(cronica_serie.index, cronica_serie.values, label="Carga Crónica (Histórica)", color='cyan', alpha=0.5)
            ax_acwr.fill_between(aguda_serie.index, aguda_serie.values, color='red', alpha=0.2)
            ax_acwr.legend()
            st.pyplot(fig_acwr)

    # --- 📥 EXPORTAR DATOS ---
    elif menu == "📥 Exportar mis Datos":
        st.header("📥 Descargar Historial de Entrenamiento")
        df = pd.read_csv(DB)
        if not df.empty:
            st.write("Aquí puedes descargar todos tus registros para usarlos en Excel o enviárselos al Coach.")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Descargar CSV para Excel", data=csv, file_name=f'datos_{USER}.csv', mime='text/csv')
            st.dataframe(df)
        else:
            st.info("No hay datos para exportar todavía.")
