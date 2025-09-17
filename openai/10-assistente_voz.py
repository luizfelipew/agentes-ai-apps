import openai
import speech_recognition as sr
from playsound import playsound
from pathlib import Path
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.Client()
openai.api_key = os.getenv("OPENAI_API_KEY")

arquivo_audio = "hello.mp3"

recognizer = sr.Recognizer()

def grava_audio():
    """Captura áudio do microfone e retorna o áudio gravado."""
    with sr.Microphone() as source:
        print("Ouvindo...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    return audio

def transcricao_audio(audio):
    """Transcreve o áudio utilizando o modelo Whisper."""
    try:
        wave_data = BytesIO(audio.get_wav_data())
        wave_data.name = "audio.wav"
        transcricao = client.audio.transcriptions.create(
            model="whisper-1",
            file=wave_data
        )
        return transcricao.text
    except Exception as e:
        print(f"Erro na transcrição do audio: {e}")
        return ""
    
def completa_textos(mensagens):
    """Gera uma resposta com base no histírico de mensagens usando o modelo GPT-3.5"""
    try:
        resposta = client.chat.completions.create(
            messages=mensagens,
            model="gpt-3.5-turbo-0125",
            max_tokens=1000,
            temperature=0
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"Erro na geração de resposta: {e}")
        return "Desculpe, não consegui entender."
    
def cria_audio(texto):
    """Cria um arquivo de áudio a partir de um texto utilizando a API do TTS."""
    if Path(arquivo_audio).exists():
        Path(arquivo_audio).unlink()
    try:
        resposta = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=texto
        )
        resposta.write_to_file(arquivo_audio)
    except Exception as e:
        print(f"Erro na criação do áudio: {e}")

def roda_audio():
    """Reproduz o arquivo de áudio gerado"""
    if Path(arquivo_audio).exists():
        playsound(arquivo_audio)
    else:
        print("Arquivo de áudio não encontrado.")

def main():
    """Função principal para executar o assistente de voz"""
    mensagens = []
    while True:
        audio = grava_audio()
        transcricao = transcricao_audio(audio)
        
        if not transcricao:
            print("Não foi possível transcrever o áudio. Tente novamente.")
            continue

        mensagens.append({"role": "user", "content": transcricao})
        print(f"User: {mensagens[-1]['content']}")
       
        resposta_texto = completa_textos(mensagens)
        mensagens.append({"role": "assistant", "content": resposta_texto})
        print(f"Assistente: {mensagens[-1]['content']}")
        
        cria_audio(resposta_texto)
        roda_audio()

if __name__ == "__main__":
    main()