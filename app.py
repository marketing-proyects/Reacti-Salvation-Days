import streamlit as st
import pandas as pd
import base64
import os
import glob
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="REACTI-SALVATION DAYS", layout="wide")

# --- FUNCIONES PARA RECURSOS ---
def get_base64_font(font_file):
    try:
        if os.path.exists(font_file):
            with open(font_file, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return None

# --- ESTILOS CSS PERSONALIZADOS ---
font_bold = get_base64_font("WuerthBold.ttf")
font_book = get_base64_font("WuerthBook.ttf")

custom_css = f"""
<style>
    @font-face {{ font-family: 'WuerthBold'; src: url(data:font/ttf;base64,{font_bold}) format('truetype'); }}
    @font-face {{ font-family: 'WuerthBook'; src: url(data:font/ttf;base64,{font_book}) format('truetype'); }}

    html, body, [class*="css"], .stMarkdown {{ font-family: 'WuerthBook', sans-serif !important; }}
    h1, h2, h3, b, strong {{ font-family: 'WuerthBold', sans-serif !important; color: #DA291C; }}
    [data-testid="stMetricValue"] {{ font-family: 'WuerthBold', sans-serif !important; color: #DA291C; }}

    /* ESTILO LOGO: 1px de espacio blanco arriba y a la izquierda */
    .logo-container {{
        border-top: 1px solid white;
        border-left: 1px solid white;
        display: inline-block;
        line-height: 0;
    }}

    /* ELIMINAR LOS CLIPS Y ANCLAJES DEFINITIVAMENTE */
    [data-testid="stHeaderActionElements"], 
    .st-emotion-cache-15zrgzn, 
    .st-emotion-cache-kg9q0s, 
    a.anchor-link, 
    button.copy-to-clipboard, 
    [data-testid="stHeader"] {{
        display: none !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DATA_FILE = "db_competencia.csv"
INITIAL_FILE = "Datos.csv"
HISTORICO_FILE = "db_historico_desempeno.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    if os.path.exists(INITIAL_FILE):
        for enc in ['latin-1', 'utf-8', 'iso-8859-1']:
            for sep in [';', ',']:
                try:
                    df = pd.read_csv(INITIAL_FILE, sep=sep, encoding=enc)
                    if len(df.columns) > 1: return df
                except: continue
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')
    df_hist = df[pd.to_numeric(df['ID'], errors='coerce').notnull()].copy()
    df_hist['Fecha Competencia'] = datetime.now().strftime("%d/%m/%Y")
    columnas_hist = ['Fecha Competencia', 'Nombre', 'Equipo que integra en la competencia', 
                     'Clientes Reactivados', 'Clientes 11 meses', 'PUNTOS ACUMULADOS']
    existentes = [c for c in columnas_hist if c in df_hist.columns]
    df_final_hist = df_hist[existentes]

    if os.path.exists(HISTORICO_FILE):
        old_hist = pd.read_csv(HISTORICO_FILE)
        old_hist = old_hist[old_hist['Fecha Competencia'] != datetime.now().strftime("%d/%m/%Y")]
        new_hist = pd.concat([old_hist, df_final_hist], ignore_index=True)
    else:
        new_hist = df_final_hist
    new_hist.to_csv(HISTORICO_FILE, index=False, encoding='utf-8')

# --- ENCABEZADO: LOGO ---
logo_search = glob.glob("logo_wurth.*")
if logo_search:
    col_l, col_r = st.columns([1, 4])
    with col_l:
        # Aplicamos el contenedor con el borde de 1px blanco solicitado
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{base64.b64encode(open(logo_search[0], "rb").read()).decode()}" width="180"></div>', unsafe_allow_html=True)

st.title("REACTI-SALVATION DAYS")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranking Actual", "📅 Evolución Histórica", "🎟️ Cupones disponibles", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df = df_raw[pd.to_numeric(df_raw['ID'], errors='coerce').notnull()].copy()
        col_pts = 'PUNTOS ACUMULADOS'
        
        if col_pts in df.columns:
            df[col_pts] = pd.to_numeric(df[col_pts], errors='coerce').fillna(0).astype(int)
            
            def cat_eq(n):
                n = str(n).lower()
                return 'Tandem' if 'tandem' in n else 'Cartera Propia' if 'cartera propia' in n else 'Otros'
            
            df['Eq_R'] = df['Equipo que integra en la competencia'].apply(cat_eq)
            s_tan = df[df['Eq_R'] == 'Tandem'][col_pts].sum()
            s_cp = df[df['Eq_R'] == 'Cartera Propia'][col_pts].sum()

            c1, c2 = st.columns(2)
            c1.metric(f"{'👑 ' if s_tan > s_cp else ''}Tandem", f"{s_tan} Pts")
            c2.metric(f"{'👑 ' if s_cp > s_tan else ''}Cartera Propia", f"{s_cp} Pts")
            st.divider()

            df = df.sort_values(by=col_pts, ascending=False).reset_index(drop=True)
            df.index += 1
            df['Pos.'] = [("🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else str(i)) for i in df.index]
            st.dataframe(df[['Pos.', 'Nombre', 'Equipo que integra en la competencia', col_pts]], 
                         use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Histórico de Desempeño por Mes")
    if os.path.exists(HISTORICO_FILE):
        h_df = pd.read_csv(HISTORICO_FILE)
        persona = st.selectbox("Seleccionar Competidora:", ["Todas"] + sorted(h_df['Nombre'].unique().tolist()))
        if persona != "Todas":
            h_df = h_df[h_df['Nombre'] == persona]
        st.dataframe(h_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros históricos todavía.")

with tab3:
    st.subheader("Cupones de Descuento")
    st.write("Accede a los cupones vigentes (EXCLUSIVOS) para el dia de la competencia en el siguiente enlace:")
    
    # URL Cupones Exclusivos competencia
    url_cupones = "https://eshop.wurth.com.uy/es/UY/UYU/"
    
    st.markdown(f"""
        <a href="{url_cupones}" target="_blank">
            <button style="
                background-color: #DA291C;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border: none;
                border-radius: 8px;
                font-family: 'WuerthBold', sans-serif;">
                Ir a E-Shop Würth
            </button>
        </a>
    """, unsafe_allow_html=True)

with tab4:
    st.subheader("Cargar Datos")
    pwd = st.text_input("Contraseña:", type="password")
    if pwd == "Patricia.Faguaga":
        archivo = st.file_uploader("Subir archivo del día", type=["csv", "xlsx"])
        if archivo:
            if st.button("Guardar y Registrar este Mes"):
                try:
                    if archivo.name.endswith('.xlsx'):
                        new_df = pd.read_excel(archivo, engine='openpyxl')
                    else:
                        new_df = pd.read_csv(archivo, sep=None, engine='python', encoding='latin-1')
                    save_data(new_df)
                    st.balloons()
                    st.success("¡Datos guardados!")
                except Exception as e: st.error(f"Error: {e}")
