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
    .stDataFrame {{
        border: 1px solid #DA291C;
        border-radius: 5px;
    }}
    </style>
    """
    st.markdown(font_style, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DATA_FILE = "db_competencia.csv"
INITIAL_FILE = "Datos.csv"

def load_data():
    # 1. Cargar datos guardados si existen
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    
    # 2. Cargar archivo inicial Datos.csv
    if os.path.exists(INITIAL_FILE):
        try:
            # Tu archivo CSV usa punto y coma (;)
            return pd.read_csv(INITIAL_FILE, sep=';', encoding='utf-8')
        except Exception:
            return pd.read_csv(INITIAL_FILE, sep=',', encoding='utf-8')
            
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

tab1, tab2 = st.tabs(["🏆 Ranking Mensual", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    
    if not df_raw.empty:
        # Limpieza de nombres de columnas
        df_raw.columns = df_raw.columns.str.strip()
        
        # Filtrar solo filas con ID válido (evita la fila de '12 de Febrero' que no tiene ID)
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        
        # Columna de puntos
        col_pts = 'PUNTOS ACUMULADOS'
        
        if col_pts in df.columns:
            # Convertir a número y rellenar vacíos
            df[col_pts] = pd.to_numeric(df[col_pts], errors='coerce').fillna(0).astype(int)
            
            # Ordenar por Ranking
            df = df.sort_values(by=col_pts, ascending=False).reset_index(drop=True)
            df.index += 1
            
            # Medallas
            def format_rank(idx):
                if idx == 1: return "🥇"
                if idx == 2: return "🥈"
                if idx == 3: return "🥉"
                return str(idx)
            
            df['Pos.'] = [format_rank(i) for i in df.index]
            
            st.subheader("Clasificación de Clientes")
            
            # Mostrar tabla limpia
            cols_mostrar = ['Pos.', 'Nombre', 'Equipo que integra en la competencia', col_pts]
            st.dataframe(
                df[cols_mostrar], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.error(f"Error: No se encuentra la columna '{col_pts}'")
    else:
        st.warning("⚠️ El archivo 'Datos.csv' no fue encontrado en el repositorio.")

with tab2:
    st.subheader("Carga de Datos")
    pwd = st.text_input("Contraseña:", type="password")
    
    if pwd == "Patricia.Faguaga":
        st.success("Acceso Permitido")
        archivo_nuevo = st.file_uploader("Actualizar base (.csv o .xlsx)", type=["csv", "xlsx"])
        
        if archivo_nuevo:
            try:
                if archivo_nuevo.name.endswith('.xlsx'):
                    new_df = pd.read_excel(archivo_nuevo, engine='openpyxl')
                else:
                    # Intentar leer CSV con ; y si no con ,
                    try:
                        new_df = pd.read_csv(archivo_nuevo, sep=';')
                        if len(new_df.columns) <= 1: 
                            archivo_nuevo.seek(0)
                            new_df = pd.read_csv(archivo_nuevo, sep=',')
                    except:
                        archivo_nuevo.seek(0)
                        new_df = pd.read_csv(archivo_nuevo)
                
                if st.button("Publicar Resultados"):
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Ranking actualizado con éxito!")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
    elif pwd != "":
        st.error("Contraseña incorrecta")
