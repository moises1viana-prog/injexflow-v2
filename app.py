import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="InjexFlow Pro", layout="wide")

# Estilo para os alertas
st.markdown("""
    <style>
    .alerta-erro { padding: 20px; background-color: #ff4b4b; color: white; border-radius: 10px; margin-bottom: 10px; }
    .alerta-aviso { padding: 20px; background-color: #ffa500; color: white; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 InjexFlow 4.0 | Inteligência de Produção")

if os.path.exists("producao.csv"):
    df = pd.read_csv("producao.csv", names=['Data', 'Injetora', 'Boas', 'Refugo', 'Defeito', 'Selo'])
    
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros de Gestão")
    maquina_sel = st.sidebar.multiselect("Selecionar Injetoras:", options=df['Injetora'].unique(), default=df['Injetora'].unique())
    
    # Filtrando os dados
    df_filtrado = df[df['Injetora'].isin(maquina_sel)]

    # --- ALERTAS INTELIGENTES ---
    total_boas = df_filtrado['Boas'].sum()
    total_refugo = df_filtrado['Refugo'].sum()
    total_geral = total_boas + total_refugo
    eficiencia = (total_boas / total_geral * 100) if total_geral > 0 else 0
    meta = 85.0

    if eficiencia < meta:
        st.markdown(f'<div class="alerta-erro">⚠️ ALERTA DE PRODUTIVIDADE: Eficiência ({eficiencia:.1f}%) abaixo da meta de {meta}%!</div>', unsafe_allow_html=True)
    
    indice_refugo = (total_refugo / total_geral * 100) if total_geral > 0 else 0
    if indice_refugo > 5:
        st.markdown(f'<div class="alerta-aviso">🚨 ALERTA DE QUALIDADE: Índice de refugo alto ({indice_refugo:.1f}%). Verifique os moldes!</div>', unsafe_allow_html=True)

    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Peças Boas", f"{int(total_boas)} UN")
    c2.metric("Refugo Total", f"{int(total_refugo)} UN")
    c3.metric("Eficiência OEE", f"{eficiencia:.1f}%", delta=f"{eficiencia - meta:.1f}% contra Meta")
    c4.metric("Máquinas Ativas", len(maquina_sel))

    # --- GRÁFICOS ---
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        fig_barra = px.bar(df_filtrado, x='Data', y=['Boas', 'Refugo'], 
                           title="Histórico de Produção por Ciclo",
                           color_discrete_map={'Boas': '#2ecc71', 'Refugo': '#e74c3c'})
        st.plotly_chart(fig_barra, use_container_width=True)
        
    with col_dir:
        # Gráfico de pizza apenas se houver refugo
        if total_refugo > 0:
            fig_pizza = px.pie(df_filtrado[df_filtrado['Refugo'] > 0], names='Defeito', values='Refugo', 
                               title="Análise de Defeitos (Pareto)")
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.success("Zero Refugo detectado no filtro atual! 🏆")

    # --- TABELA DE AUDITORIA ---
    with st.expander("Ver Log de Produção Detalhado"):
        st.dataframe(df_filtrado.sort_values(by='Data', ascending=False), use_container_width=True)

else:
    st.error("Aguardando base de dados `producao.csv`...")if st.sidebar.button("💾 Realizar Backup de Segurança"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"backup_seguranca_{ts}.csv", index=False)
    st.sidebar.success(f"Backup criado: backup_seguranca_{ts}.csv")