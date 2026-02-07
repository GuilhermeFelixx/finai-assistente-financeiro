import streamlit as st
import requests
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------
# CONFIGURAÇÃO BASE
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
# TEMA DINÂMICO
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

        h1, h2, h3, h4 {{
            color: {accent};
        }}

        label, .stMarkdown, .stTextInput label {{
            color: {text_color} !important;
        }}

        .stButton>button {{
            background-color: {accent};
            color: {"black" if dark_mode else "white"};
            font-weight: bold;
            border-radius: 8px;
        }}

        .stTextInput>div>div>input,
        .stTextArea textarea {{
            background-color: {secondary_bg};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("💰 FinAI — Assistente Financeiro Inteligente")
st.caption("Experiência digital de relacionamento financeiro guiada por IA")

# -------------------------------------------------
# BANCO DE DADOS
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
# LAYOUT PRINCIPAL
# -------------------------------------------------
col1, col2 = st.columns([1, 1])

# =================================================
# 📈 SIMULADOR
# =================================================
with col1:
    st.subheader("📈 Simulador de Juros Compostos")

    valor = st.number_input("Valor inicial (R$)", min_value=0.0)
    taxa = st.number_input("Taxa mensal (%)", min_value=0.0)
    tempo = st.number_input("Tempo (meses)", min_value=0)

    if st.button("Calcular crescimento"):

        resultado = valor * (1 + (taxa / 100)) ** tempo

        st.metric("Valor Final Projetado", f"R$ {resultado:,.2f}")

        meses = np.arange(tempo + 1)
        valores = valor * (1 + (taxa / 100)) ** meses

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(meses, valores, linewidth=3)
        ax.fill_between(meses, valores, alpha=0.2)

        ax.set_facecolor(secondary_bg)
        fig.patch.set_facecolor(background)

        ax.set_title("Evolução do Investimento", color=text_color)
        ax.set_xlabel("Meses", color=text_color)
        ax.set_ylabel("Valor acumulado (R$)", color=text_color)

        ax.tick_params(colors=text_color)

        st.pyplot(fig)

# =================================================
# 🤖 CHAT IA
# =================================================
with col2:
    st.subheader("🤖 Assistente Financeiro")

    pergunta = st.text_area("Digite sua pergunta sobre finanças:")

    if st.button("Enviar Pergunta") and pergunta:

        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except KeyError:
            st.error("API Key não encontrada nos Secrets.")
            st.stop()

        with st.spinner("Analisando cenário financeiro..."):

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
Você é um educador financeiro especialista no Brasil.

O usuário possui perfil {perfil}.

Explique:
- Conceitos simples
- Exemplos em reais
- Riscos envolvidos
- Relação com inflação brasileira
- Se aplicável, inclua cripto e Web3

Nunca dê recomendação direta.
Eduque, não aconselhe.

Inclua:
1) Explicação simples
2) Exemplo prático
3) Riscos
4) Como o perfil {perfil} deve pensar
5) Conclusão educativa

Finalize com:
"Isto é conteúdo educativo e não constitui recomendação de investimento."
"""
                    },
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
                st.success("Resposta gerada com IA:")
                st.write(resposta)

                c.execute("INSERT INTO conversas VALUES (?, ?)", (pergunta, resposta))
                conn.commit()
            else:
                st.error("Erro ao comunicar com a API.")
                st.write(res_json)

# -------------------------------------------------
# HISTÓRICO
# -------------------------------------------------
st.divider()

with st.expander("📜 Histórico recente"):
    c.execute("SELECT * FROM conversas ORDER BY ROWID DESC LIMIT 5")
    dados = c.fetchall()

    if dados:
        for p, r in dados:
            st.markdown(f"**Pergunta:** {p}")
            st.markdown(f"**Resposta:** {r}")
            st.divider()
    else:
        st.write("Nenhuma conversa registrada ainda.")

st.caption("© 2026 FinAI — Projeto educacional com IA generativa.")
