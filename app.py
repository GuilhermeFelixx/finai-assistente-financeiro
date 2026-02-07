import streamlit as st
import requests
import sqlite3
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
st.set_page_config(page_title="FinAI", layout="centered")

st.title("💰 FinAI — Assistente Financeiro Inteligente")
st.caption("Projeto educacional com IA generativa")

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

# ---------- PERFIL ----------
st.subheader("👤 Perfil do Usuário")

perfil = st.selectbox(
    "Qual seu perfil financeiro?",
    ["Conservador", "Moderado", "Arrojado"]
)

# ---------- SIMULADOR ----------
st.subheader("📈 Simulador de Juros Compostos")

valor = st.number_input("Valor inicial (R$)", min_value=0.0)
taxa = st.number_input("Taxa mensal (%)", min_value=0.0)
tempo = st.number_input("Tempo (meses)", min_value=0)

if st.button("Calcular"):
    resultado = valor * (1 + (taxa/100)) ** tempo
    st.success(f"Valor final: R$ {resultado:,.2f}")

    # gráfico simples
    valores = []
    for i in range(tempo + 1):
        valores.append(valor * (1 + (taxa/100)) ** i)

    plt.plot(valores)
    plt.xlabel("Meses")
    plt.ylabel("Valor acumulado")
    st.pyplot(plt)

st.divider()

# ---------- CHAT IA ----------
st.subheader("🤖 Pergunte sobre Finanças")

pergunta = st.text_input("Digite sua pergunta:")

if st.button("Enviar") and pergunta:

    headers = {
    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    "Content-Type": "application/json"
}


    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": f"""
                Você é um assistente financeiro educativo.
                O usuário tem perfil {perfil}.
                Nunca dê recomendação direta de investimento.
                Explique de forma clara e didática.
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

    resposta = response.json()["choices"][0]["message"]["content"]

    st.write(resposta)

    # salvar no banco
    c.execute("INSERT INTO conversas VALUES (?, ?)", (pergunta, resposta))
    conn.commit()

st.caption("⚠️ Este projeto é apenas educacional e não constitui recomendação financeira.")
