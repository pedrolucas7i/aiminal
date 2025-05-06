import requests
import re
import os
from dotenv import load_dotenv
import llm

# Define o modelo a ser usado no servidor Ollama
OLLAMA_MODEL = "llama3.2:3b"

# Extensões padrão para linguagens detectadas
EXT_POR_LINGUAGEM = {
    'python': 'py',
    'javascript': 'js',
    'html': 'html',
    'bash': 'sh',
    'shell': 'sh',
    'c': 'c',
    'cpp': 'cpp',
    'java': 'java',
    'json': 'json',
    'txt': 'txt',
}

# Função para enviar prompt ao servidor Ollama
def enviar_para_ollama(prompt):
    return llm.get(OLLAMA_MODEL, prompt)

# Identifica se o prompt é para gerar código ou responder pergunta
def identificar_intencao(prompt):
    palavras_chave_codigo = ['cria', 'criar', 'gera', 'gerar', 'escreve', 'escrever', 'exemplo', 'arquivo', 'script', 'código']
    if any(palavra in prompt.lower() for palavra in palavras_chave_codigo):
        return 'gerar_codigo'
    return 'responder_pergunta'

# Processa resposta do Ollama: salva código se válido, ou mostra resposta
def processar_resposta(resposta, intencao):
    conteudo = resposta
    print("[DEBUG] Resposta:\n", conteudo)

    if intencao == 'gerar_codigo':
        blocos = re.findall(r'```([a-zA-Z0-9]+)?\s*(.*?)\n(.*?)```', conteudo, re.DOTALL)

        if not blocos:
            print("[!] Nenhum bloco de código detectado.")
            return

        for idx, (linguagem, header, codigo) in enumerate(blocos):
            codigo = codigo.strip()
            header = header.strip()

            if header and '.' in header:
                nome_arquivo = header
            else:
                ext = EXT_POR_LINGUAGEM.get(linguagem.lower(), 'txt') if linguagem else 'txt'
                nome_arquivo = f"arquivo{idx+1}.{ext}"

            try:
                with open(nome_arquivo, "w") as f:
                    f.write(codigo)
                print(f"[✓] Arquivo '{nome_arquivo}' criado.")
            except Exception as e:
                print(f"[x] Falha ao criar '{nome_arquivo}': {e}")
    else:
        print(f"Ollama: {conteudo}")


# Loop principal do terminal
def terminal_inteligente():
    print("Terminal Inteligente com Ollama - Digite 'sair' para encerrar.")
    while True:
        prompt = input("Você: ")
        if prompt.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando o terminal.")
            break
        intencao = identificar_intencao(prompt)
        resposta = enviar_para_ollama(prompt)
        processar_resposta(resposta, intencao)

if __name__ == "__main__":
    terminal_inteligente()
