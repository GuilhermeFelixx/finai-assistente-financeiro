import streamlit as st
import requests
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="FinAI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")
    dark_mode = st.toggle("🌙 Ativar Dark Mode")
    perfil = st.selectbox(
        "Seu perfil financeiro:",
        ["Conservador", "Moderado", "Arrojado"]
    )
    st.divider()
    st.caption("Projeto educacional com IA generativa.")

# -------------------------------------------------
# TEMA
# -------------------------------------------------
if dark_mode:
    background = "#0E1117"
    text_color = "white"
else:
    background = "#FFFFFF"
    text_color = "#111111"

# -------------------------------------------------
# CSS GLOBAL
# -------------------------------------------------
st.markdown(f"""
<style>
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
[data-testid="stToolbar"] {{display: none !important;}}
.stDeployButton {{display: none;}}

html, body, .stApp {{
    background-color: {background};
    color: {text_color};
}}

label, .stMarkdown, .stText {{
    color: {text_color} !important;
}}

button[data-baseweb="tab"] {{
    color: {"white" if dark_mode else "black"} !important;
}}

/* Força texto preto no botão Enviar Pergunta */
div[data-testid="stButton"] > button {{
    color: black !important;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("💰 FinAI — Assistente Financeiro Inteligente")
st.caption("Simuladores financeiros + IA educacional")

# -------------------------------------------------
# BANCO
# -------------------------------------------------
conn = sqlite3.connect("historico.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS conversas (
    pergunta TEXT,
    resposta TEXT
)
""")
conn.commit()

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Juros Compostos",
    "₿ DCA Bitcoin",
    "🏦 CDI",
    "🏢 FIIs",
    "📊 Comparativo",
    "🤖 Chat IA"
])

# =================================================
# 📈 JUROS COMPOSTOS
# =================================================
with tab1:
    valor = st.number_input("Valor inicial (R$)", min_value=0.0, key="jc1")
    taxa = st.number_input("Taxa mensal (%)", min_value=0.0, key="jc2")
    tempo = st.number_input("Tempo (meses)", min_value=0, key="jc3")

    if st.button("Calcular", key="jc_btn"):
        meses = np.arange(tempo + 1)
        valores_jc = valor * (1 + (taxa / 100)) ** meses
        st.metric("Valor Final", f"R$ {valores_jc[-1]:,.2f}")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.plot(meses, valores_jc)
            ax.tick_params(labelsize=8)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

# =================================================
# ₿ DCA
# =================================================
with tab2:
    aporte = st.number_input("Aporte mensal (R$)", min_value=0.0, key="dca1")
    meses_dca = st.number_input("Meses", min_value=0, key="dca2")
    retorno = st.number_input("Retorno médio mensal (%)", value=5.0, key="dca3")

    if st.button("Simular DCA", key="dca_btn"):
        total = 0
        valores_dca = []
        for i in range(int(meses_dca)):
            total = (total + aporte) * (1 + retorno/100)
            valores_dca.append(total)

        if valores_dca:
            st.metric("Valor Final", f"R$ {valores_dca[-1]:,.2f}")

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                fig, ax = plt.subplots(figsize=(4,2))
                ax.plot(valores_dca)
                ax.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

# =================================================
# 🏦 CDI
# =================================================
with tab3:
    valor_cdi = st.number_input("Valor investido (R$)", min_value=0.0, key="cdi1")
    taxa_cdi = st.number_input("CDI anual (%)", value=10.0, key="cdi2")
    meses_cdi = st.number_input("Meses", min_value=0, key="cdi3")

    if st.button("Simular CDI", key="cdi_btn"):
        taxa_mensal = (taxa_cdi/100)/12
        meses = np.arange(meses_cdi + 1)
        valores_cdi = valor_cdi * (1 + taxa_mensal) ** meses

        st.metric("Valor Final", f"R$ {valores_cdi[-1]:,.2f}")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.plot(meses, valores_cdi)
            ax.tick_params(labelsize=8)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

# =================================================
# 🏢 FIIs
# =================================================
with tab4:
    valor_fii = st.number_input("Valor investido (R$)", min_value=0.0, key="fii1")
    dy = st.number_input("Dividend Yield anual (%)", value=8.0, key="fii2")
    meses_fii = st.number_input("Meses", min_value=0, key="fii3")
    reinvestir = st.toggle("Reinvestir dividendos?", key="fii4")

    if st.button("Simular FIIs", key="fii_btn"):
        taxa_mensal = (dy/100)/12
        total = valor_fii
        valores_fii = []

        for i in range(int(meses_fii)):
            dividendo = total * taxa_mensal
            if reinvestir:
                total += dividendo
            valores_fii.append(total)

        if valores_fii:
            st.metric("Patrimônio Final", f"R$ {valores_fii[-1]:,.2f}")

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                fig, ax = plt.subplots(figsize=(4,2))
                ax.plot(valores_fii)
                ax.tick_params(labelsize=8)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

# =================================================
# 📊 COMPARATIVO
# =================================================
with tab5:
    aporte_comp = st.number_input("Valor inicial (R$)", min_value=0.0, key="comp1")
    meses_comp = st.number_input("Meses", min_value=0, key="comp2")
    taxa_comp = st.number_input("Taxa mensal estimada (%)", value=1.0, key="comp3")

    if st.button("Comparar", key="comp_btn"):
        meses = np.arange(meses_comp + 1)

        juros = aporte_comp * (1 + taxa_comp/100) ** meses
        cdi = aporte_comp * (1 + ((taxa_comp*12)/100)/12) ** meses
        fii = aporte_comp * (1 + ((taxa_comp*8)/100)/12) ** meses

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.plot(meses, juros, label="Juros Compostos")
            ax.plot(meses, cdi, label="CDI")
            ax.plot(meses, fii, label="FIIs")
            ax.legend(fontsize=6)
            ax.tick_params(labelsize=8)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

# =================================================
# 🤖 CHAT IA
# =================================================
with tab6:
    pergunta = st.text_area("Digite sua pergunta:")

    if st.button("Enviar Pergunta", key="chat_btn") and pergunta:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except:
            st.error("API Key não encontrada.")
            st.stop()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": f"Você é educador financeiro no Brasil. Perfil: {perfil}. Nunca dê recomendação direta."},
                {"role": "user", "content": pergunta}
            ]
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )

        res_json = response.json()

        if "choices" in res_json:
            resposta = res_json["choices"][0]["message"]["content"]
            st.write(resposta)

            c.execute("INSERT INTO conversas VALUES (?, ?)", (pergunta, resposta))
            conn.commit()
        else:
            st.error("Erro na API")

st.caption("© 2026 FinAI — Projeto educacional.")
