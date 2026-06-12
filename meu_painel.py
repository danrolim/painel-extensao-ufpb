import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. Configuração inicial da página web
st.set_page_config(page_title="Painel PROEX | UFPB", page_icon="🎓", layout="wide")

# Função auxiliar para converter imagem local em string Base64
def converter_imagem_local(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

# Caminhos das imagens (caminhos relativos para a nuvem)
img_ufpb_base64 = converter_imagem_local("logo_ufpb.png")
img_proex_base64 = converter_imagem_local("logo_proex.png")

# ==========================================
# 2. IDENTIDADE VISUAL PROEX (CSS)
# ==========================================
COR_AZUL = "#2D2E83"
COR_VERMELHA = "#E30613"

st.markdown(f"""
    <style>
    .cabecalho-proex {{
        background-color: #FFFFFF;
        padding: 20px 30px;
        border-radius: 10px;
        border: 3px solid {COR_AZUL};
        border-bottom: 7px solid {COR_VERMELHA};
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
    }}
    .logo-img {{ height: 80px; object-fit: contain; }}
    .titulo-container {{ text-align: center; flex-grow: 1; }}
    .titulo-container h1 {{
        color: {COR_AZUL}; margin: 0; font-size: 2.2rem;
        font-family: 'Arial', sans-serif; font-weight: bold;
    }}
    .titulo-container h3 {{
        color: {COR_AZUL}; margin: 5px 0 0 0; font-size: 1.1rem;
        font-family: 'Arial', sans-serif; font-weight: 600; opacity: 0.9;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. Renderização do Cabeçalho
src_ufpb = f"data:image/png;base64,{img_ufpb_base64}" if img_ufpb_base64 else ""
src_proex = f"data:image/png;base64,{img_proex_base64}" if img_proex_base64 else ""

st.markdown(f"""
    <div class="cabecalho-proex">
        {"<img class='logo-img' src='" + src_ufpb + "' alt='Logo UFPB'>" if img_ufpb_base64 else "<div style='width:80px;'></div>"}
        <div class="titulo-container">
            <h1>Panorama da Extensão Universitária</h1>
            <h3>Pró-Reitoria de Extensão (PROEX) | Universidade Federal da Paraíba</h3>
        </div>
        {"<img class='logo-img' src='" + src_proex + "' alt='Logo PROEX'>" if img_proex_base64 else "<div style='width:80px;'></div>"}
    </div>
""", unsafe_allow_html=True)

# 4. Carregando os dados
@st.cache_data
def carregar_dados():
    # Caminho relativo para a nuvem
    caminho = 'base_painel_2020_2025.csv'
    dados = pd.read_csv(caminho)
    if len(dados.columns) == 1:
        dados = pd.read_csv(caminho, sep=';')
        
    ordem_colunas = [
        'Ano Projeto', 'Codigo', 'Tipo de Ação', 'Titulo', 
        'CENTRO DE ENSINO', 'Data Inicio', 'Data Fim',  
        'Situacao', 'Status_macro', 'Fonte Financiamento'
    ]
    colunas_existentes = [col for col in ordem_colunas if col in dados.columns]
    return dados[colunas_existentes]

df = carregar_dados()

# ==========================================
# 5. ÁREA DE FILTROS
# ==========================================
st.subheader("🔍 Filtros de Análise")
col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

with col_filtro1:
    lista_anos = sorted(df['Ano Projeto'].dropna().unique())
    filtro_ano = st.multiselect("Selecione o Ano:", lista_anos)

with col_filtro2:
    lista_centros = sorted(df['CENTRO DE ENSINO'].astype(str).unique())
    filtro_centro = st.multiselect("Selecione o Centro de Ensino:", lista_centros)

with col_filtro3:
    lista_acoes = sorted(df['Tipo de Ação'].dropna().unique())
    filtro_acao = st.multiselect("Selecione o Tipo de Ação:", lista_acoes)

with col_filtro4:
    lista_status = sorted(df['Status_macro'].dropna().unique()) 
    filtro_status = st.multiselect("Selecione o Status:", lista_status)

# ==========================================
# 6. LÓGICA DE FILTRAGEM
# ==========================================
df_filtrado = df.copy()

if filtro_ano:
    df_filtrado = df_filtrado[df_filtrado['Ano Projeto'].isin(filtro_ano)]
if filtro_centro:
    df_filtrado = df_filtrado[df_filtrado['CENTRO DE ENSINO'].isin(filtro_centro)]
if filtro_acao:
    df_filtrado = df_filtrado[df_filtrado['Tipo de Ação'].isin(filtro_acao)]
if filtro_status:
    df_filtrado = df_filtrado[df_filtrado['Status_macro'].isin(filtro_status)]

st.markdown("---")

# ==========================================
# 7. GRÁFICO 1: SÉRIE TEMPORAL
# ==========================================
df_ano = df_filtrado['Ano Projeto'].value_counts().reset_index()
df_ano.columns = ['Ano', 'Quantidade']
df_ano = df_ano.sort_values('Ano') 
df_ano['Ano'] = df_ano['Ano'].astype(int).astype(str)

fig_temporal = px.bar(df_ano, x='Ano', y='Quantidade', text_auto=True, 
                      title="Série Temporal: Volume de Ações por Ano (2020-2025)",
                      color_discrete_sequence=[COR_AZUL]) 
fig_temporal.update_xaxes(type='category', title_text="Ano de Início")
fig_temporal.update_yaxes(title_text="Total de Projetos")
fig_temporal.update_layout(showlegend=False)
st.plotly_chart(fig_temporal, use_container_width=True)

# ==========================================
# 8. GRÁFICOS INFERIORES
# ==========================================
col_graf1, col_graf2, col_graf3 = st.columns(3)

with col_graf1:
    df_centro = df_filtrado['CENTRO DE ENSINO'].value_counts().reset_index()
    df_centro.columns = ['Centro de Ensino', 'Quantidade']
    df_centro = df_centro.head(10).sort_values('Quantidade', ascending=True)
    
    fig_centro = px.bar(df_centro, y='Centro de Ensino', x='Quantidade', orientation='h', 
                         title="Top 10 Centros de Ensino", text_auto=True,
                         color_discrete_sequence=[COR_VERMELHA])
    fig_centro.update_yaxes(title_text="")
    st.plotly_chart(fig_centro, use_container_width=True)

with col_graf2:
    df_acao = df_filtrado['Tipo de Ação'].value_counts().reset_index()
    df_acao.columns = ['Tipo de Ação', 'Quantidade']
    
    fig_acao = px.bar(df_acao, x='Tipo de Ação', y='Quantidade', 
                      title="Por Tipo de Ação", text_auto=True,
                      color_discrete_sequence=[COR_AZUL]) 
    fig_acao.update_xaxes(title_text="")
    fig_acao.update_layout(showlegend=False)
    st.plotly_chart(fig_acao, use_container_width=True)

with col_graf3:
    df_status = df_filtrado['Status_macro'].value_counts().reset_index()
    df_status.columns = ['Status', 'Quantidade']
    
    fig_status = px.bar(df_status, x='Status', y='Quantidade', 
                        title="Por Status Macro", text_auto=True,
                        color='Status',
                        color_discrete_sequence=[COR_AZUL, '#4A4B9D', '#9192C3', COR_VERMELHA])
    fig_status.update_xaxes(title_text="")
    fig_status.update_layout(showlegend=False)
    st.plotly_chart(fig_status, use_container_width=True)

# ==========================================
# 9. VISUALIZAÇÃO DOS DADOS BRUTOS E DOWNLOAD
# ==========================================
st.markdown("---")
st.subheader("📋 Tabela de Dados Detalhada")
st.dataframe(df_filtrado, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.download_button(
    label="📥 Baixar Dados Filtrados (CSV)",
    data=df_filtrado.to_csv(index=False, sep=';').encode('utf-8-sig'),
    file_name="dados_extensao_proex.csv",
    mime="text/csv"
)
