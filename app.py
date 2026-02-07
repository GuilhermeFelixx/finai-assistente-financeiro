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

    valores = []
    for i in range(tempo + 1):
        valores.append(valor * (1 + (taxa/100)) ** i)

    plt.figure()
    plt.plot(valores)
    plt.xlabel("Meses")
    plt.ylabel("Valor acumulado")
    st.pyplot(plt)

st.divider()

# ---------- CHAT IA ----------
st.subheader("🤖 Pergunte sobre Finanças")

pergunta = st.text_input("Digite sua pergunta:")

if st.button("Enviar") and pergunta:

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        st.error("API Key não encontrada nos Secrets.")
        st.stop()

    with st.spinner("Pensando... 🤖"):

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
Você é um assistente financeiro educacional especializado na realidade do brasileiro médio.

OBJETIVO:
Educar, orientar e explicar conceitos financeiros de forma clara, prática e aplicável ao Brasil.

O usuário possui perfil {perfil}.

REGRAS IMPORTANTES:
- Nunca dê recomendação direta de investimento.
- Nunca diga "compre X" ou "invista em Y".
- Sempre explique riscos.
- Sempre incentive diversificação.
- Sempre adapte a linguagem ao brasileiro comum.
- Use exemplos práticos com valores em reais (R$).
- Considere inflação brasileira e taxa Selic quando relevante.

RENDA FIXA:
Explique CDI, Tesouro Selic, CDB, LCI/LCA, relação com inflação.

RENDA VARIÁVEL:
Explique volatilidade, ciclos de mercado, horizonte de tempo.

CRIPTO E WEB3:
Explique:
- Volatilidade extrema
- Ciclos de bull e bear market
- Risco regulatório
- Risco de custódia
- Diferença entre especulação e investimento
- DeFi
- Staking
- Liquidez
- Perda impermanente
- Risco de contrato inteligente

ESTRUTURA DA RESPOSTA:
1) Explicação simples
2) Exemplo prático em reais
3) Riscos envolvidos
4) Como alguém do perfil {perfil} deveria pensar
5) Conclusão educativa

Se detectar FOMO, impulsividade ou ganância, explique psicologia financeira.

Finalize sempre com:
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
            st.write(resposta)

            # Salvar apenas se resposta válida
            c.execute("INSERT INTO conversas VALUES (?, ?)", (pergunta, resposta))
            conn.commit()
        else:
            st.error("Erro ao comunicar com a API.")
            st.write(res_json)

st.caption("⚠️ Este projeto é apenas educacional e não constitui recomendação financeira.")
