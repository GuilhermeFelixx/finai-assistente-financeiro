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
    secondary_bg = "#1E222A"
    text_color = "white"
    accent = "#00FFA3"
else:
    background = "#FFFFFF"
    secondary_bg = "#F3F4F6"
    text_color = "#111111"
    accent = "#2563EB"

st.markdown(f"""
<style>
.stApp {{
    background-color: {background};
    color: {text_color};
}}
h1, h2, h3 {{
    color: {accent};
}}
label {{
    color: {text_color} !important;
}}
.stButton>button {{
    background-color: {accent};
    color: {"black" if dark_mode else "white"};
    font-weight: bold;
    border-radius: 8px;
}}
.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    background-color: {secondary_bg};
    color: {text_color};
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
# ABAS DE SIMULADORES
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Juros Compostos",
    "₿ DCA Bitcoin",
    "🏦 CDI",
    "🏢 FIIs",
    "🤖 Chat IA"
])

# =================================================
# 📈 JUROS COMPOSTOS
# =================================================
with tab1:
    st.subheader("Simulador de Juros Compostos")

    valor = st.number_input("Valor inicial (R$)", min_value=0.0, key="jc1")
    taxa = st.number_input("Taxa mensal (%)", min_value=0.0, key="jc2")
    tempo = st.number_input("Tempo (meses)", min_value=0, key="jc3")

    if st.button("Calcular", key="jc_btn"):
        meses = np.arange(tempo + 1)
        valores = valor * (1 + (taxa / 100)) ** meses
        resultado = valores[-1]

        st.metric("Valor Final", f"R$ {resultado:,.2f}")

        fig, ax = plt.subplots()
        ax.plot(meses, valores, linewidth=3)
        ax.set_facecolor(secondary_bg)
        fig.patch.set_facecolor(background)
        ax.tick_params(colors=text_color)
        st.pyplot(fig)

# =================================================
# ₿ DCA BITCOIN
# =================================================
with tab2:
    st.subheader("Simulador DCA Bitcoin")

    aporte = st.number_input("Aporte mensal (R$)", min_value=0.0)
    meses = st.number_input("Quantidade de meses", min_value=0)
    retorno_medio = st.number_input("Retorno médio mensal estimado (%)", value=5.0)

    if st.button("Simular DCA"):
        valores = []
        total = 0

        for i in range(int(meses)):
            total = (total + aporte) * (1 + retorno_medio/100)
            valores.append(total)

        if valores:
            st.metric("Valor acumulado estimado", f"R$ {valores[-1]:,.2f}")

            fig, ax = plt.subplots()
            ax.plot(valores, linewidth=3)
            ax.set_facecolor(secondary_bg)
            fig.patch.set_facecolor(background)
            ax.tick_params(colors=text_color)
            st.pyplot(fig)

# =================================================
# 🏦 CDI
# =================================================
with tab3:
    st.subheader("Simulador 100% CDI")

    valor_cdi = st.number_input("Valor investido (R$)", min_value=0.0)
    selic = st.number_input("Taxa anual CDI (%)", value=10.0)
    meses_cdi = st.number_input("Tempo (meses)", min_value=0)

    if st.button("Simular CDI"):
        taxa_mensal = (selic / 100) / 12
        meses = np.arange(meses_cdi + 1)
        valores = valor_cdi * (1 + taxa_mensal) ** meses

        if len(valores) > 0:
            st.metric("Valor Final", f"R$ {valores[-1]:,.2f}")

            fig, ax = plt.subplots()
            ax.plot(meses, valores, linewidth=3)
            ax.set_facecolor(secondary_bg)
            fig.patch.set_facecolor(background)
            ax.tick_params(colors=text_color)
            st.pyplot(fig)

# =================================================
# 🏢 FIIs
# =================================================
with tab4:
    st.subheader("Simulador FIIs (Dividendos Mensais)")

    valor_fii = st.number_input("Valor investido (R$)", min_value=0.0)
    dividend_yield = st.number_input("Dividend Yield anual (%)", value=8.0)
    meses_fii = st.number_input("Tempo (meses)", min_value=0)
    reinvestir = st.toggle("Reinvestir dividendos?")

    if st.button("Simular FIIs"):
        taxa_mensal = (dividend_yield / 100) / 12
        valores = []
        total = valor_fii

        for i in range(int(meses_fii)):
            dividendo = total * taxa_mensal
            if reinvestir:
                total += dividendo
            valores.append(total)

        if valores:
            st.metric("Patrimônio Final", f"R$ {valores[-1]:,.2f}")

            fig, ax = plt.subplots()
            ax.plot(valores, linewidth=3)
            ax.set_facecolor(secondary_bg)
            fig.patch.set_facecolor(background)
            ax.tick_params(colors=text_color)
            st.pyplot(fig)

# =================================================
# 🤖 CHAT IA
# =================================================
with tab5:
    st.subheader("Assistente Financeiro com IA")

    pergunta = st.text_area("Digite sua pergunta:")

    if st.button("Enviar Pergunta") and pergunta:

        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except KeyError:
            st.error("API Key não encontrada.")
            st.stop()

        with st.spinner("Gerando resposta..."):

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": f"Você é educador financeiro no Brasil. Perfil do usuário: {perfil}. Nunca dê recomendação direta."},
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
                st.success("Resposta:")
                st.write(resposta)

                c.execute("INSERT INTO conversas VALUES (?, ?)", (pergunta, resposta))
                conn.commit()
            else:
                st.error("Erro na API")
                st.write(res_json)

st.caption("© 2026 FinAI — Projeto educacional.")
