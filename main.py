import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração da Página
st.set_page_config(page_title="InjexFlow 4.0 - Dashboard", layout="wide")

st.title("🏭 InjexFlow 4.0 | Monitoramento em Tempo Real")
st.markdown("---")

# Verificar se o arquivo existe
if os.path.exists("producao.csv"):
    # Carregar Dados
    df = pd.read_csv("producao.csv", names=['Data', 'Injetora', 'Boas', 'Refugo', 'Defeito', 'Selo'])
    
    # Métricas de Topo
    total_boas = df['Boas'].sum()
    total_refugo = df['Refugo'].sum()
    eficiencia = (total_boas / (total_boas + total_refugo) * 100) if (total_boas + total_refugo) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Peças Boas", f"{int(total_boas)} un")
    col2.metric("Refugo Total", f"{int(total_refugo)} un", delta=f"{int(total_refugo)}", delta_color="inverse")
    col3.metric("Eficiência OEE", f"{eficiencia:.1f}%")

    st.markdown("---")

    # Gráficos Interativos
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Produção por Entrada")
        fig_prod = px.bar(df, x=df.index, y=['Boas', 'Refugo'], 
                          title="Evolução da Produção",
                          color_discrete_map={'Boas': '#2ecc71', 'Refugo': '#e74c3c'})
        st.plotly_chart(fig_prod, use_container_width=True)

    with c2:
        st.subheader("🔍 Motivos de Refugo")
        fig_pizza = px.pie(df[df['Refugo'] > 0], names='Defeito', values='Refugo', 
                           title="Distribuição de Defeitos",
                           color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # Tabela de Auditoria (ISO 9001)
    st.subheader("📋 Registro de Auditoria (Imutável)")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ Arquivo 'producao.csv' não encontrado. Registre algo no terminal primeiro!")