import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN VISUAL, ESTILO Y MARCA (CSS) ---
st.set_page_config(page_title="TIGRES Performance Hub", page_icon="📈", layout="wide")

# Fondo de la App, Colores de Botones y Títulos (Inspirado en el logo)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3 { color: #1E90FF; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* Imagen del logo principal en el sidebar (Asegúrate de tener logo_app.png en GitHub) */
    [data-testid="stSidebarNav"]::before {
        content: "";
        display: block;
        margin: 20px auto;
        width: 130px;
        height: 130px;
        background-image: url("https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }
    
    /* Fondo con el logo de Tigres en el ranking (Pro) */
    .tigres-bg {
        background-image: url("https://raw.githubusercontent.com/ai-generated-logos/MONITOREO-RATIO-ACWR/main/tigres_bg.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        opacity: 0.1; /* Sutil como marca de agua */
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
    }
    .ranking-container { position: relative; z-index: 1; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS Y SEGURIDAD TOTAL (Mantenemos tu lista) ---
USERS = {
    "carlos": ["cafyd2026", "Carlos (Coach)", "Staff"],
    "admin": ["pro-trainer", "Admin", "Staff"],
    "vanessa": ["100618", "Vanessa Carrascal", "Familia"],
    "alejandrop": ["Prade2004", "Alejandro de Prádena", "Tigres"],
    "manuel": ["Camavinga8", "Manuel Benito", "Tigres"],
    "alejandror": ["Rome3+1", "Alejandro Romero", "Tigres"],
    "quique": ["Chocotatrejo", "Quique", "Tigres"],
    "fran": ["AtmAlcorcon", "Fran Fernández", "Tigres"]
}

REAL_NAMES = {
    "carlos": "Carlos",
    "vanessa": "Vanessa Carrascal",
    "alejandrop": "Alejandro de Prádena",
    "manuel": "Manuel Benito",
    "alejandror": "Alejandro Romero",
    "quique": "Quique",
    "fran": "Fran Fernández",
    "admin": "Administrador"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Acceso Plataforma ACWR")
        st.info("Introduce tus credenciales de atleta.")
        u = st.text_input("Usuario").lower()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"authenticated": True, "user": u, "name": USERS[u][1], "group": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error de acceso.")
        return False
    return True

# Funciones de imagen (Base64) para guardar en CSV (Mantenemos las mismas)
def image_to_base64(image_file):
    if image_file is not None:
        try:
            img = Image.open(image_file)
            img.thumbnail((400, 400))
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=70)
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            st.error(f"Error procesando la imagen: {e}")
            return None
    return None

def base64_to_image(base64_string):
    if base64_string and pd.notna(base64_string):
        try:
            img_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(img_data))
        except: return None
    return None

# --- 3. LÓGICA PRINCIPAL ---
if check_password():
    USER, NAME, GROUP, DB = st.session_state.user, st.session_state.name, st.session_state.group, st.session_state.db
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=['Fecha','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto']).to_csv(DB, index=False)

    # Sidebar personalizada
    st.sidebar.markdown(f"### Atleta:\n## **{NAME}**")
    st.sidebar.markdown(f"**Grupo:** {GROUP}")
    st.sidebar.divider()
    menu = st.sidebar.radio("Navegación", ["Mi Diario", "Mi Análisis Pro", "Ranking del Grupo", "Mis Datos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state["authenticated"]
        st.rerun()

    DEPORTES = sorted(["Tenis", "Fútbol", "Balonmano", "Piragüismo", "Running", "Gimnasio", "Natación", "Ciclismo", "Pádel", "Voleibol", "Rugby", "Crossfit", "Yoga", "Recuperación", "Otro"])

    # --- REGISTRO ---
    if menu == "Mi Diario":
        st.header(f"📝 Registro de Sesión")
        st.subheader("🧠 Wellness (1=Mal, 5=Genial)")
        cw1, cw2, cw3 = st.columns(3)
        with cw1: sueno = st.slider("Sueño", 1, 5, 3)
        with cw2: estres = st.slider("Estrés", 1, 5, 3)
        with cw3: fatiga = st.slider("Energía", 1, 5, 3)
        
        with st.form("carga_form", clear_on_submit=True):
            st.subheader("🏃‍♂️ Sesión de Entrenamiento")
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", value=date.today())
                disciplina = st.selectbox("Deporte", DEPORTES)
            with col2:
                duracion = st.number_input("Duración (min)", 0, 480, 60)
                rpe = st.select_slider("Esfuerzo Percibido (RPE 1-10)", options=list(range(1,11)), value=5)
            
            c3, c4 = st.columns([2, 1])
            with c3: notas = st.text_area("📓 Notas/Molestias")
            with c4: foto_file = st.file_uploader("📸 Añadir Foto (JPEG/PNG)", type=['jpg','jpeg','png'])
            
            if st.form_submit_button("Guardar Datos del Día ✅"):
                carga = duracion * rpe
                foto_b64 = image_to_base64(foto_file)
                nueva_fila = pd.DataFrame([[fecha, disciplina, duracion, rpe, carga, sueno, estres, fatiga, notas, foto_b64]], columns=['Fecha','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Notas','Foto'])
                pd.concat([pd.read_csv(DB), nueva_fila], ignore_index=True).to_csv(DB, index=False)
                st.success("¡Datos guardados!")

    # --- ANÁLISIS ---
    elif menu == "Mi Análisis Pro":
        st.header(f"📊 Panel de Control")
        df = pd.read_csv(DB)
        if len(df.groupby('Fecha')) < 7: st.info("Necesitas 7 días de datos para generar el Ratio ACWR.")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            resumen = df.groupby('Fecha').agg({'Carga': 'sum', 'Sueno': 'mean', 'Estres': 'mean', 'Fatiga': 'mean'}).sort_index()
            resumen = resumen.reindex(pd.date_range(resumen.index.min(), date.today()), fill_value=0)
            aguda = resumen['Carga'].rolling(7, min_periods=1).sum()
            cronica = resumen['Carga'].rolling(28, min_periods=1).sum() / 4
            acwr = aguda / cronica
            
            # --- MÉTRICAS ---
            m1, m2, m3 = st.columns(3)
            val_acwr = acwr.iloc[-1]
            m1.metric("Tu Ratio ACWR", f"{val_acwr:.2f}", help="Ideal: 0.8 - 1.3")
            wellness_avg = (resumen['Sueno'].iloc[-1] + resumen['Estres'].iloc[-1] + resumen['Fatiga'].iloc[-1]) / 3
            m2.metric("Tu Wellness Medio", f"{wellness_avg:.1f}/5")
            m3.metric("Última Carga", f"{int(resumen['Carga'].iloc[-1])} UA")

            # --- GRÁFICA SEMÁFORO ---
            fig, ax = plt.subplots(figsize=(12, 3.5), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            # Fondos del semáforo
            ax.axhspan(0.8, 1.3, color='green', alpha=0.1) # Sweet spot
            ax.axhspan(1.5, 2.5, color='red', alpha=0.08)   # Riesgo alto
            # Puntos y línea
            puntos_col = ['#1E90FF' if v < 0.8 else '#00CC00' if v <= 1.3 else '#FFA500' if v <= 1.5 else '#FF0000' for v in acwr.fillna(0)]
            ax.scatter(acwr.index, acwr, c=puntos_col, s=110, zorder=3, edgecolors='white', linewidth=1)
            ax.plot(acwr.index, acwr, color='white', alpha=0.2)
            
            # Estilo
            ax.tick_params(colors='white')
            ax.grid(axis='y', color='gray', linestyle='--', alpha=0.1)
            for spine in ax.spines.values(): spine.set_color('white')
            st.pyplot(fig)

    # --- RANKING DE GRUPO DUAL CON MARCA DE AGUA PRO ---
    elif menu == "Ranking del Grupo":
        st.header(f"🏆 Clasificación y Recuperación de {GROUP}")
        
        # Primero el Ranking (Mismo proceso que antes)
        ranking_data = []
        hoy = date.today()
        hace_7_dias = pd.Timestamp(hoy - timedelta(days=7))
        hace_28_dias = pd.Timestamp(hoy - timedelta(days=28))
        acwr_grupo_sum = 0
        atletas_con_acwr = 0
        
        for u, info in USERS.items():
            if info[2] == GROUP: # Solo miembros del grupo
                path = f'database_{u}.csv'
                if os.path.exists(path):
                    temp_df = pd.read_csv(path)
                    if not temp_df.empty:
                        temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha'])
                        # Filtrar datos de la última semana y mes
                        df_7 = temp_df[temp_df['Fecha'] >= hace_7_dias]
                        df_28 = temp_df[temp_df['Fecha'] >= hace_28_dias]
                        
                        if not df_7.empty:
                            # 1. Suma de Carga Semanal
                            carga_7 = df_7['Carga'].sum()
                            
                            # 2. Promedio de Wellness Semanal
                            wellness_7 = ((df_7['Sueno'] + df_7['Estres'] + df_7['Fatiga']) / 3).mean()
                            
                            # 3. Cálculo de ACWR individual (para la media del grupo)
                            if not df_28.empty:
                                # Resumen diario para el rolling
                                res_ind = temp_df.groupby('Fecha').agg({'Carga':'sum'}).reindex(pd.date_range(hace_28_dias, hace_7_dias), fill_value=0)
                                aguda_ind = res_ind['Carga'].sum()
                                cronica_ind = temp_df[temp_df['Fecha'] >= hace_28_dias]['Carga'].sum() / 4
                                if cronica_ind > 0:
                                    acwr_ind = aguda_ind / cronica_ind
                                    acwr_grupo_sum += acwr_ind
                                    atletas_con_acwr += 1
                                    
                            ranking_data.append({
                                "Atleta": info[1], 
                                "Carga Semanal (UA)": int(carga_7),
                                "Wellness Promedio (1-5)": round(wellness_7, 1)
                            })
        
        # Métrica de Grupo arriba
        m1, m2, m3 = st.columns(3)
        if atletas_con_acwr > 0:
            acwr_grupo = acwr_grupo_sum / atletas_con_acwr
            estado_grupo = "Verde ✅" if 0.8 <= acwr_grupo <= 1.3 else "Rojo ⚠️" if acwr_grupo > 1.5 else "Naranja"
            m1.metric("Ratio ACWR Medio del Grupo", f"{acwr_grupo:.2f}", help="Media de los ACWR de todos los atletas de la manada.")
        if ranking_data:
            wellness_grupo = sum([x["Wellness Promedio (1-5)"] for x in ranking_data]) / len(ranking_data)
            m2.metric("Wellness Medio del Grupo", f"{wellness_grupo:.1f}/5", help="Indica la recuperación general de la manada.")
        
        st.divider()

        # Ranking con Marca de Agua Pro
        st.markdown(f'<div class="ranking-container"><div class="tigres-bg"></div>', unsafe_allow_html=True)
        if ranking_data:
            st.subheader("Clasificación General (Últimos 7 días)")
            rank_df = pd.DataFrame(ranking_data).sort_values(by="Carga Semanal (UA)", ascending=False)
            
            # Aplicar estilo de color RdYlGn (Rojo-Amarillo-Verde) a Wellness
            st.dataframe(
                rank_df.style.background_gradient(cmap='RdYlGn', subset=['Wellness Promedio (1-5)'], vmin=1, vmax=5),
                use_container_width=True
            )
            st.info("💡 El ranking se ordena por Carga. Un Wellness alto (verde) indica buena recuperación.")
            
        else: st.info("No hay datos suficientes registrados en este grupo esta semana para generar el ranking.")
        st.markdown('</div>', unsafe_allow_html=True) # Cierra el container

    elif menu == "Mis Datos":
        st.header("⚙️ Historial Completo")
        df = pd.read_csv(DB)
        st.dataframe(df)
        if st.button("🗑️ Borrar MI último registro"):
            df[:-1].to_csv(DB, index=False)
            st.rerun()
