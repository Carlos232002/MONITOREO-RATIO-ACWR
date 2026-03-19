import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os

# 1. Configuración visual de la App
st.set_page_config(page_title="Monitor ACWR CAFYD", page_icon="🏃‍♂️", layout="centered")
st.title("📊 Monitor de Carga Concurrente")
st.markdown("*(Tenis, Running y Fuerza)*")

FILE_NAME = 'registro_cargas.csv'

# Inicializar CSV
if not os.path.exists(FILE_NAME):
    df_init = pd.DataFrame(columns=['Fecha', 'Disciplina', 'Duracion_min', 'RPE', 'Carga_sRPE'])
    df_init.to_csv(FILE_NAME, index=False)

# 2. Interfaz de usuario (Formulario)
with st.form("registro_entreno"):
    st.subheader("Registrar nueva sesión")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", value=date.today())
        disciplina = st.selectbox("Disciplina", ['Tenis', 'Correr', 'Gimnasio', 'Otros'])
    with col2:
        duracion = st.number_input("Duración (min)", min_value=1, max_value=300, value=60, step=1)
        rpe = st.slider("RPE (1-10)", min_value=1, max_value=10, value=5, step=1)
        
    submit_button = st.form_submit_button(label="Guardar Sesión ✅")

# 3. Lógica al guardar
if submit_button:
    carga = duracion * rpe
    nueva_fila = pd.DataFrame([{
        'Fecha': fecha, 'Disciplina': disciplina, 
        'Duracion_min': duracion, 'RPE': rpe, 'Carga_sRPE': carga
    }])
    
    df = pd.read_csv(FILE_NAME)
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.success(f"¡Entreno guardado! Disciplina: {disciplina} | Carga: {carga} UA")

# 4. Gráfica del Semáforo ACWR
st.divider()
st.subheader("Evolución del Ratio Agudo/Crónico")

df = pd.read_csv(FILE_NAME)
if df.empty or len(df.groupby('Fecha')) < 7:
    st.info("⏳ Faltan datos (mínimo 7 días registrados) para generar la gráfica del ACWR.")
else:
    # Preparar datos
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df_diario = df.groupby('Fecha')['Carga_sRPE'].sum().reset_index()
    df_diario.set_index('Fecha', inplace=True)
    
    idx = pd.date_range(df_diario.index.min(), date.today())
    df_diario = df_diario.reindex(idx, fill_value=0)
    
    df_diario['Carga_Aguda'] = df_diario['Carga_sRPE'].rolling(window=7, min_periods=1).sum()
    df_diario['Carga_Cronica'] = df_diario['Carga_sRPE'].rolling(window=28, min_periods=1).sum() / 4
    df_diario['ACWR'] = np.where(df_diario['Carga_Cronica'] > 0, df_diario['Carga_Aguda'] / df_diario['Carga_Cronica'], 0)

    # Colores CAFYD
    puntos_colores = ['#1E90FF' if v < 0.8 else '#00CC00' if v <= 1.3 else '#FFA500' if v <= 1.5 else '#FF0000' for v in df_diario['ACWR']]

    # Dibujar Gráfica
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_diario.index, df_diario['ACWR'], color='gray', linestyle='-', alpha=0.3)
    ax.scatter(df_diario.index, df_diario['ACWR'], c=puntos_colores, s=80, zorder=3)
    
    ax.axhspan(0.0, 0.8, color='#1E90FF', alpha=0.05)  
    ax.axhspan(0.8, 1.3, color='#00CC00', alpha=0.08)  
    ax.axhspan(1.3, 1.5, color='#FFA500', alpha=0.08)  
    ax.axhspan(1.5, 2.5, color='#FF0000', alpha=0.05)  
    
    ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylim(0, 2.2)
    ax.grid(True, linestyle=':', alpha=0.4)
    st.pyplot(fig)

# 5. Botón de descarga de Excel
st.divider()
with open(FILE_NAME, "rb") as file:
    st.download_button(label="📥 Descargar todos mis datos (Excel)", data=file, file_name="registro_cargas.csv", mime="text/csv")
