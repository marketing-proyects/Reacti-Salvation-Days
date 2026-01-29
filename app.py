import streamlit as st
import pandas as pd
import base64
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="REACTISALVATION DAYS", layout="wide")

# --- FUNCIONES PARA FUENTES WÜRTH ---
def get_base64_font(font_file):
    try:
        if os.path.exists(font_file):
            with open(font_file, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except Exception:
        return None
    return None

# --- APLICAR ESTILOS ---
font_bold = get_base64_font("WuerthBold.ttf")
font_book = get_base64_font("WuerthBook.ttf")

if font_bold and font_book:
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
    html, body, [class*="css"], .stMarkdown {{
        font-family: 'WuerthBook', sans-serif !important;
    }}
    h1, h2, h3, b, strong {{
        font-family: 'WuerthBold', sans-serif !important;
        color: #DA291C; /* Rojo Würth */
    }}
    </style>
    """
    st.markdown(font_style, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DATA_FILE = "datos_competencia.csv"
INITIAL_FILE = "Libro2.xlsx - Hoja1.csv"

def load_data():
    # 1. Intentar cargar datos guardados (CSV interno)
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    
    # 2. Intentar cargar el archivo inicial (CSV del repo)
    if os.path.exists(INITIAL_FILE):
        try:
            return pd.read_csv(INITIAL_FILE)
        except Exception:
            pass
            
    # 3. Si nada existe, devolver estructura base
    return pd.DataFrame(columns=['ID', 'Nombre', 'Equipo que integra en la competencia', 'PUNTOS ACUMULADOS'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

tab1, tab2 = st.tabs(["🏆 Ranking Mensual", "⚙️ Cargar Datos"])

with tab1:
    df_raw = load_data()
    
    if not df_raw.empty:
        # Limpiar nombres de columnas para evitar errores de espacios
        df_raw.columns = df_raw.columns.str.strip()
        
        # Filtrar filas válidas (que tengan ID numérico)
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        
        if 'PUNTOS ACUMULADOS' in df.columns:
            df['PUNTOS ACUMULADOS'] = pd.to_numeric(df['PUNTOS ACUMULADOS'], errors='coerce').fillna(0).astype(int)
            
            # Ordenar por puntos de mayor a menor
            df = df.sort_values(by='PUNTOS ACUMULADOS', ascending=False).reset_index(drop=True)
            df.index += 1
            
            # Formato de medallas para el top 3
            def get_medal(idx):
                if idx == 1: return "🥇"
                if idx == 2: return "🥈"
                if idx == 3: return "🥉"
                return str(idx)
            
            df['Puesto'] = [get_medal(i) for i in df.index]
            
            st.subheader("Clasificación General")
            st.dataframe(
                df[['Puesto', 'Nombre', 'Equipo que integra en la competencia', 'PUNTOS ACUMULADOS']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No se encontró la columna 'PUNTOS ACUMULADOS'. Por favor, verifica el archivo.")
    else:
        st.warning("No hay datos cargados. Ve a la pestaña de 'Cargar Datos' para subir el archivo.")

with tab2:
    st.subheader("Acceso Administrativo")
    password = st.text_input("Contraseña:", type="password")
    
    if password == "Patricia.Faguaga":
        st.success("Acceso concedido")
        uploaded_file = st.file_uploader("Sube el archivo Excel o CSV actualizado", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                # Carga dinámica: detecta si es Excel y usa openpyxl
                if uploaded_file.name.endswith('.xlsx'):
                    # Forzamos el motor openpyxl para evitar el error anterior
                    new_df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    new_df = pd.read_csv(uploaded_file)
                
                if st.button("Confirmar y Actualizar Ranking"):
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Datos actualizados con éxito!")
                    st.info("Cambia a la pestaña de Ranking para ver los resultados.")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
                st.info("Sugerencia: Intenta guardar tu Excel como archivo .CSV y súbelo de nuevo.")
    elif password != "":
        st.error("Contraseña incorrecta")
