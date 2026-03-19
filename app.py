import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os

# 1. Configuración de la App
st.set_page_config(page_title="Monitor ACWR Pro", page_icon="🏃‍♂️", layout="centered")
st.title("📊 Monitor de Carga ACWR")

FILE_NAME = 'registro_cargas.csv'

if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=['Fecha', 'Disciplina', 'Duracion_min', 'RPE', 'Carga_sRPE']).to_csv(FILE_NAME, index=False)

# 2. Formulario de Entrada
with st.expander("📝 Registrar Nueva Sesión", expanded=True):
    with st.form("registro_entreno", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
            disciplina = st.selectbox("Disciplina", ['Tenis', 'Correr', 'Gimnasio', 'Otros'])
        with col2:
            duracion = st.number_input("Minutos", min_value=1, max_value=300, value=60)
            rpe = st.select_slider("Esfuerzo (RPE 1-10)", options=list(range(1, 11)), value=5)
        
        enviar = st.form_submit_button("Guardar Sesión ✅")

if enviar:
    carga = duracion * rpe
    nueva_fila = pd.DataFrame([{'Fecha': fecha, 'Disciplina': disciplina, 'Duracion_min': duracion, 'RPE': rpe, 'Carga_sRPE': carga}])
    df = pd.read_csv(FILE_NAME)
    pd.concat([df, nueva_fila], ignore_index=True).to_csv(FILE_NAME, index=False)
    st.success(f"¡Guardado! Carga de {carga} UA añadida.")
    st.balloons()

# 3. Gestión de Errores (Borrar Último)
st.divider()
col_del, col_empty = st.columns([1, 2])
with col_del:
    if st.button("🗑️ Borrar última sesión", help="Elimina el último registro guardado"):
        df = pd.read_csv(FILE_NAME)
        if not df.empty:
            df = df[:-1]
            df.to_csv(FILE_NAME, index=False)
            st.warning("Último registro eliminado.")
            st.rerun()

# 4. Visualización ACWR
st.subheader("Evolución del Ratio Agudo/Crónico")
df = pd.read_csv(FILE_NAME)
if len(df) < 7:
    st.info("Necesitas 7 días de datos para ver la gráfica.")
else:
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df_diario = df.groupby('Fecha')['Carga_sRPE'].sum().reindex(pd.date_range(df['Fecha'].min(), date.today()), fill_value=0)
    
    aguda = df_diario.rolling(window=7, min_periods=1).sum()
    cronica = df_diario.rolling(window=28, min_periods=1).sum() / 4
    acwr = aguda / cronica

    fig, ax = plt.subplots(figsize=(10, 4))
    colores = ['#1E90FF' if v < 0.8 else '#00CC00' if v <= 1.3 else '#FFA500' if v <= 1.5 else '#FF0000' for v in acwr]
    ax.scatter(acwr.index, acwr, c=colores, s=100, edgecolors='black', zorder=3)
    ax.plot(acwr.index, acwr, color='gray', alpha=0.2)
    ax.axhspan(0.8, 1.3, color='green', alpha=0.1, label="Sweet Spot")
    ax.set_ylim(0, 2.5)
    st.pyplot(fig)

# 5. Descarga
st.download_button("📥 Descargar CSV", pd.read_csv(FILE_NAME).to_csv(index=False), "datos.csv")
