import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.figure_factory as ff

# ⬅️ ADICIONADO para exportar imagens
import os
import plotly.io as pio

# Garantir que a pasta 'imagens' exista
os.makedirs("imagens", exist_ok=True)

# Carregando os dados
df_2ano = pd.read_excel("2_ano_epv.xlsx")
df_5ano = pd.read_excel("5_ano_epv.xlsx")

# Limpando nomes de colunas
df_2ano.columns = df_2ano.columns.str.strip()
df_5ano.columns = df_5ano.columns.str.strip()

# Função para calcular crescimento
def calcular_crescimento(df, nome_ano):
    df_crescimento = df[["ESCOLA", "DIAGNÓSTICA - MAT", "FORMATIVA I - MAT"]].copy()
    df_crescimento["CRESCIMENTO_%"] = ((df_crescimento["FORMATIVA I - MAT"] - df_crescimento["DIAGNÓSTICA - MAT"]) /
                                       df_crescimento["DIAGNÓSTICA - MAT"]) * 100
    df_crescimento["CRESCIMENTO_%"] = df_crescimento["CRESCIMENTO_%"].round(2)
    df_crescimento["ANO"] = nome_ano
    return df_crescimento

# Processando os dados
crescimento_2ano = calcular_crescimento(df_2ano, "2º ANO")
crescimento_5ano = calcular_crescimento(df_5ano, "5º ANO")
crescimento_total = pd.concat([crescimento_2ano, crescimento_5ano], ignore_index=True)

# --- INTERFACE STREAMLIT ---
st.title("📈 Crescimento no Desempenho Escolar - MAT")

# Filtro de ano
ano_escolhido = st.selectbox("Selecione o Ano:", ["2º ANO", "5º ANO", "Todos"])

# Filtrando os dados
if ano_escolhido != "Todos":
    dados = crescimento_total[crescimento_total["ANO"] == ano_escolhido]
else:
    dados = crescimento_total.copy()

# Tabela completa
st.subheader("📋 Tabela de Crescimento por Escola")
st.dataframe(dados.sort_values(by="CRESCIMENTO_%", ascending=False), use_container_width=True)

# Top 5 crescimento
top5 = dados.sort_values(by="CRESCIMENTO_%", ascending=False).head(5)
fig_top5 = px.bar(top5, x="ESCOLA", y="CRESCIMENTO_%", title="🏆 Top 5 Escolas com Maior Crescimento",
                  text="CRESCIMENTO_%", color="CRESCIMENTO_%", color_continuous_scale="Greens")
st.plotly_chart(fig_top5, use_container_width=True)

# ⬅️ EXPORTANDO gráfico como imagem
fig_top5.write_image("imagens/top5_crescimento.png")

# Bottom 5 crescimento
bottom5 = dados.sort_values(by="CRESCIMENTO_%", ascending=True).head(5)
fig_bottom5 = px.bar(bottom5, x="ESCOLA", y="CRESCIMENTO_%", title="🚨 Escolas que Precisam de Atenção",
                     text="CRESCIMENTO_%", color="CRESCIMENTO_%", color_continuous_scale="Reds")
st.plotly_chart(fig_bottom5, use_container_width=True)

# ⬅️ EXPORTANDO gráfico como imagem
fig_bottom5.write_image("imagens/bottom5_crescimento.png")

# Filtro por escola
escolas_disponiveis = dados["ESCOLA"].unique()
escolas_selecionadas = st.multiselect("Filtrar por Escola:", escolas_disponiveis)

if escolas_selecionadas:
    dados = dados[dados["ESCOLA"].isin(escolas_selecionadas)]

media_crescimento = dados["CRESCIMENTO_%"].mean().round(2)
st.metric(label="📌 Crescimento Médio (%)", value=f"{media_crescimento}%")

def gerar_heatmap(df, ano):
    df_heat = df[["ESCOLA", "DIAGNÓSTICA - MAT", "FORMATIVA I - MAT"]].set_index("ESCOLA")
    fig = ff.create_annotated_heatmap(
        z=df_heat.values,
        x=["Diagnóstica", "Formativa I"],
        y=df_heat.index.tolist(),
        colorscale="Viridis",
        showscale=True
    )
    fig.update_layout(title_text=f"🔥 Mapa de Calor - {ano}º Ano", height=600)
    st.plotly_chart(fig, use_container_width=True)

    # ⬅️ EXPORTANDO gráfico como imagem
    fig.write_image(f"imagens/heatmap_{ano}ano.png")

if ano_escolhido == "2º ANO" or ano_escolhido == "Todos":
    gerar_heatmap(df_2ano, 2)

if ano_escolhido == "5º ANO" or ano_escolhido == "Todos":
    gerar_heatmap(df_5ano, 5)

import io

# Salvar os dados em um buffer de memória
excel_buffer = io.BytesIO()
dados.to_excel(excel_buffer, index=False, engine='openpyxl')
excel_buffer.seek(0)

# Botão para download dos dados
st.download_button(
    label="📥 Baixar Dados em Excel",
    data=excel_buffer,
    file_name='crescimento_escolar.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# python -m streamlit run app.py
# ou,
# streamlit run app.py