# Importação das bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial da página do Streamlit
st.set_page_config(page_title="Dashboard - Indicadores de Transporte", layout="wide")

# Título principal e descrição do dashboard
st.title("🚌 Dashboard de Mobilidade e Transporte por Raça/Cor")
st.markdown("Análise dos modais de transporte utilizados no Brasil com base em dados raciais e regionais.")

# Caminho do arquivo Excel com os dados
caminho_ficheiro = 'Tabela_13_Meio_de_transporte.xlsx'

# Função para carregar e tratar a planilha de dados
@st.cache_data
def carregar_dados():
    try:
        # Leitura da aba correta ignorando a primeira linha de cabeçalho
        df_brasil = pd.read_excel(caminho_ficheiro, sheet_name='Exemplo gráfico Brasil', skiprows=1)
        df_brasil.columns = ['Meio de Transporte', 'Branca', 'Preta ou Parda', 'Indígena']
        
        # Transformação das colunas de raça em linhas (unpivot/melt)
        df_melted = df_brasil.melt(
            id_vars=['Meio de Transporte'], 
            var_name='Raça/Cor', 
            value_name='Percentual'
        )
        
        # Função interna para agrupar os tipos de transporte
        def categorizar_modal(modal):
            modal_str = str(modal).lower()
            if 'coletivo' in modal_str:
                return 'Público'
            elif 'automóvel' in modal_str or 'moto' in modal_str:
                return 'Particular'
            elif 'bicicleta' in modal_str or 'pé' in modal_str:
                return 'Ativo'
            else:
                return 'Outros'

        # Criação da nova coluna de categoria usando a função interna
        df_melted['Categoria Modal'] = df_melted['Meio de Transporte'].apply(categorizar_modal)
        return df_melted
    except Exception as e:
        # Exibe mensagem de erro caso a planilha não seja encontrada ou lida
        st.error(f"Erro ao carregar a planilha '{caminho_ficheiro}': {e}")
        return None

# Execução da função de carregamento de dados
df = carregar_dados()

# Bloco principal executado apenas se os dados forem carregados com sucesso
if df is not None:
    # Filtros na barra lateral (Sidebar)
    st.sidebar.header("Filtros")
    
    # Filtro multi-seleção de Raça/Cor
    raca_selecionada = st.sidebar.multiselect(
        "Selecione a Raça/Cor:",
        options=df['Raça/Cor'].unique(),
        default=df['Raça/Cor'].unique()
    )
    
    # Filtro multi-seleção de Categoria de Transporte
    categoria_selecionada = st.sidebar.multiselect(
        "Selecione a Categoria de Transporte:",
        options=df['Categoria Modal'].unique(),
        default=df['Categoria Modal'].unique()
    )
    
    # Aplicação dos filtros selecionados no DataFrame principal
    df_filtrado = df[
        (df['Raça/Cor'].isin(raca_selecionada)) & 
        (df['Categoria Modal'].isin(categoria_selecionada))
    ]
    
    # Criação de 3 colunas para exibição dos cartões de métricas
    col1, col2, col3 = st.columns(3)
    
    # Cálculo das métricas básicas (mediana e valor máximo)
    mediana_uso = df_filtrado['Percentual'].median()
    max_uso = df_filtrado.loc[df_filtrado['Percentual'].idxmax()] if not df_filtrado.empty else None
    
    # Preenchimento dos cartões de métricas (KPIs)
    col1.metric("Mediana do Uso (%)", f"{mediana_uso:.2f}%" if pd.notnull(mediana_uso) else "N/A")
    if max_uso is not None:
        col2.metric("Modal Mais Utilizado", f"{max_uso['Meio de Transporte']}")
        col3.metric("Maior Percentual", f"{max_uso['Percentual']:.2f}% ({max_uso['Raça/Cor']})")
    
    # Linha divisória visual
    st.markdown("---")
    
    # Gráfico 1: Barras agrupadas por meio de transporte e raça
    st.subheader("Distribuição por Meio de Transporte e Raça/Cor")
    fig = px.bar(
        df_filtrado, 
        x='Meio de Transporte', 
        y='Percentual', 
        color='Raça/Cor', 
        barmode='group',
        text_auto='.1f',
        title="Uso dos Modais por Raça/Cor"
    )
    st.plotly_chart(fig, width='stretch')
    
    # Gráfico 2: Barras agrupadas pela categoria agregada
    st.subheader("Uso Agrupado por Categoria de Modal")
    df_cat = df_filtrado.groupby(['Categoria Modal', 'Raça/Cor'])['Percentual'].sum().reset_index()
    fig_cat = px.bar(
        df_cat,
        x='Categoria Modal',
        y='Percentual',
        color='Raça/Cor',
        barmode='group',
        title="Uso por Categoria (Público x Particular x Ativo)"
    )
    st.plotly_chart(fig_cat, width='stretch')
    
    # Exibição do conjunto de dados filtrados em formato de tabela interativa
    st.subheader("Tabela de Dados Filtrados")
    st.dataframe(df_filtrado)

