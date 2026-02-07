import streamlit as st
import requests
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# ---------- CONFIG ----------
st.set_page_config(
    page_title="FinAI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DARK MODE CUSTOM ----------
st.markdown("""
    <style>
        body {
            background-color: #0E1117;
            color: white;
        }
        .stApp {
            background-color: #0E1117;
        }
        h1, h2, h3, h4 {
            color: #00FFA3;
        }
        .stButton>button {
            background-color: #00FFA3;
            color: black;
            font-weight: bold;
            border-radius: 8px;
        }
        .stTextInput>div>div>input {
            background-color: #1E222A;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("💰 FinAI — Assistente Financeiro Inteligente")
st.caption("Experiência digital de relacionamento financeiro guiada por IA")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Configurações")
    perfil = st.selectbox(
        "Seu perfil financeiro:",
        ["Conservador", "Moderado", "Arrojado"]
    )
    st.divider()
    st.info("Projeto educacional com IA generativa.\n\nNão constitui recomendação de investimento.")

# ---------- BANCO ----------
conn = sqlite3.connect("historico.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS conversas (
    pergunta TEXT,
    resposta TEXT
)
""")
conn.commit()

# ---------- LAYOUT EM COLUNAS ----------
col1, col2 = st.columns([1, 1])

# ===============================
# 📈 COLUNA SIMULADOR
# ===============================
with col1:
    st.subheader("📈 Simulador de Juros Compostos")

    valor = st.number_input("Valor inicial (R$)", min_value=0.0)
    taxa = st.number_input("Taxa mensal (%)", min_value=0.0)
    tempo = st.number_input("Tempo (meses)", min_value=0)

    if st.button("Calcular crescimento"):

        resultado = valor * (1 + (taxa / 100)) ** tempo

        st.metric(
            label="Valor Final Projetado",
            value=f"R$ {resultado:,.2f}"
        )

        # Gráfico Profissional
        meses = np.arange(tempo + 1)
        valores = valor * (1 + (taxa / 100)) ** meses

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(meses, valores, linewidth=3)
        ax.fill_between(meses, valores, alpha=0.2)

        ax.set_facecolor("#1E222A")
        fig.patch.set_facecolor("#0E1117")

        ax.set_title("Evolução do Investimento", color="white")
        ax.set_xlabel("Meses", color="white")
        ax.set_ylabel("Valor acumulado (R$)", color="white")

        ax.tick_params(colors="white")

        st.pyplot(fig)

# ===============================
# 🤖 COLUNA CHAT
# ===============================
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

Explique sempre:
- Conceitos simples
- Exemplos em reais (R$)
- Riscos envolvidos
- Relação com inflação e cenário brasileiro
- Se aplicável, explique também cripto e Web3

Nunca dê recomendação direta.
Nunca diga para comprar algo.
Eduque, não aconselhe.

Inclua sempre:
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

st.divider()

# ---------- HISTÓRICO ----------
with st.expander("📜 Histórico de Perguntas"):
    c.execute("SELECT * FROM conversas ORDER BY ROWID DESC LIMIT 5")
    dados = c.fetchall()

    if dados:
        for p, r in dados:
            st.markdown(f"**Pergunta:** {p}")
            st.markdown(f"**Resposta:** {r}")
            st.divider()
    else:
        st.write("Nenhuma conversa registrada ainda.")

st.caption("© 2026 FinAI — Projeto educacional desenvolvido com IA generativa.")
