"""
=============================================================================
ARQUIVO: app.py
O QUE FAZ: Interface principal em Streamlit, Dashboard BI, ML e gerador de PDF.
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from src.recommender import recomendar_planos
from src.db import carregar_catalogo_do_supabase
from src.predictor import prever_churn_cliente
from src.pdf_generator import gerar_pdf_proposta

st.set_page_config(page_title="AURA // Telecom Intelligence", page_icon="🌸", layout="wide")

# Customização CSS: Fundo branco, letras vermelhas e botões vermelhos com texto branco
st.markdown("""
<style>
    /* Fundo da aplicação e cor padrão dos textos */
    .stApp { 
        background-color: #FFFFFF !important; 
        color: #DA291C !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Remoção de gradiente e padronização da cor das fontes em vermelho */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown, div[data-testid="stMarkdownContainer"] {
        color: #DA291C !important;
        background: none !important;
        -webkit-text-fill-color: #DA291C !important;
    }
    
    /* Cartões dos planos em fundo claro com borda vermelha */
    .sci-card { 
        background-color: #FAFAFA; 
        border: 1px solid #DA291C; 
        border-radius: 16px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 8px rgba(218, 41, 28, 0.08);
    }
    .sci-card h3, .sci-card h4, .sci-card p {
        color: #DA291C !important;
    }
    
    /* Botão vermelho (#DA291C) com texto branco (#FFFFFF) */
    .stButton>button { 
        background-color: #DA291C !important; 
        background-image: none !important;
        border-radius: 8px; 
        width: 100%; 
        border: none; 
        padding: 0.75rem; 
    }
    
    /* Forçar texto do botão em branco */
    .stButton>button, .stButton>button *, .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Botão de download estilizado no mesmo padrão */
    .stDownloadButton>button {
        background-color: #DA291C !important;
        background-image: none !important;
        border-radius: 8px;
        border: none;
        padding: 0.75rem;
    }
    .stDownloadButton>button, .stDownloadButton>button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Ajuste de fundo da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

if 'historico' not in st.session_state:
    st.session_state.historico = []

st.markdown('<h1 style="color: #DA291C; font-family: Orbitron;">AURA TELECOM INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #DA291C;'>Plataforma analítica com Machine Learning (Random Forest) e Propostas em PDF.</p>", unsafe_allow_html=True)
st.markdown("---")

df_catalogo = carregar_catalogo_do_supabase()

st.sidebar.markdown("### NAVEGAÇÃO")
menu = st.sidebar.radio("Módulo:", ["Recomendador, Churn (ML) & PDF", "Dashboard & Upsell Regional", "Histórico"])

if menu == "Recomendador, Churn (ML) & PDF":
    st.sidebar.markdown("### PARÂMETROS")
    nome = st.sidebar.text_input("Cliente", "Felipe Ribeiro (Feris)")
    dados_gb = st.sidebar.slider("Dados (GB/mês)", 1.0, 100.0, 25.0)
    minutos = st.sidebar.slider("Voz / Minutos", 50, 1500, 500)
    streaming = st.sidebar.slider("Streaming (h/mês)", 0.0, 50.0, 10.0)
    mobilidade = st.sidebar.selectbox("Mobilidade", [0, 1, 2, 3], format_func=lambda x: ["Local", "Regional", "Nacional", "Global"][x])
    meses = st.sidebar.number_input("Tempo de Relacionamento (Meses)", 1, 240, 24)
    fatura = st.sidebar.number_input("Fatura Atual (R$)", 0.0, 999.0, 119.90)
    reclamacoes = st.sidebar.slider("Reclamações", 0, 5, 1)

    if st.button("PROCESSAR ANÁLISE COM MACHINE LEARNING"):
        resultado = recomendar_planos(df_catalogo, dados_gb, minutos, streaming, mobilidade, meses)
        campeao = resultado.iloc[0]
        churn_score = prever_churn_cliente(dados_gb, meses, fatura, reclamacoes)
        
        st.markdown("### PÓDIO OTIMIZADO")
        cols = st.columns(len(resultado))
        for idx, (_, p) in enumerate(resultado.iterrows()):
            with cols[idx]:
                st.markdown(f'<div class="sci-card"><h4>{p["nome"]}</h4><h3>R$ {p["preco_mensal_brl"]:.2f}</h3><p>Franquia: {p["franquia_gb"]} GB</p></div>', unsafe_allow_html=True)
                
        st.markdown(f"### CHURN SCORE (Random Forest): {churn_score*100:.1f}%")
        
        economia = fatura - campeao['preco_mensal_brl']
        caminho_pdf = f"proposta_{nome.replace(' ', '_').lower()}.pdf"
        gerar_pdf_proposta(caminho_pdf, {'nome': nome, 'meses': meses, 'consumo_gb': dados_gb, 'fatura_atual': fatura, 'churn_score': churn_score}, campeao.to_dict(), economia)
        
        with open(caminho_pdf, "rb") as f:
            st.download_button("BAIXAR PROPOSTA EM PDF", data=f.read(), file_name=caminho_pdf, mime="application/pdf")

elif menu == "Dashboard & Upsell Regional":
    st.markdown("## DASHBOARD EXECUTIVO & UPSELL REGIONAL (H3)")
    col1, col2 = st.columns(2)
    with col1:
        # Gráfico ajustado para fundo branco com barras em vermelho (#DA291C)
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        ax.barh(['Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste'], [85, 45, 92, 60], color='#DA291C')
        ax.tick_params(colors='#DA291C')
        for spine in ax.spines.values():
            spine.set_color('#DA291C')
        st.pyplot(fig)
    with col2:
        st.dataframe(df_catalogo, use_container_width=True)

elif menu == "📂 Histórico":
    st.markdown("## 📂 LOG DE AUDITORIA")
    st.info("Nenhum atendimento processado nesta sessão.")
