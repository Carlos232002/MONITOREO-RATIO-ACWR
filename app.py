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

# Inicializar CSV si no existe
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
        'Fecha': pd.to_datetime(fecha), 'Disciplina': disciplina, 
        'Duracion_min': duracion, 'RPE': rpe, 'Carga_sRPE': carga
    }])
    
    df = pd.read_csv(FILE_NAME)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.success(f"¡Entreno guardado! Carga: {carga} UA")

# 4. Gráfica del Semáforo ACWR
st.divider()
st.subheader("Evolución del Ratio Agudo/Crónico (ACWR)")

df = pd.read_csv(FILE_NAME)
if df.empty or len(df.groupby('Fecha')) < 7:
    st.info("⏳ Registra al menos 7 días de entrenamiento para ver la gráfica del ACWR.")
else:
    # Preparar datos
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df_diario = df.groupby('Fecha')['Carga_sRPE'].sum().reset_index()
    df_diario.set_index('Fecha', inplace=True)
    
    # Rellenar huecos
    idx = pd.date_range(df_diario.index.min(), date.today())
    df_diario = df_diario.reindex(idx, fill_value=0)
    
    # Cálculos
    df_diario['Carga_Aguda'] = df_diario['Carga_sRPE'].rolling(window=7, min_periods=1).sum()
    df_diario['Carga_Cronica'] = df_diario['Carga_sRPE'].rolling(window=28, min_periods=1).sum() / 4
    df_diario['ACWR'] = np.where(df_diario['Carga_Cronica'] > 0, df_diario['Carga_Aguda'] / df_diario['Carga_Cronica'], 0)

    # Gráfica
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Colores según tu petición
    puntos_colores = []
    for v in df_diario['ACWR']:
        if v < 0.8: puntos_colores.append('#1E90FF')   # Azul
        elif v <= 1.3: puntos_colores.append('#00CC00') # Verde
        elif v <= 1.5: puntos_colores.append('#FFA500') # Naranja
        else: puntos_colores.append('#FF0000')          # Rojo

    ax.plot(df_diario.index, df_diario['ACWR'], color='gray', alpha=0.3)
    ax.scatter(df_diario.index, df_diario['ACWR'], c=puntos_colores, s=80, zorder=3)
    
    # Fondos de color
    ax.axhspan(0.0, 0.8, color='#1E90FF', alpha=0.05)
    ax.axhspan(0.8, 1.3, color='#00CC00', alpha=0.08)
    ax.axhspan(1.3, 1.5, color='#FFA500', alpha=0.08)
    ax.axhspan(1.5, 2.5, color='#FF0000', alpha=0.05)
    
    ax.set_ylim(0, 2.2)
    st.pyplot(fig)

# 5. Descarga
st.divider()
df_download = pd.read_csv(FILE_NAME)
st.download_button(label="📥 Descargar Excel con mis datos", data=df_download.to_csv(index=False), file_name="mis_cargas.csv", mime="text/csv")
