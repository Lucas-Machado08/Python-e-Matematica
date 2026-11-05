import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard - Indicadores de Transporte", layout="wide")

st.title("🚌 Dashboard de Mobilidade e Transporte por Raça/Cor")
st.markdown("Análise dos modais de transporte utilizados no Brasil com base em dados raciais e regionais.")

caminho_ficheiro = 'Tabela_13_Meio_de_transporte.xlsx'

@st.cache_data
def carregar_dados():
    try:
        df_brasil = pd.read_excel(caminho_ficheiro, sheet_name='Exemplo gráfico Brasil', skiprows=1)
        df_brasil.columns = ['Meio de Transporte', 'Branca', 'Preta ou Parda', 'Indígena']
        
        df_melted = df_brasil.melt(
            id_vars=['Meio de Transporte'], 
            var_name='Raça/Cor', 
            value_name='Percentual'
        )
        
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

        df_melted['Categoria Modal'] = df_melted['Meio de Transporte'].apply(categorizar_modal)
        return df_melted
    except Exception as e:
        st.error(f"Erro ao carregar a planilha '{caminho_ficheiro}': {e}")
        return None

df = carregar_dados()

if df is not None:
    st.sidebar.header("Filtros")
    raca_selecionada = st.sidebar.multiselect(
        "Selecione a Raça/Cor:",
        options=df['Raça/Cor'].unique(),
        default=df['Raça/Cor'].unique()
    )
    
    categoria_selecionada = st.sidebar.multiselect(
        "Selecione a Categoria de Transporte:",
        options=df['Categoria Modal'].unique(),
        default=df['Categoria Modal'].unique()
    )
    
    df_filtrado = df[
        (df['Raça/Cor'].isin(raca_selecionada)) & 
        (df['Categoria Modal'].isin(categoria_selecionada))
    ]
    
    col1, col2, col3 = st.columns(3)
    
    mediana_uso = df_filtrado['Percentual'].median()
    max_uso = df_filtrado.loc[df_filtrado['Percentual'].idxmax()] if not df_filtrado.empty else None
    
    col1.metric("Mediana do Uso (%)", f"{mediana_uso:.2f}%" if pd.notnull(mediana_uso) else "N/A")
    if max_uso is not None:
        col2.metric("Modal Mais Utilizado", f"{max_uso['Meio de Transporte']}")
        col3.metric("Maior Percentual", f"{max_uso['Percentual']:.2f}% ({max_uso['Raça/Cor']})")
    
    st.markdown("---")
    
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
    st.plotly_chart(fig, use_container_width=True)
    
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
    st.plotly_chart(fig_cat, use_container_width=True)
    
    st.subheader("Tabela de Dados Filtrados")
    st.dataframe(df_filtrado)
