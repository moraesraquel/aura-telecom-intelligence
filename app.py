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

st.set_page_config(page_title="AURA // Telecom Intelligence & BI", page_icon="🌸", layout="wide")
st.markdown("""
<style>
    .stApp { background: #FFFFFF; color: #FF0000; font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"] { color: #FF0000; }
    [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { background-color: #FFFFFF; }
    .sci-card { background: #FFFFFF; border: 1px solid #FF0000; border-radius: 16px; padding: 20px; backdrop-filter: blur(12px); margin-bottom: 20px; }
    .stButton>button, .stDownloadButton>button { background: #FF0000; color: #FFFFFF; font-weight: 700; border-radius: 8px; width: 100%; border: none; padding: 0.75rem; }
    .stButton>button:hover, .stDownloadButton>button:hover, .stButton>button:focus, .stDownloadButton>button:focus { background: #FF0000; color: #FFFFFF; }
    .stButton>button p, .stDownloadButton>button p { color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.markdown('<h1 style="color: #FF0000; font-family: Orbitron;">AURA TELECOM INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #FF0000;'>Plataforma analítica com Machine Learning (Random Forest) e Propostas em PDF.</p>", unsafe_allow_html=True)
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
    if st.button("⚡ PROCESSAR ANÁLISE COM MACHINE LEARNING"):
        resultado = recomendar_planos(df_catalogo, dados_gb, minutos, streaming, mobilidade, meses)
        campeao = resultado.iloc[0]
        churn_score = prever_churn_cliente(dados_gb, meses, fatura, reclamacoes)

        st.markdown("### 🏆 PÓDIO OTIMIZADO")
        cols = st.columns(len(resultado))
        for idx, (_, p) in enumerate(resultado.iterrows()):
            with cols[idx]:
                st.markdown(f'<div class="sci-card"><h4>{p["nome"]}</h4><h3>R$ {p["preco_mensal_brl"]:.2f}</h3><p>Franquia: {p["franquia_gb"]} GB</p></div>', unsafe_allow_html=True)

        st.markdown(f"### 🤖 CHURN SCORE (Random Forest): {churn_score*100:.1f}%")

        economia = fatura - campeao['preco_mensal_brl']
        caminho_pdf = f"proposta_{nome.replace(' ', '_').lower()}.pdf"
        gerar_pdf_proposta(caminho_pdf, {'nome': nome, 'meses': meses, 'consumo_gb': dados_gb, 'fatura_atual': fatura, 'churn_score': churn_score}, campeao.to_dict(), economia)

        with open(caminho_pdf, "rb") as f:
            st.download_button("📥 BAIXAR PROPOSTA EM PDF", data=f.read(), file_name=caminho_pdf, mime="application/pdf")
elif menu == "Dashboard & Upsell Regional":
    st.markdown("## 📈 DASHBOARD EXECUTIVO & UPSELL REGIONAL (H3)")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#FFFFFF')
        ax.barh(['Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste'], [85, 45, 92, 60], color='#FF0000')
        ax.tick_params(colors='#FF0000')
        st.pyplot(fig)
    with col2:
        st.dataframe(df_catalogo, use_container_width=True)
elif menu == "Histórico":
    st.markdown("## 📂 LOG DE AUDITORIA")
    st.info("Nenhum atendimento processado nesta sessão.")
