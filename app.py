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
DATA_FILE = "datos_competencia_guardados.csv"
INITIAL_FILE = "Datos.csv"

def load_data():
    # 1. Intentar cargar datos guardados por la app
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    
    # 2. Intentar cargar el archivo inicial 'Datos.csv'
    if os.path.exists(INITIAL_FILE):
        try:
            # Probamos con punto y coma primero, que es el formato de tu archivo
            return pd.read_csv(INITIAL_FILE, sep=';')
        except Exception:
            try:
                # Si falla, probamos con coma normal
                return pd.read_csv(INITIAL_FILE)
            except Exception:
                pass
            
    # 3. Si nada existe, devolver estructura base
    return pd.DataFrame(columns=['ID', 'Nombre', 'Equipo que integra en la competencia', 'PUNTOS ACUMULADOS'])

def save_data(df):
    # Guardamos siempre con coma para evitar problemas de compatibilidad interna
    df.to_csv(DATA_FILE, index=False)

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

tab1, tab2 = st.tabs(["🏆 Ranking Mensual", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    
    if not df_raw.empty:
        # Limpiar nombres de columnas
        df_raw.columns = df_raw.columns.str.strip()
        
        # Filtrar filas que tengan un ID numérico (ignora encabezados de fecha o filas vacías)
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        
        # Verificar si existe la columna de puntos
        col_puntos = 'PUNTOS ACUMULADOS'
        if col_puntos in df.columns:
            df[col_puntos] = pd.to_numeric(df[col_puntos], errors='coerce').fillna(0).astype(int)
            
            # Ordenar por puntos (Ranking)
            df = df.sort_values(by=col_puntos, ascending=False).reset_index(drop=True)
            df.index += 1
            
            # Formato de Ranking con medallas
            def get_medal(idx):
                if idx == 1: return "🥇"
                if idx == 2: return "🥈"
                if idx == 3: return "🥉"
                return str(idx)
            
            df['Posición'] = [get_medal(i) for i in df.index]
            
            st.subheader("Clasificación General del Equipo")
            
            # Columnas a mostrar
            vista_df = df[['Posición', 'Nombre', 'Equipo que integra en la competencia', col_puntos]]
            
            st.dataframe(
                vista_df, 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info(f"No se encontró la columna '{col_puntos}' en el archivo.")
    else:
        st.warning("No se detectaron datos. Ve a 'Administrar' para cargar tu archivo Datos.csv.")

with tab2:
    st.subheader("Panel de Control")
    password = st.text_input("Contraseña de acceso:", type="password")
    
    if password == "Patricia.Faguaga":
        st.success("Acceso autorizado")
        uploaded_file = st.file_uploader("Actualizar base de datos (.csv o .xlsx)", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    new_df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    # Al cargar manualmente, intentamos detectar el separador
                    try:
                        new_df = pd.read_csv(uploaded_file, sep=';')
                        if len(new_df.columns) <= 1: # Si no separó bien, probar coma
                            uploaded_file.seek(0)
                            new_df = pd.read_csv(uploaded_file, sep=',')
                    except:
                        uploaded_file.seek(0)
                        new_df = pd.read_csv(uploaded_file)
                
                if st.button("Guardar Cambios y Actualizar Ranking"):
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Datos actualizados con éxito!")
            except Exception as e:
                st.error(f"Error al procesar: {e}")
    elif password != "":
        st.error("Contraseña incorrecta")
