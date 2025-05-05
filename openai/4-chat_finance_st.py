import yfinance as yf
import json
import openai
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.Client()
openai.api_key = os.getenv("OPENAI_API_KEY")

def retorna_cotacao(ticker, period="1mo"):
    ticker_obj = yf.Ticker(f"{ticker}.SA")
    hist = ticker_obj.history(period=period)["Close"]
    hist.index = hist.index.map(lambda x: x.strftime("%Y-%m-%d"))
    hist = round(hist, 2)
    # limitar em 30 resultados
    if len(hist) > 30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]
    return hist.to_json()

tools = [
    {
        "type": "function",
        "function": {
            "name": "retorna_cotacao",
            "description": "Retorna a cotação de de ações da Ibovespa",
            "parameters":{
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "O ticker da ação. Ex: BBAS3, BBDC4, etc."
                    },
                    "period": {
                        "type": "string",
                        "description": "O período retornado dos dados históricos da cotação \
                            sendo '1mo' equivale a um mês, '1d' equivale a 1 dia \
                                 e '1y' equivale a um ano e 'ytd' equivale a todos os tempos.",
                        "enum": [ "1d", "5d", "1mo", "6mo", "1y", "5y", "10y", "ytd", "max"]
                    }
                },
                "required": ["ticker"]
            }
        }
    }
]

funcao_disponivel = {"retorna_cotacao": retorna_cotacao}

def gera_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        tools= tools,
        tool_choice="auto"
    )

    tools_calls = resposta.choices[0].message.tool_calls

    if tools_calls:
        mensagens.append(resposta.choices[0].message)
        for tool_call in tools_calls:
            function_name = tool_call.function.name
            function_to_call = funcao_disponivel[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_return = function_to_call(**function_args)

            mensagens.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_return
            })

            segunda_resposta = client.chat.completions.create(
                messages=mensagens,
                model="gpt-3.5-turbo-0125",
            )

            mensagens.append(segunda_resposta.choices[0].message)
            
        return mensagens

st.set_page_config(page_title="Chat Financeiro", page_icon="📈")

st.title("Chatbots Cotação de ações📈")

if "mensagem" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "system", "content": "Você é um assistente financeiro."}
    ]

# Historico de mensagens
for msg in st.session_state.mensagens:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg.content)
    if msg["role"] == "assistant":
        st.chat_message("assistant").markdown(msg.content)

# Entrada de mensagem do usuário
user_input = st.chat_input("Digite sua pergunta sobre cotação de ações:")
if user_input:
    # Adicionar mensagem ao histórico
    st.session_state.mensagens.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # Processa a mensagem
    print(st.session_state.mensagens)
    st.session_state.mensagens = gera_texto(st.session_state.mensagens)

    # Exibir a resposta do chatbot
    ultima_msg = st.session_state.mensagens[-1]
    if ultima_msg.role == "assistant":
        st.chat_message("assistant").markdown(ultima_msg.content)
    elif ultima_msg.role == "tool":
        st.chat_message("tool").markdown(ultima_msg["content"])