import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import date, timedelta

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="My Performance Journal", 
    page_icon="https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png", 
    layout="wide"
)

URL_LOGO = "https://raw.githubusercontent.com/Carlos232002/MONITOREO-RATIO-ACWR/main/logo_app.png"

# --- 2. ESTILOS ---
st.markdown(f"""
    <style>
    .stMetric {{ background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    [data-testid="stSidebarNavContent"]::before {{
        content: ""; display: block; margin: 20px auto; width: 100px; height: 100px;
        background-image: url("{URL_LOGO}"); background-size: contain; background-repeat: no-repeat;
    }}
    .medal-box {{ background-color: #1c2128; padding: 10px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. USUARIOS ---
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

# --- 4. FUNCIONES ---
def calcular_racha(df):
    if df.empty: return 0, "🌱", "Estás en racha"
    fechas = pd.to_datetime(df['Fecha']).dt.date.unique()
    fechas = sorted(fechas, reverse=True)
    racha = 0
    t = date.today()
    if fechas and fechas[0] < t:
        if fechas[0] == t - timedelta(days=1): t -= timedelta(days=1)
        else: return 0, "🌱", "Estás en racha"
    for f in fechas:
        if f == t: racha += 1; t -= timedelta(days=1)
        else: break
    if racha >= 30: return racha, "🥈", "PLATA"
    if racha >= 7: return racha, "🍫", "CHOCOLATE"
    return racha, "🌱", "Racha actual"

def check_password():
    if "auth" not in st.session_state:
        st.title("🔐 Acceso")
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u in USERS and USERS[u][0] == p:
                st.session_state.update({"auth": True, "u": u, "n": USERS[u][1], "g": USERS[u][2], "db": f'database_{u}.csv'})
                st.rerun()
            else: st.error("Error.")
        return False
    return True

# --- 5. APP ---
if check_password():
    U, NAME, G, DB = st.session_state.u, st.session_state.n, st.session_state.g, st.session_state.db
    COLS = ['Fecha','Tipo','Disciplina','Duracion','RPE','Carga','Sueno','Estres','Fatiga','Muscular','Animo','Notas','Foto']
    if not os.path.exists(DB): pd.DataFrame(columns=COLS).to_csv(DB, index=False)
    
    df_act = pd.read_csv(DB)
    rn, ico, txt = calcular_racha(df_act)
    st.sidebar.markdown(f"### 👤 {NAME}")
    st.sidebar.markdown(f'<div class="medal-box"><h1>{ico}</h1><p>{txt}</p><span>🔥 {rn} días</span></div>', unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navegación", ["🌅 Wellness", "🏃‍♂️ Sesión", "🏆 Ranking", "📊 Análisis", "📥 Datos"])

    if menu == "🌅 Wellness":
        st.header("🌅 Wellness")
        with st.form("w"):
            f = st.date_input("Fecha", value=date.today())
            s = st.slider("Sueño", 1, 5, 3)
            e = st.slider("Estrés", 1, 5, 3)
            fa = st.slider("Fatiga", 1, 5, 3)
            if st.form_submit_button("Guardar"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f),'WELLNESS','-',0,0,0,s,e,fa,3,3,'','']], columns=COLS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Hecho."); st.rerun()

    elif menu == "🏃‍♂️ Sesión":
        st.header("🏃‍♂️ Sesión")
        with st.form("s"):
            f = st.date_input("Fecha", value=date.today())
            dur = st.number_input("Minutos", 1, 300, 60)
            rpe = st.slider("RPE", 1, 10, 5)
            if st.form_submit_button("Guardar"):
                df = pd.read_csv(DB)
                nueva = pd.DataFrame([[str(f),'ENTRENO','Fútbol',dur,rpe,dur*rpe,0,0,0,0,0,'','']], columns=COLS)
                pd.concat([df, nueva], ignore_index=True).to_csv(DB, index=False)
                st.success("Registrado."); st.rerun()

    elif menu == "🏆 Ranking":
        if "Staff" in G:
            st.header("🕵️ Panel Maestro (Coach)")
            g_sel = st.selectbox("Grupo:", [x for x in G if x != "Staff"])
            res = []
            hoy = date.today()
            for u_id, info in USERS.items():
                p_db = f'database_{u_id}.csv'
                if g_sel in info[2] and os.path.exists(p_db) and "Staff" not in info[2]:
                    d = pd.read_csv(p_db)
                    if not d.empty:
                        d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                        diario = d[d['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
                        aguda = diario.reindex(pd.date_range(hoy-timedelta(days=6), hoy).date, fill_value=0).mean()
                        cronica = diario.reindex(pd.date_range(hoy-timedelta(days=27), hoy).date, fill_value=0).mean()
                        ratio = aguda/cronica if cronica > 0 else 1.0
                        w = d[(d['Tipo']=='WELLNESS') & (d['Fecha']==hoy)]
                        well = w[['Sueno','Estres','Fatiga']].mean(axis=1).values[0] if not w.empty else 0.0
                        alerta = "🔴 RIESGO" if ratio > 1.5 or (0 < well < 2.5) else "🟢 OK"
                        res.append({"Atleta": info[1], "Wellness": well, "ACWR": round(ratio,2), "Estado": alerta})
            if res:
                st.dataframe(pd.DataFrame(res).style.applymap(lambda x: 'background-color: #721c24' if x == "🔴 RIESGO" else '', subset=['Estado']))
        else:
            st.info("Solo disponible para Coach.")

    elif menu == "📊 Análisis":
        st.header("Análisis Individual")
        # Aquí iría tu código de gráficas simplificado

    elif menu == "📥 Datos":
        st.dataframe(pd.read_csv(DB))
