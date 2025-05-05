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
    hist.index = hist.index.strftime("%Y-%m-%d")
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
                }
            }
        }
    }
]

funcao_disponivel = {"retorna_cotacao": retorna_cotacao}

def message_to_dict(message):
    # Verifica se já é um dicionário
    if isinstance(message, dict):
        return message
    
    # Caso seja um objeto Message da OpenAI
    try:
        return {
            "role": message.role,
            "content": message.content or ""
        }
    except AttributeError:
        # Caso não seja possível acessar os atributos
        st.error(f"Erro ao converter mensagem: {type(message)}")
        return {"role": "assistant", "content": "Erro ao processar a mensagem."}

def filter_messages_for_api(messages):
    """
    Filtra mensagens para enviar para a API, removendo mensagens de tool
    que podem causar erros se não tiverem contexto apropriado.
    Mantém apenas mensagens do usuário e do assistente para nova conversa.
    """
    filtered_messages = []
    for msg in messages:
        msg_dict = message_to_dict(msg)
        role = msg_dict.get("role")
        # Mantém somente mensagens de usuário e assistente para nova conversa
        if role in ["user", "assistant", "system"]:
            filtered_messages.append(msg_dict)
    return filtered_messages

def gera_texto(mensagens):
    # mensagens_dict = [message_to_dict(msg) for msg in mensagens]
    # Filtra apenas mensagens válidas para enviar para a API
    mensagens_filtradas = filter_messages_for_api(mensagens)


    try:
        resposta = client.chat.completions.create(
            messages=mensagens_filtradas,
            model="gpt-3.5-turbo-0125",
            tools=tools,
            tool_choice="auto" 
        )

        # Lista para construir a nova sequência de mensagens
        novas_mensagens = mensagens_filtradas.copy()
        
        tools_calls = resposta.choices[0].message.tool_calls

        if tools_calls:
            # Converte a mensagem do assistente para dicionário
            assistant_msg = {
                "role": "assistant",
                "content": resposta.choices[0].message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tools_calls
                ]
            }
            novas_mensagens.append(assistant_msg)
            
            for tool_call in tools_calls:
                function_name = tool_call.function.name
                function_to_call = funcao_disponivel[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_return = function_to_call(**function_args)

                novas_mensagens.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_return
                })

            segunda_resposta = client.chat.completions.create(
                messages=novas_mensagens,
                model="gpt-3.5-turbo-0125",
            )

            novas_mensagens.append({
                "role": "assistant",
                "content": segunda_resposta.choices[0].message.content or ""
            })
        else:
            # Se não houver chamadas de ferramenta, apenas adiciona a resposta
            novas_mensagens.append({
                "role": "assistant",
                "content": resposta.choices[0].message.content or ""
            })
            
        return novas_mensagens
        
    except Exception as e:
        st.error(f"Erro na API: {str(e)}")
        # Retorna as mensagens originais sem modificação em caso de erro
        return mensagens

def get_role(message):
    """Extrai o papel (role) da mensagem com segurança"""
    if hasattr(message, 'role'):
        return message.role
    if isinstance(message, dict) and "role" in message:
        return message["role"]
    return None

def get_content(message):
    """Extrai o papel (content) da mensagem com segurança"""
    if hasattr(message, 'content'):
        return message.content
    if isinstance(message, dict) and "content" in message:
        return message["content"]
    return None


st.set_page_config(page_title="Chatbot Financeiro", page_icon="🤖")

st.title("Chatbot de cotações de ações 📈")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Histórico de Mensagens
for msg in st.session_state.mensagens:
    
    if get_role(msg) == "user":
        st.chat_message("user").markdown(get_content(msg))
    elif get_role(msg) == "assistant":
        st.chat_message("assistant").markdown(get_content(msg))

# Entrada de mensagem do usuário
user_input = st.chat_input("Digite sua pergunta sobre cotação de ações:")
if user_input:
    # Adicionar mensagem ao histórico
    st.session_state.mensagens.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # Processa a mensagem 
    st.session_state.mensagens = gera_texto(st.session_state.mensagens)

    # Exibir resposta do chatbot
    ultima_msg = st.session_state.mensagens[-1]
    if ultima_msg["role"] == "assistant":
        st.chat_message("assistant").markdown(ultima_msg["content"])
