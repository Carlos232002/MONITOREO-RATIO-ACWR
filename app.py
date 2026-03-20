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

# --- 2. DICCIONARIO DE USUARIOS ---
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

# --- 3. FUNCIONES DE APOYO ---
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

# --- 4. LÓGICA PRINCIPAL ---
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
        st.header("🏆 Panel de Gestión de Rendimiento")
        
        # --- LÓGICA ESPECIAL PARA EL COACH (STAFF) ---
        if "Staff" in GROUPS:
            st.subheader("🕵️‍♂️ Vista de Supervisor (Modo Coach Premium)")
            
            if GROUPS:
                g_sel = st.selectbox("Seleccionar Grupo para Analizar:", GROUPS)
                res_maestro = []
                hoy = date.today()
                hace_7 = hoy - timedelta(days=7)
                hace_28 = hoy - timedelta(days=28)

                # Escaneo de toda la base de datos de usuarios
                for u, info in USERS.items():
                    p_db = f'database_{u}.csv'
                    # Solo analizamos si el usuario pertenece al grupo seleccionado y no es el propio coach
                    if g_sel in info[2] and os.path.exists(p_db) and "Staff" not in info[2]:
                        try:
                            d = pd.read_csv(p_db)
                            if not d.empty:
                                d['Fecha'] = pd.to_datetime(d['Fecha']).dt.date
                                
                                # 1. Cálculo ACWR (Científico)
                                diario = d[d['Tipo'] == 'ENTRENO'].groupby('Fecha')['Carga'].sum()
                                aguda = diario.reindex(pd.date_range(hoy-timedelta(days=6), hoy).date, fill_value=0).mean()
                                cronica = diario.reindex(pd.date_range(hoy-timedelta(days=27), hoy).date, fill_value=0).mean()
                                ratio = aguda / cronica if cronica > 0 else 1.0
                                
                                # 2. Wellness de Hoy
                                w_hoy = d[(d['Tipo'] == 'WELLNESS') & (d['Fecha'] == hoy)]
                                if not w_hoy.empty:
                                    well_score = w_hoy[['Sueno','Estres','Fatiga','Muscular','Animo']].mean(axis=1).values[0]
                                    estado_w = "Registrado ✅"
                                else:
                                    well_score = 0
                                    estado_w = "PENDIENTE ⏳"
                                
                                # 3. Determinar Estado de Alerta
                                if ratio > 1.5 or (well_score < 2.5 and well_score > 0):
                                    alerta = "🔴 RIESGO ALTO"
                                elif ratio > 1.3 or ratio < 0.8:
                                    alerta = "🟡 PRECAUCIÓN"
                                else:
                                    alerta = "🟢 ÓPTIMO"

                                res_maestro.append({
                                    "Jugador": info[1],
                                    "Wellness Hoy": well_score if well_score > 0 else "---",
                                    "Registro": estado_w,
                                    "Ratio ACWR": round(ratio, 2),
                                    "Estado": alerta,
                                    "Carga Semanal": int(diario.reindex(pd.date_range(hace_7, hoy).date, fill_value=0).sum())
                                })
                        except: continue

                if res_maestro:
                    df_maestro = pd.DataFrame(res_maestro)

                    # --- TARJETAS DE ACCIÓN RÁPIDA ---
                    c1, c2, c3 = st.columns(3)
                    en_riesgo = df_maestro[df_maestro['Estado'] == "🔴 RIESGO ALTO"].shape[0]
                    pendientes = df_maestro[df_maestro['Registro'] == "PENDIENTE ⏳"].shape[0]
                    
                    c1.metric("Jugadores en Riesgo", en_riesgo, delta_color="inverse")
                    c2.metric("Pendientes Wellness", pendientes)
                    c3.metric("Media Carga Grupo", int(df_maestro['Carga Semanal'].mean()))

                    st.markdown("---")
                    
                    # --- TABLA INTERACTIVA CON COLORES ---
                    def color_estado(val):
                        if val == "🔴 RIESGO ALTO": color = '#721c24'
                        elif val == "🟡 PRECAUCIÓN": color = '#856404'
                        elif val == "🟢 ÓPTIMO": color = '#155724'
                        else: color = 'transparent'
                        return f'background-color: {color}'

                    st.write("### 📋 Listado de Control Diario")
                    st.dataframe(
                        df_maestro.style.applymap(color_estado, subset=['Estado'])
                        .background_gradient(cmap='RdYlGn', subset=['Wellness Hoy'], vmin=1, vmax=5),
                        use_container_width=True
                    )
                    
                    # --- BOTÓN PREMIUM: EXPORTAR A COACH ---
                    csv_maestro = df_maestro.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar Reporte Diario (Excel/CSV)", csv_maestro, f"reporte_coach_{hoy}.csv", "text/csv")
                else:
                    st.warning("Aún no hay datos de jugadores para este grupo.")
        
        # --- VISTA PARA EL JUGADOR (RANKING NORMAL) ---
        else:
            st.subheader("📊 Ranking del Grupo")
            # (Aquí va el código del ranking normal que ya tenías o uno simplificado)
            st.info("¡Sigue registrando para subir en el ranking de carga semanal!")
            # [Aquí puedes re-insertar tu lógica de ranking anterior si quieres que los jugadores se vean entre ellos]
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

    elif menu == "📥 Gestión de Datos":
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
            st.download_button(label="📥 Descargar", data=csv, file_name=f'datos_{USER}.csv')
            
            with st.form("del_f"):
                f_del = st.selectbox("Eliminar fecha:", sorted(df_filtrado['Fecha'].unique(), reverse=True))
                conf = st.checkbox("Confirmar borrado")
                if st.form_submit_button("Borrar Registro"):
                    if conf:
                        df[df['Fecha'] != f_del].to_csv(DB, index=False)
                        st.rerun()
            st.dataframe(df_filtrado.sort_values(by="Fecha", ascending=False))

    elif menu == "📖 Guía de Ayuda":
        st.header("📖 Guía de Interpretación de Datos")
        
        with st.expander("🏅 Sistema de Medallas (Tu Compromiso)", expanded=True):
            st.write("""
            **La disciplina y el compromiso diario son los pilares que sustentan tu rendimiento a largo plazo.** Este sistema premia tu rigor al registrar tus datos:
            
            | Medalla | Racha Requerida | Significado |
            | :--- | :--- | :--- |
            | 🍫 **Chocolate** | **7 Días** | ¡Buen comienzo! Has superado la barrera de la primera semana. |
            | 🥉 **Bronce** | **14 Días** | Hábito creado. Empiezas a demostrar una constancia sólida. |
            | 🥈 **Plata** | **30 Días** | Compromiso de Élite. Un mes entero sin fallar denota mentalidad profesional. |
            | 🥇 **Oro** | **90 Días** | Disciplina de Tigre. Máximo nivel de rigor y seriedad con tu salud. |
            | 💎 **Diamante** | **180 Días** | Leyenda del Club. Referente absoluto de compromiso para todo el grupo. |
            
            *⚠️ **Importante:** La racha se mantiene simplemente registrando el Wellness. Si olvidas registrar tus datos un día entero, el contador volverá a cero.*
            """)

        with st.expander("🌅 Cuestionario Wellness (Método Hooper)"):
            st.write("""
            El **Wellness** indica tu capacidad de recuperación. Evaluamos 5 ítems de 1 a 5 (**5 es óptimo**, 1 es crítico):
            
            * **Calidad del Sueño:** Evalúa si el descanso ha sido reparador y profundo.
            * **Nivel de Estrés:** Refleja la carga mental o tensiones externas al entrenamiento.
            * **Fatiga Percibida:** Sensación general de cansancio o falta de energía.
            * **Dolor Muscular (DOMS):** Presencia de agujetas o molestias musculares específicas.
            * **Estado de Ánimo:** Tu predisposición psicológica y motivación para afrontar el día.
            
            *Mantener una media alta en estos valores asegura que estás asimilando bien el trabajo.*
            """)
            
        with st.expander("📉 Monotonía (Variabilidad de la Carga)"):
            st.write("""
            Mide si tus cargas son muy similares día tras día. La variabilidad es necesaria para que el cuerpo progrese.
            
            * **Valores Óptimos (< 1.5):** Indica que hay buena alternancia entre días intensos y de recuperación.
            * **Zona de Riesgo (1.5 - 2.0):** Empiezas a perder variabilidad; presta atención a tu descanso.
            * **Alerta (> 2.0):** Monotonía alta. Esto puede generar sobreentrenamiento (por falta de descanso) o estancamiento (porque el cuerpo se acostumbra y deja de mejorar).
            """)

        with st.expander("⚖️ Ratio ACWR (Aguda vs Crónica)"):
            st.write("""
            Compara tu carga de la última semana contra tu media del mes para asegurar una progresión segura.
            
            * **Zona de Desentrenamiento (< 0.8):** Estás entrenando considerablemente menos de lo habitual. Puede haber riesgo de pérdida de forma o lesiones al reincorporar carga bruscamente.
            * **Punto Dulce (0.8 - 1.3):** Carga de entrenamiento óptima. Progresión segura y mejora del rendimiento.
            * **Zona de Peligro (> 1.5):** Riesgo crítico de lesión por exceso de carga.
            
            **Sistema de Semáforos:**
            * 🟢 **Verde (0.8 - 1.3):** Todo en orden. ¡Sigue así!
            * 🟡 **Amarillo (1.3 - 1.5 o 0.5 - 0.8):** Precaución. Estamos en el límite del desentrenamiento o de la fatiga excesiva.
            * 🔴 **Rojo (< 0.5 o > 1.5):** Alerta máxima. Riesgo muy elevado de lesión o desajuste total.
            """)
