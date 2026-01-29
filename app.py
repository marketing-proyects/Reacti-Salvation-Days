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
        color: #DA291C;
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
    
    # 2. Cargar archivo inicial Datos.csv con manejo de errores de codificación
    if os.path.exists(INITIAL_FILE):
        # Probamos combinaciones comunes de Excel (Punto y coma + latin-1)
        for encoding in ['latin-1', 'utf-8', 'iso-8859-1']:
            for sep in [';', ',']:
                try:
                    df = pd.read_csv(INITIAL_FILE, sep=sep, encoding=encoding)
                    if len(df.columns) > 1: # Si encontró más de una columna, es el separador correcto
                        return df
                except Exception:
                    continue
            
    return pd.DataFrame()

def save_data(df):
    # Guardamos en UTF-8 para evitar errores futuros en la app
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

tab1, tab2 = st.tabs(["🏆 Ranking Mensual", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        
        # Filtro para ignorar filas sin ID (como la fila de fecha bajo los encabezados)
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        
        col_pts = 'PUNTOS ACUMULADOS'
        if col_pts in df.columns:
            df[col_pts] = pd.to_numeric(df[col_pts], errors='coerce').fillna(0).astype(int)
            df = df.sort_values(by=col_pts, ascending=False).reset_index(drop=True)
            df.index += 1
            
            def format_rank(idx):
                if idx == 1: return "🥇"
                elif idx == 2: return "🥈"
                elif idx == 3: return "🥉"
                return str(idx)
            
            df['Pos.'] = [format_rank(i) for i in df.index]
            
            st.subheader("Clasificación de Clientes")
            cols_mostrar = ['Pos.', 'Nombre', 'Equipo que integra en la competencia', col_pts]
            st.dataframe(df[cols_mostrar], use_container_width=True, hide_index=True)
        else:
            st.error(f"No se encuentra la columna '{col_pts}'")
    else:
        st.warning("⚠️ No se pudieron cargar los datos de 'Datos.csv'.")

with tab2:
    st.subheader("Panel Administrativo")
    pwd = st.text_input("Contraseña:", type="password")
    
    if pwd == "Patricia.Faguaga":
        st.success("Acceso Permitido")
        archivo_nuevo = st.file_uploader("Actualizar base (.csv o .xlsx)", type=["csv", "xlsx"])
        
        if archivo_nuevo:
            try:
                if archivo_nuevo.name.endswith('.xlsx'):
                    new_df = pd.read_excel(archivo_nuevo, engine='openpyxl')
                else:
                    # Intento de lectura robusta para CSV subido
                    new_df = None
                    for enc in ['latin-1', 'utf-8']:
                        for s in [';', ',']:
                            try:
                                archivo_nuevo.seek(0)
                                temp_df = pd.read_csv(archivo_nuevo, sep=s, encoding=enc)
                                if len(temp_df.columns) > 1:
                                    new_df = temp_df
                                    break
                            except: continue
                        if new_df is not None: break
                
                if st.button("Publicar Resultados") and new_df is not None:
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Datos actualizados con éxito!")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
    elif pwd != "":
        st.error("Contraseña incorrecta")
