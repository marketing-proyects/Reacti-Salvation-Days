import streamlit as st
import pandas as pd
import base64
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="REACTISALVATION DAYS", layout="wide")

# --- FUNCIONES PARA FUENTES WÜRTH ---
def get_base64_font(font_file):
    with open(font_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- FUENTES ---
font_bold = get_base64_font("WuerthBold.ttf")
font_book = get_base64_font("WuerthBook.ttf")

font_style = f"""
<style>
@font-face {{
    font-family: 'WuerthBold';
    src: url(data:font/ttf;base64,{font_bold}) format('truetype');
}}
@font-face {{
    font-family: 'WuerthBook';
    src: url(data:font/ttf;base64,{font_book}) format('truetype');
}}

html, body, [class*="css"] {{
    font-family: 'WuerthBook', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'WuerthBold', sans-serif !important;
    color: #DA291C; /* Rojo Würth */
}}

.stDataFrame {{
    font-family: 'WuerthBook', sans-serif;
}}
</style>
"""
st.markdown(font_style, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DATA_FILE = "datos_competencia.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Si no existe, usamos el que subiste originalmente (ajusta el nombre si es necesario)
        return pd.read_csv("Libro2.xlsx - Hoja1.csv")

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

# Pestañas para separar el Ranking de la Administración
tab1, tab2 = st.tabs(["🏆 Ranking Mensual", "⚙️ Cargar Datos"])

with tab1:
    df = load_data()
    
    # Lógica de Puntos: 1 reactivado = 1 pto, 1 salvado = 1 pto.
    # Nota: Ajustamos según las columnas detectadas en tu archivo.
    # Asumimos que "PUNTOS ACUMULADOS" es la suma que quieres mostrar.
    
    st.subheader("Clasificación General")
    
    # Limpieza básica para visualización (saltando las filas de encabezado extra si existen)
    display_df = df[df['ID'].notna()].copy()
    
    # Ordenar por Puntos Acumulados (de mayor a menor)
    if 'PUNTOS ACUMULADOS' in display_df.columns:
        display_df['PUNTOS ACUMULADOS'] = pd.to_numeric(display_df['PUNTOS ACUMULADOS'], errors='coerce').fillna(0)
        display_df = display_df.sort_values(by='PUNTOS ACUMULADOS', ascending=False)

    # Mostrar Tabla de Ranking
    st.dataframe(display_df[['Nombre', 'Equipo que integra en la competencia', 'PUNTOS ACUMULADOS']], 
                 use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Acceso Administrativo")
    password = st.text_input("Introduce el password para actualizar los datos:", type="password")
    
    # --- PASSWORD ---
    if password == "Patricia.Faguaga":
        st.success("Acceso concedido")
        uploaded_file = st.file_uploader("Sube el Excel/CSV actualizado con los puntos del mes", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.xlsx'):
                new_df = pd.read_excel(uploaded_file)
            else:
                new_df = pd.read_csv(uploaded_file)
            
            if st.button("Confirmar y Actualizar Ranking"):
                save_data(new_df)
                st.balloons()
                st.success("¡Datos actualizados correctamente!")
    elif password != "":
        st.error("Password incorrecto")