# Noticias
st.markdown("---")
st.header("📰 Notícias e Panorama de Mobilidade Urbana & Desigualdade")

# Puxando dados calculados das notícias
pct_coletivo_negros = df[(df['Meio de Transporte'] == 'Transporte coletivo') & (df['Raça/Cor'] == 'Preta ou Parda')]['Percentual'].values[0] if df is not None else 45.8
pct_coletivo_brancos = df[(df['Meio de Transporte'] == 'Transporte coletivo') & (df['Raça/Cor'] == 'Branca')]['Percentual'].values[0] if df is not None else 35.2

# noticia 1
st.subheader("Desigualdade Racial no Acesso ao Transporte Público")
col_text1, col_img1 = st.columns([2, 1])

with col_text1:
    st.markdown(f"""
    A população negra e parda depende significativamente mais do transporte público coletivo para deslocamentos diários no Brasil. 
    Segundo dados do IPEA e estudos do Instituto Mobilidade em Foco, trabalhadores negros chegam a gastar até **20% a mais do seu tempo diário em deslocamentos** quando comparados a trabalhadores brancos.

    **Dado do projeto:**
    Enquanto a utilização do transporte coletivo entre a população **Preta ou Parda é de {pct_coletivo_negros:.1f}%**, entre a população **Branca este valor cai para {pct_coletivo_brancos:.1f}%**. Essa disparidade evidencia como o acesso à infraestrutura viária e ao transporte de qualidade afeta diretamente a inclusão socioeconômica e a mobilidade social.
    """)

with col_img1:
    st.image(
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=600&q=80",
        caption="Ônibus urbano e transporte público coletivo nas grandes capitais",
        width='stretch'
    )

st.markdown("<br>", unsafe_allow_html=True)

# noticia 2
st.subheader("Expansão da Mobilidade Ativa e Infraestrutura de Ciclovias")
col_img2, col_text2 = st.columns([1, 2])

with col_img2:
    st.image(
        "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
        caption="Uso da bicicleta e infraestrutura de mobilidade ativa nas cidades",
        width='stretch'
    )

with col_text2:
    st.markdown("""
    Com o avanço do debate sobre sustentabilidade e a aprovação da Política Nacional de Mobilidade Urbana, diversas cidades brasileiras têm investido no incentivo à **mobilidade ativa (bicicletas e caminhadas)**. 
    
    Apesar dos avanços na construção de ciclovias, pesquisas apontam que a malha cicloviária ainda se concentra majoritariamente nos centros urbanos e bairros de maior renda. Nas periferias, o uso da bicicleta é frequentemente uma necessidade econômica de transporte básico, porém praticado em vias sem sinalização ou proteção adequada, exigindo políticas públicas focadas em segurança e integração modal.
    """)
