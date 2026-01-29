import streamlit as st
import pandas as pd
import base64
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="REACTISALVATION DAYS", layout="wide")

# --- FUNCIONES PARA RECURSOS ---
def get_base64_font(font_file):
    try:
        if os.path.exists(font_file):
            with open(font_file, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except Exception:
        return None
    return None

def load_image(image_path):
    if os.path.exists(image_path):
        return image_path
    return None

# --- LOGO Y ESTILOS ---
logo_path = load_image("logo_wurth.jpg") # Asegúrate de que el nombre sea exacto

if logo_path:
    # Centrar logo mediante columnas
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 1, 1])
    with col_logo_2:
        st.image(logo_path, width=250)

# --- APLICAR FUENTES ---
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
    [data-testid="stMetricValue"] {{
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
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    if os.path.exists(INITIAL_FILE):
        for enc in ['latin-1', 'utf-8', 'iso-8859-1']:
            for sep in [';', ',']:
                try:
                    df = pd.read_csv(INITIAL_FILE, sep=sep, encoding=enc)
                    if len(df.columns) > 1:
                        return df
                except: continue
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')

# --- INTERFAZ ---
st.title("REACTISALVATION DAYS")

tab1, tab2 = st.tabs(["🏆 Ranking y Equipos", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        
        col_pts = 'PUNTOS ACUMULADOS'
        if col_pts in df.columns:
            df[col_pts] = pd.to_numeric(df[col_pts], errors='coerce').fillna(0).astype(int)
            
            # --- SCORE POR EQUIPOS ---
            def categorizar_equipo(nombre_equipo):
                nombre = str(nombre_equipo).lower().strip()
                if 'tandem' in nombre: return 'Tandem'
                if 'cartera propia' in nombre: return 'Cartera Propia'
                return 'Otros'

            df['Equipo_Resumido'] = df['Equipo que integra en la competencia'].apply(categorizar_equipo)
            
            score_tandem = df[df['Equipo_Resumido'] == 'Tandem'][col_pts].sum()
            score_cp = df[df['Equipo_Resumido'] == 'Cartera Propia'][col_pts].sum()

            st.subheader("Marcador General")
            c1, c2 = st.columns(2)
            win_t = "👑 " if score_tandem > score_cp else ""
            win_cp = "👑 " if score_cp > score_tandem else ""
            
            c1.metric(f"{win_t}Tandem", f"{score_tandem} Puntos")
            c2.metric(f"{win_cp}Cartera Propia", f"{score_cp} Puntos")
            
            st.divider()

            # --- RANKING INDIVIDUAL ---
            df = df.sort_values(by=col_pts, ascending=False).reset_index(drop=True)
            df.index += 1
            
            def format_rank(idx):
                if idx == 1: return "🥇"
                if idx == 2: return "🥈"
                if idx == 3: return "🥉"
                return str(idx)
            
            df['Pos.'] = [format_rank(i) for i in df.index]
            
            st.subheader("Ranking Individual")
            cols_mostrar = ['Pos.', 'Nombre', 'Equipo que integra en la competencia', col_pts]
            st.dataframe(df[cols_mostrar], use_container_width=True, hide_index=True)
        else:
            st.error("No se encontró la columna de puntos.")
    else:
        st.warning("⚠️ Sin datos. Carga 'Datos.csv' o usa el panel Administrar.")

with tab2:
    st.subheader("Panel Administrativo")
    pwd = st.text_input("Contraseña:", type="password")
    
    if pwd == "Patricia.Faguaga":
        st.success("Acceso Permitido")
        archivo_nuevo = st.file_uploader("Actualizar base", type=["csv", "xlsx"])
        
        if archivo_nuevo:
            try:
                if archivo_nuevo.name.endswith('.xlsx'):
                    new_df = pd.read_excel(archivo_nuevo, engine='openpyxl')
                else:
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
                
                if st.button("Actualizar y Publicar"):
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Datos actualizados!")
            except Exception as e:
                st.error(f"Error: {e}")
    elif pwd != "":
        st.error("Contraseña incorrecta")
