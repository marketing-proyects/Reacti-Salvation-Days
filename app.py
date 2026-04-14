import streamlit as st
import pandas as pd
import base64
import os
import glob
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="REACTISALVATION DAYS", 
    layout="wide",
    page_icon="favicon.png" 
)

# --- 2. FUNCIONES PARA RECURSOS ---
def get_base64_font(font_file):
    try:
        if os.path.exists(font_file):
            with open(font_file, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return None

# --- 3. ESTILOS CSS PERSONALIZADOS ---
font_bold = get_base64_font("WuerthBold.ttf")
font_book = get_base64_font("WuerthBook.ttf")

st.markdown(f"""
<style>
    @font-face {{ font-family: 'WuerthBold'; src: url(data:font/ttf;base64,{font_bold}) format('truetype'); }}
    @font-face {{ font-family: 'WuerthBook'; src: url(data:font/ttf;base64,{font_book}) format('truetype'); }}
    html, body, [class*="css"], .stMarkdown {{ font-family: 'WuerthBook', sans-serif !important; }}
    h1, h2, h3, b, strong {{ font-family: 'WuerthBold', sans-serif !important; color: #DA291C; }}
    [data-testid="stMetricValue"] {{ font-family: 'WuerthBold', sans-serif !important; color: #DA291C; }}
    .logo-container {{ border-top: 1px solid white; border-left: 1px solid white; display: inline-block; padding: 0; margin: 0; }}
    [data-testid="stHeaderActionElements"], .st-emotion-cache-15zrgzn, .st-emotion-cache-kg9q0s, a.anchor-link, 
    button.copy-to-clipboard, [data-testid="stHeader"], .st-emotion-cache-10trblm,
    div[data-testid="stVerticalBlock"] > div > div > div > h3 > a {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. GESTIÓN DE DATOS ---
DATA_FILE = "db_competencia.csv"
INITIAL_FILE = "Datos.csv"
EXCEL_HISTORICO = "Evolucion_Manual.xlsx"

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

# --- 5. LOGOS DE CABECERA ---
logo_empresa = glob.glob("logo_wurth.*")
logo_competencia = glob.glob("imagen.png") 

col_l, col_r = st.columns([1, 4])
with col_l:
    if logo_empresa:
        with open(logo_empresa[0], "rb") as f:
            b64_logo = base64.b64encode(f.read()).decode()
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64_logo}" width="180"></div>', unsafe_allow_html=True)
with col_r:
    if logo_competencia:
        with open(logo_competencia[0], "rb") as f:
            b64_comp = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/png;base64,{b64_comp}" width="500">', unsafe_allow_html=True)

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranking Actual", "📅 Evolución Histórica", "🎟️ Cupones disponibles", "⚙️ Administrar"])

with tab1:
    df_raw = load_data()
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df_raw['ID_num'] = pd.to_numeric(df_raw['ID'], errors='coerce')
        df = df_raw[df_raw['ID_num'].notnull()].copy()
        col_pts = 'PUNTOS ACUMULADOS'
        
        if col_pts in df.columns:
            df[col_pts] = pd.to_numeric(df[col_pts], errors='coerce').fillna(0).astype(int)
            def cat_eq(n):
                n = str(n).lower()
                if 'tandem' in n: return 'Tandem'
                if 'cartera propia' in n: return 'Cartera Propia'
                return 'Otros'
            
            df['Eq_R'] = df['Equipo que integra en la competencia'].apply(cat_eq)
            s_tan = df[df['Eq_R'] == 'Tandem'][col_pts].sum()
            s_cp = df[df['Eq_R'] == 'Cartera Propia'][col_pts].sum()

            st.subheader("Marcador por Equipos")
            c1, c2 = st.columns(2)
            c1.metric(f"{'👑 ' if s_tan > s_cp else ''}Tandem", f"{s_tan} Pts")
            c2.metric(f"{'👑 ' if s_cp > s_tan else ''}Cartera Propia", f"{s_cp} Pts")
            st.divider()

            df = df.sort_values(by=col_pts, ascending=False).reset_index(drop=True)
            df.index += 1
            df['Pos.'] = [("🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else str(i)) for i in df.index]
            st.subheader("Ranking Individual")
            st.dataframe(df[['Pos.', 'Nombre', 'Equipo que integra en la competencia', col_pts]], use_container_width=True, hide_index=True)
        else:
            st.error(f"No se encontró la columna '{col_pts}'.")
    else:
        st.warning("⚠️ Sin datos.")

with tab2:
    st.subheader("Desempeño Acumulado (Histórico)")
    if os.path.exists(EXCEL_HISTORICO):
        try:
            h_df = pd.read_excel(EXCEL_HISTORICO, engine='openpyxl')
            h_df.columns = h_df.columns.str.strip()
            
            # --- LIMPIEZA ROBUSTA ---
            # 1. Asegurar que Nombre sea string y no tenga nulos
            h_df['Nombre'] = h_df['Nombre'].astype(str).replace('nan', '').str.strip()
            h_df = h_df[h_df['Nombre'] != ""].copy()
            
            # 2. Asegurar que Puntos sea numérico
            if 'PUNTOS ACUMULADOS' in h_df.columns:
                h_df['PUNTOS ACUMULADOS'] = pd.to_numeric(h_df['PUNTOS ACUMULADOS'], errors='coerce').fillna(0)

            if not h_df.empty:
                # 3. Filtrar nombres válidos para el selector (evita el error de comparación)
                lista_vendedores = [v for v in h_df['Nombre'].unique() if isinstance(v, str) and v != ""]
                vendedor = st.selectbox("Filtrar por Vendedor:", ["Todos"] + sorted(lista_vendedores))
                
                df_final = h_df.copy()
                if vendedor != "Todos":
                    df_final = df_final[df_final['Nombre'] == vendedor]
                
                if 'PUNTOS ACUMULADOS' in df_final.columns:
                    eje_x = 'Mes' if 'Mes' in df_final.columns else None
                    st.area_chart(df_final, x=eje_x, y='PUNTOS ACUMULADOS')
                
                st.dataframe(df_final, use_container_width=True, hide_index=True)
            else:
                st.warning("El archivo está cargado pero no contiene datos válidos en la columna 'Nombre'.")
        except Exception as e:
            st.error(f"Error al procesar el Excel: {e}")
    else:
        st.info(f"📂 Archivo `{EXCEL_HISTORICO}` no detectado.")

with tab3:
    st.subheader("Cupones vigentes")
    url_cupones = "https://viewer.ipaper.io/wurth-uruguay/cupones/cupones-regalos-reacti-salvation-days/cupones-activos-reacti-salvation-days-wurth-y-wmaxpdf/"
    st.markdown(f'<a href="{url_cupones}" target="_blank"><button style="background-color: #DA291C; color: white; padding: 12px 24px; border: none; border-radius: 5px; font-family: \'WuerthBold\'; cursor: pointer;">Ir a Cupones Würth</button></a>', unsafe_allow_html=True)

with tab4:
    st.subheader("Panel Administrativo")
    pwd = st.text_input("Contraseña:", type="password")
    if pwd == "Patricia.Faguaga":
        archivo = st.file_uploader("Subir Ranking Actual (Datos.csv)", type=["csv", "xlsx"])
        if archivo and st.button("Guardar Datos"):
            try:
                if archivo.name.endswith('.xlsx'):
                    new_df = pd.read_excel(archivo, engine='openpyxl')
                else:
                    new_df = pd.read_csv(archivo, sep=None, engine='python', encoding='latin-1')
                new_df.to_csv(DATA_FILE, index=False, encoding='utf-8')
                st.success("¡Datos actualizados!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
