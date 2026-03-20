import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import base64
from datetime import date, timedelta, datetime
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="My Performance Journal", 
    page_icon="logo_app.png", 
    layout="wide"
)

# URL DIRECTA
URL_LOGO = "https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png"

# --- 2. ESTILOS CSS (ACTUALIZADO PARA EL NUEVO STREAMLIT) ---
st.markdown(f"""
    <style>
    /* Fondo y colores generales */
    .main {{ background-color: #0e1117; color: #ffffff; }}
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; }}
    h1, h2, h3 {{ color: #1E90FF; }}

    /* ESTE ES EL SELECTOR NUEVO QUE NECESITAS */
    [data-testid="stSidebarNavContent"]::before {{
        content: "";
        display: block;
        margin: 20px auto;
        width: 120px;
        height: 120px;
        background-image: url("{URL_LOGO}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}

    .medal-box {{ 
        background-color: #1c2128; padding: 15px; border-radius: 12px; border: 2px solid #30363d; text-align: center; margin-bottom: 25px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DICCIONARIO DE USUARIOS ---
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

# --- 4. FUNCIONES DE APOYO ---
def calcular_racha_y_medalla(df):
    if df.empty: return 0, "Estás en racha", "🌱"
    fechas = pd.to_datetime(df['Fecha']).dt.date.unique()
    fechas = sorted(fechas, reverse=True)
    racha = 0
    target = date.today()
    
    if fechas and fechas[0] < target:
        if fechas[0] == target - timedelta(days=1):
            target = target - timedelta(days=1)
        else: return 0, "Estás en racha", "🌱"

    for f in fechas:
        if f == target:
            racha += 1
            target -= timedelta(days=1)
        else: break
        
    if racha >= 180: return racha, "LEYENDA DIAMANTE", "💎"
    if racha >= 90: return racha, "MEDALLA DE ORO", "🥇"
    if racha >= 30: return racha, "MEDALLA DE PLATA", "🥈"
    if racha >= 14: return racha, "MEDALLA DE BRONCE", "🥉"
    if racha >= 7: return racha, "MEDALLA DE CHOCOLATE", "🍫"
    return racha, "Estás en racha", "🌱"

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

# --- 5. LÓGICA PRINCIPAL ---
if check_password():
    USER, NAME, GROUPS, DB = st.session_state.user, st.session_state.name, st.session_state.groups, st.session_state.db
    COLUMNAS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Muscular','Animo','Notas','Foto']
    
    if not os.path.exists(DB):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB, index=False)

    df_actual = pd.read_csv(DB)
    racha_num, medalla_txt, icono = calcular_racha_y_medalla(df_actual)
    
    st.sidebar.markdown(f"### 👤 {NAME}")
    st.sidebar.markdown(f"""
    <div class="medal-box">
        <h1 style='margin:0; font-size: 45px;'>{icono}</h1>
        <p style='color: #1E90FF; font-weight: bold; margin: 5px 0;'>{medalla_txt}</p>
        <span style='font-size: 14px;'>🔥 {racha_num} días seguidos</span>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness (Salud)", "🏃‍♂️ Registrar Sesión", "🏆 Ranking del Grupo", "📊 Mi Análisis Pro", "📥 Gestión de Datos", "📖 Guía de Ayuda"])

    if menu == "🌅 Wellness (Salud)":
        st.header("🌅 Cuestionario Wellness (Hooper)")
        with st.form("w_form"):
            f_w = st.date_input("Fecha", value=date.today())
            s = st.slider("Calidad del Sueño", 1, 5, 3)
            e = st.slider("Nivel de Estrés", 1, 5, 3)
            f = st.slider("Fatiga Percibida", 1, 5, 3)
            m = st.slider("Dolor Muscular", 1, 5, 3)
            a = st.slider("Estado de Ánimo", 1, 5, 3)
            w_notas = st.text_area("🗒️ Anotaciones extra", placeholder="¿Por qué te sientes así hoy?")
            if st.form_submit_button("Guardar Wellness ✅"):
                df = pd.read_csv(DB)
                df = df.drop(df[(df['Fecha'] == str(f_w)) & (df['Tipo'] == 'WELLNESS')].index)
                nueva = pd.DataFrame([[str(f_w), 'WELLNESS', '-', 0, 0, 0, s, e, f, m, a, w_notas, '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("¡Datos guardados!")
                st.rerun()

    elif menu == "🏃‍♂️ Registrar Sesión":
        st.header("🏃‍♂️ Registro de Actividad")
        with st.form("s_form"):
            f_s = st.date_input("Fecha", value=date.today())
            dep = st.selectbox("Deporte/Actividad", ["Fútbol", "Baloncesto", "Tenis", "Pádel", "Balonmano", "Volleyball", "Badminton", "Tenis de Mesa", "Gimnasio", "Running", "Natación", "Ciclismo", "Otro"])
            dur = st.number_input("Duración (minutos)", 1, 400, 60)
            rpe = st.select_slider("RPE (1-10)", options=list(range(1,11)), value=5)
            notas = st.text_area("📓 Diario", placeholder="Sensaciones de la sesión...")
            if st.form_submit_button("Guardar Registro ✅"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f_s), 'ENTRENO', dep, dur, rpe, dur*rpe, 0, 0, 0, 0, 0, notas, '']], columns=COLUMNAS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Actividad registrada.")
                st.rerun()

    elif menu == "🏆 Ranking del Grupo":
        st.header("🏆 Clasificación")
        if GROUPS:
            g_sel = st.selectbox("Seleccionar Grupo para visualizar:", GROUPS)
            
            # --- LÓGICA COACH PREMIUM SOLO PARA GRUPO STAFF ---
            if g_sel == "Staff":
                st.subheader("🕵️ Panel Maestro (Staff Only)")
                res_premium = []
                hoy = date.today()
                for u_id, info in USERS.items():
                    if "Staff" in info[2]: continue 
                    p_db = f'database_{u_id}.csv'
                    if os.path.exists(p_db):
                        d = pd.read_csv(p_db)
                        if not d.empty:
                            d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                            diario = d[d['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
                            aguda = diario.reindex(pd.date_range(hoy-timedelta(days=6), hoy).date, fill_value=0).mean()
                            cronica = diario.reindex(pd.date_range(hoy-timedelta(days=27), hoy).date, fill_value=0).mean()
                            ratio = aguda/cronica if cronica > 0 else 1.0
                            w_h = d[(d['Tipo'] == 'WELLNESS') & (d['Fecha'] == hoy)]
                            well_hoy = w_h[['Sueno','Estres','Fatiga','Muscular','Animo']].mean(axis=1).iloc[0] if not w_h.empty else 0
                            alerta = "🟢 OK"
                            if ratio > 1.5: alerta = "🔴 RIESGO CARGA"
                            elif well_hoy > 0 and well_hoy < 2.5: alerta = "🟡 WELLNESS BAJO"
                            res_premium.append({"Atleta": info[1], "Wellness": round(float(well_hoy),1) if well_hoy > 0 else "Pendiente", "Ratio ACWR": round(ratio,2), "Estado": alerta})
                if res_premium: st.dataframe(pd.DataFrame(res_premium), use_container_width=True)
            
            # --- RANKING NORMAL (JUGADORES VEN NOTAS AHORA) ---
            else:
                res = []
                hoy = date.today()
                hace_7 = hoy - timedelta(days=7)
                for u, info in USERS.items():
                    p_db = f'database_{u}.csv'
                    if g_sel in info[2] and os.path.exists(p_db):
                        try:
                            d = pd.read_csv(p_db)
                            if not d.empty:
                                d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                                c = d[d['Fecha'] >= hace_7]['Carga'].sum()
                                w_hoy = d[(d['Tipo'] == 'WELLNESS') & (d['Fecha'] == hoy)]
                                if not w_hoy.empty:
                                    well_display = round(float(w_hoy[['Sueno','Estres','Fatiga','Muscular','Animo']].mean(axis=1).iloc[0]), 1)
                                else:
                                    well_display = "Pendiente ⏳"
                                res.append({"Atleta": info[1], "Carga (7d)": int(c), "Wellness Hoy": well_display})
                        except: continue
                if res: st.dataframe(pd.DataFrame(res).sort_values("Carga (7d)", ascending=False), use_container_width=True)
        else: st.info("No tienes grupos asignados.")

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
            ax.legend(); st.pyplot(fig)

    elif menu == "📥 Gestión de Datos":
        st.header("📥 Gestión de Datos")
        df = pd.read_csv(DB)
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            tipo_filtro = st.radio("Filtro:", ["Todo", "Esta Semana", "Mes Específico"], horizontal=True)
            df_filtrado = df.copy()
            if tipo_filtro == "Esta Semana": df_filtrado = df[df['Fecha'] >= (date.today() - timedelta(days=date.today().weekday()))]
            elif tipo_filtro == "Mes Específico":
                meses = sorted(list(set(df['Fecha'].apply(lambda x: x.strftime('%Y-%m')))), reverse=True)
                mes_sel = st.selectbox("Mes:", meses)
                df_filtrado = df[df['Fecha'].apply(lambda x: x.strftime('%Y-%m')) == mes_sel]
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Descargar", data=csv, file_name=f'datos_{USER}.csv')
            with st.form("del_f"):
                f_del = st.selectbox("Eliminar fecha:", sorted(df_filtrado['Fecha'].unique(), reverse=True))
                conf = st.checkbox("Confirmar borrado")
                if st.form_submit_button("Borrar Registro"):
                    if conf: df[df['Fecha'] != f_del].to_csv(DB, index=False); st.rerun()
            st.dataframe(df_filtrado.sort_values(by="Fecha", ascending=False))

    elif menu == "📖 Guía de Ayuda":
        st.header("📖 Guía de Interpretación de Datos")
        with st.expander("🏅 Sistema de Medallas (Tu Compromiso)", expanded=True):
            st.write("""
            | Medalla | Racha Requerida | Significado |
            | :--- | :--- | :--- |
            | 🍫 **Chocolate** | **7 Días** | ¡Buen comienzo! Has superado la barrera de la primera semana. |
            | 🥉 **Bronce** | **14 Días** | Hábito creado. Empiezas a demostrar una constancia sólida. |
            | 🥈 **Plata** | **30 Días** | Compromiso de Élite. Un mes entero sin fallar denota mentalidad profesional. |
            | 🥇 **Oro** | **90 Días** | Disciplina de Tigre. Máximo nivel de rigor y seriedad con tu salud. |
            | 💎 **Diamante** | **180 Días** | Leyenda del Club. Referente absoluto de compromiso para todo el grupo. |
            """)
        with st.expander("🌅 Cuestionario Wellness (Método Hooper)"):
            st.write("El **Wellness** indica tu capacidad de recuperación (5 es óptimo, 1 es crítico).")
        with st.expander("📉 Monotonía (Variabilidad de la Carga)"):
            st.write("Mide si tus cargas son muy similares día tras día.")
        with st.expander("⚖️ Ratio ACWR (Aguda vs Crónica)"):
            st.write("Compara tu carga de la última semana contra tu media del mes.")
