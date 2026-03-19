import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import base64
from datetime import date, timedelta, datetime
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN Y LOGO ---
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

# --- 2. DICCIONARIO DE USUARIOS (ACTUALIZADO CON YOEL Y DANIEL) ---
USERS = {
    "carlos": ["cafyd2026", "Carlos (Coach)", ["Staff", "Tigres", "Familia"]],
    "admin": ["pro-trainer", "Admin", ["Staff"]],
    "vanessa": ["100618", "Vanessa Carrascal", ["Familia"]],
    "alejandrop": ["Prade2004", "Alejandro de Prádena", ["Tigres"]],
    "manuel": ["Camavinga8", "Manuel Benito", ["Tigres"]],
    "alejandror": ["Rome3+1", "Alejandro Romero", ["Tigres"]],
    "quique": ["Chocotatrejo", "Quique", ["Tigres"]],
    "fran": ["AtmAlcorcon", "Fran Fernández", ["Tigres"]],
    "marcoscalzado": ["Madridcfusera", "Marcos Calzado", ["Tigres"]],
    "alexrdrgz": ["AvilaAnse", "Alex Rodríguez", ["Tigres"]],
    "jorgerdrgz": ["Alcorconedp", "Jorge Rodríguez", ["Tigres"]],
    "jaime": ["Chapigri", "Jaime Rodríguez", []],
    "diego": ["Titos148", "Diego Fernández", ["Familia"]],
    "yoel": ["Sierogenuine", "Yoel Moro", ["Tigres"]],
    "daniel": ["Julianpinilla", "Daniel Martínez", ["Tigres"]]
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
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Muscular','Animo','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    st.sidebar.markdown(f"### 👤 {NAME}")
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro", "📥 Exportar mis Datos", "📖 Guía de Ayuda"])

    # --- 🌅 WELLNESS ---
    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Cuestionario Wellness (Hooper)")
        with st.form("w_form"):
            f_w = st.date_input("Fecha", value=date.today())
            s = st.slider("Calidad del Sueño", 1, 5, 3)
            e = st.slider("Nivel de Estrés", 1, 5, 3)
            f = st.slider("Fatiga Percibida", 1, 5, 3)
            m = st.slider("Dolor Muscular", 1, 5, 3)
            a = st.slider("Estado de Ánimo", 1, 5, 3)
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                df = df.drop(df[(df['Fecha'] == str(f_w)) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[str(f_w), 'WELLNESS', '-', 0, 0, 0, s, e, f, m, a, 'Basal', '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Wellness guardado.")

    # --- 🏃‍♂️ REGISTRAR SESIÓN ---
    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Entrenamiento")
        with st.form("s_form"):
            f_s = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte", ["Fútbol", "Baloncesto", "Tenis", "Pádel", "Balonmano", "Volleyball", "Badminton", "Tenis de Mesa", "Gimnasio", "Running", "Natación", "Ciclismo", "Otro"])
            dur = st.number_input("Duración (minutos)", 1, 400, 60)
            rpe = st.select_slider("RPE (1-10)", options=list(range(1,11)), value=5)
            notas = st.text_area("📓 Diario", placeholder="Sensaciones...")
            if st.form_submit_button("Guardar Sesión ✅"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, 0, 0, notas, '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Sesión guardada.")

    # --- 🏆 RANKING ---
    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación")
        if GROUPS:
            g_sel = st.selectbox("Ver Grupo:", GROUPS)
            res = []
            hace_7 = date.today() - timedelta(days=7)
            for u, info in USERS.items():
                p_db = f'database_{u}.csv'
                if g_sel in info[2] and os.path.exists(p_db):
                    try:
                        d = pd.read_csv(p_db)
                        if not d.empty:
                            d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                            d7 = d[d['Fecha'] >= hace_7]
                            c = d7['Carga'].sum()
                            w_df = d7[d7['Tipo'] == 'WELLNESS']
                            well = w_df[['Sueno','Estres','Fatiga','Muscular','Animo']].mean(axis=1).mean() if not w_df.empty else 0
                            diario = d7[d7['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
                            serie_7 = diario.reindex(pd.date_range(hace_7, date.today()).date, fill_value=0)
                            mono = serie_7.mean() / serie_7.std() if serie_7.std() > 0 else 0
                            res.append({"Atleta": info[1], "Carga": int(c), "Wellness": round(well,1), "Monotonía": round(mono,2)})
                    except: continue
            if res:
                df_rank = pd.DataFrame(res).sort_values("Carga", ascending=False)
                st.dataframe(df_rank.style.background_gradient(cmap='RdYlGn', subset=['Wellness'], vmin=1, vmax=5), use_container_width=True)
            else:
                st.info("No hay registros en los últimos 7 días.")
        else:
            st.info("No perteneces a ningún grupo de clasificación.")

    # --- 📊 ANÁLISIS PRO ---
    elif menu == "📊 Mi Análisis Pro":
        st.header(f"📊 Panel Pro: {NAME}")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            hoy = date.today()
            diario = df[df['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
            aguda_serie = diario.reindex(pd.date_range(hoy-timedelta(days=6), hoy).date, fill_value=0)
            cronica_serie = diario.reindex(pd.date_range(hoy-timedelta(days=27), hoy).date, fill_value=0)
            aguda, cronica = aguda_serie.mean(), cronica_serie.mean()
            acwr = aguda / cronica if cronica > 0 else 1.0
            mono = aguda_serie.mean() / aguda_serie.std() if aguda_serie.std() > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Monotonía", f"{mono:.2f}")
            c2.metric("Ratio ACWR", f"{acwr:.2f}")
            c3.metric("Carga Semanal", f"{int(aguda_serie.sum())}")
            
            st.subheader("Gráfico Aguda vs Crónica")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(aguda_serie.index, [aguda]*len(aguda_serie), color='red', linestyle='--', label="Aguda")
            ax.plot(cronica_serie.index, cronica_serie.values, color='cyan', alpha=0.5, label="Crónica")
            ax.fill_between(aguda_serie.index, aguda_serie.values, color='red', alpha=0.2)
            ax.legend()
            st.pyplot(fig)

    # --- 📥 GESTIÓN DE DATOS ---
    elif menu == "📥 Exportar mis Datos":
        st.header("📥 Gestión de Datos")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            tipo_filtro = st.radio("Filtro:", ["Todo", "Esta Semana", "Mes Específico"], horizontal=True)
            df_filtrado = df.copy()
            if tipo_filtro == "Esta Semana":
                df_filtrado = df[df['Fecha'] >= (date.today() - timedelta(days=date.today().weekday()))]
            elif tipo_filtro == "Mes Específico":
                meses = sorted(list(set(df['Fecha'].apply(lambda x: x.strftime('%Y-%m')))), reverse=True)
                mes_sel = st.selectbox("Mes:", meses)
                df_filtrado = df[df['Fecha'].apply(lambda x: x.strftime('%Y-%m')) == mes_sel]
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Descargar Selección", data=csv, file_name=f'datos_{USER}.csv')
            
            with st.form("del_f"):
                f_del = st.selectbox("Borrar fecha:", sorted(df_filtrado['Fecha'].unique(), reverse=True))
                conf = st.checkbox("Confirmar borrado")
                if st.form_submit_button("Eliminar"):
                    if conf:
                        df[df['Fecha'] != f_del].to_csv(DB, index=False)
                        st.rerun()

            st.dataframe(df_filtrado.sort_values(by="Fecha", ascending=False))

    # --- 📖 GUÍA DE AYUDA ---
    elif menu == "📖 Guía de Ayuda":
        st.header("📖 Guía de Interpretación de Datos")
        st.info("Usa esta guía para entender tus métricas y optimizar tu rendimiento con el Coach.")
        
        with st.expander("🌅 1. Wellness (Cuestionario Hooper)", expanded=True):
            st.write("""
            El Wellness mide cómo te sientes cada mañana antes de entrenar. Puntúa de 1 a 5 (**5 es lo mejor**).
            * **Calidad de Sueño:** ¿Has descansado?
            * **Fatiga:** ¿Te sientes fresco o agotado?
            * **Estrés:** ¿Estás relajado o con mucha tensión mental?
            * **Dolor Muscular:** ¿Tienes muchas agujetas o molestias?
            * **Ánimo:** ¿Tienes energía y ganas de entrenar?
            """)

        with st.expander("📉 2. Monotonía (Variabilidad)", expanded=True):
            st.write("""
            Mide si tus entrenamientos son siempre iguales o si varías la intensidad.
            * **Baja (< 1.5):** **Óptimo.** Estás variando cargas, lo que permite adaptarte y mejorar.
            * **Alta (> 2.0):** **Peligro.** Refleja estancamiento o riesgo de sobreentrenamiento.
            """)

        with st.expander("⚖️ 3. Ratio ACWR (Carga Aguda vs Crónica)", expanded=True):
            st.write("""
            Es el equilibrio entre lo que has hecho esta semana y lo que estás acostumbrado a hacer (últimos 28 días).
            * **Zona Óptima (0.8 - 1.3):** El "punto dulce". Estás progresando de forma segura.
            * **Zona de Alerta (1.3 - 1.5):** Estás subiendo la carga rápido.
            * **Zona de Peligro (> 1.5):** Riesgo crítico de lesión.
            """)
