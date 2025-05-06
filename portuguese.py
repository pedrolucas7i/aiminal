import requests
import re
import os
from dotenv import load_dotenv
import llm


# Define o modelo a ser usado no servidor Ollama
OLLAMA_MODEL = "llama3.2:3b"

# Função para enviar prompt ao servidor Ollama
def enviar_para_ollama(prompt):
    return llm.get(OLLAMA_MODEL, prompt)

# Identifica se o prompt é para gerar código ou responder pergunta
def identificar_intencao(prompt):
    palavras_chave_codigo = ['cria', 'criar', 'gera', 'gerar', 'escreve', 'escrever', 'exemplo', 'arquivo', 'script', 'código']
    if any(palavra in prompt.lower() for palavra in palavras_chave_codigo):
        return 'gerar_codigo'
    return 'responder_pergunta'

# Valida se o código é sintaticamente correto
def validar_codigo(codigo):
    try:
        compile(codigo, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"[!] Erro de sintaxe: {e}")
        return False

# Processa resposta do Ollama: salva código se válido, ou mostra resposta
def processar_resposta(resposta, intencao):
    conteudo = resposta
    if intencao == 'gerar_codigo':
        match = re.search(r'```python(.*?)```', conteudo, re.DOTALL)
        if match:
            codigo = match.group(1).strip()
            if validar_codigo(codigo):
                with open("codigo_gerado.py", "w") as f:
                    f.write(codigo)
                print("[OK] Arquivo 'codigo_gerado.py' criado com sucesso!")
            else:
                print("[!] Código gerado inválido. Não foi salvo.")
        else:
            print("[!] Nenhum código detectado na resposta.")
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
