import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# Configurações de estilo
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

st.set_page_config(page_title="Violência Contra Mulheres", layout="wide")
st.title("🔫 Violência Contra Mulheres por Armas de Fogo no Brasil")

st.markdown(f"""
Este painel interativo tem como objetivo analisar os homicídios de mulheres por armas de fogo no Brasil.  
Você pode explorar os dados por estado, cidade e também observar tendências temporais.
""")

# Upload e leitura do CSV
st.sidebar.header("📂 Upload e Filtros")
uploaded_file = st.sidebar.file_uploader("Escolha o arquivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=';')

    # Pré-processamento
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df.dropna(subset=['valor', 'cod', 'nome', 'período'])
    df['período'] = df['período'].astype(str)
    df['uf'] = df['cod'].astype(str).str[:2]
    mapa_uf = {
        '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
        '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL',
        '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
        '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
    }
    df['sigla_uf'] = df['uf'].map(mapa_uf)

    def classifica(valor):
        if valor < 100:
            return '🔵 Baixo'
        elif valor < 300:
            return '🟠 Médio'
        else:
            return '🔴 Alto'

    # Filtros
    estados = ['Todos'] + sorted(df['sigla_uf'].dropna().unique())
    estado_sel = st.sidebar.selectbox("Selecione o Estado", estados)

    if estado_sel != 'Todos':
        cidades = ['Todas'] + sorted(df[df['sigla_uf'] == estado_sel]['nome'].unique())
    else:
        cidades = ['Todas'] + sorted(df['nome'].unique())

    cidade_sel = st.sidebar.selectbox("Selecione a Cidade", cidades)

    # Filtrar dataset
    df_filtrado = df.copy()
    if estado_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['sigla_uf'] == estado_sel]
    if cidade_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['nome'] == cidade_sel]

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📅 Baixar CSV Filtrado",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )

    with st.expander("🔍 Visualizar dados filtrados"):
        st.dataframe(df_filtrado)

    # Gráficos
    st.header("📊 Análises Visuais")

    # Top cidades
    top_cidades = df_filtrado.groupby('nome')['valor'].sum().sort_values(ascending=False).head(10).reset_index()
    top_cidades['classificacao'] = top_cidades['valor'].apply(classifica)

    fig1, ax1 = plt.subplots()
    sns.barplot(data=top_cidades, x='valor', y='nome', palette="Reds_d", ax=ax1)
    ax1.set_title("🔴 Top 10 cidades com mais homicídios de mulheres por armas de fogo")
    ax1.set_xlabel("Total de homicídios")
    ax1.set_ylabel("Cidade")
    st.pyplot(fig1)

    # Top estados
    top_estados = df_filtrado.groupby('sigla_uf')['valor'].sum().sort_values(ascending=False).head(10).reset_index()
    top_estados['classificacao'] = top_estados['valor'].apply(classifica)

    fig2, ax2 = plt.subplots()
    sns.barplot(data=top_estados, x='valor', y='sigla_uf', palette="Blues_d", ax=ax2)
    ax2.set_title("🔵 Top 10 estados com mais homicídios de mulheres por armas de fogo")
    ax2.set_xlabel("Total de homicídios")
    ax2.set_ylabel("Estado")
    st.pyplot(fig2)

    # Evolução temporal
    df_total_ano = df_filtrado.groupby('período')['valor'].sum().reset_index()
    df_total_ano['classificacao'] = df_total_ano['valor'].apply(classifica)

    fig3, ax3 = plt.subplots()
    sns.lineplot(data=df_total_ano, x='período', y='valor', marker='o', color='black', ax=ax3)
    ax3.set_title("📈 Evolução temporal dos homicídios de mulheres por armas de fogo")
    ax3.set_xlabel("Ano")
    ax3.set_ylabel("Total de homicídios")
    plt.xticks(rotation=45)
    st.pyplot(fig3)
    
else:
    st.warning("📌 Por favor, envie um arquivo CSV com os dados para iniciar a análise.")

# Assinatura no final
st.markdown("---")
st.markdown("📊 **by Victor Resende**")
