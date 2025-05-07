import requests
import re
import os
import subprocess
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
    'shellscript': 'sh',
    'c': 'c',
    'cpp': 'cpp',
    'java': 'java',
    'json': 'json',
    'txt': 'txt',
    'text': 'txt',
    'css': 'css',
    'ruby': 'rb',
    'go': 'go',
    'rust': 'rs',
    'php': 'php',
    'typescript': 'ts',
    'scala': 'scala',
    'swift': 'swift',
    'kotlin': 'kt',
    'r': 'r',
    'lua': 'lua',
    'haskell': 'hs',
    'matlab': 'm',
    'perl': 'pl',
    'objective-c': 'm',
    'elixir': 'ex',
    'clojure': 'clj',
    'groovy': 'groovy',
    'sql': 'sql',
    'markdown': 'md',
    'yaml': 'yaml',
    'yml': 'yml',
    'xml': 'xml',
    'csv': 'csv',
    'tex': 'tex',
    'latex': 'latex',
    'vhdl': 'vhd',
    'verilog': 'v',
    'dart': 'dart',
    'coffee': 'coffee',
    'coffeescript': 'coffee',
    'powershell': 'ps1',
    'batch': 'bat',
    'bat': 'bat',
    'fortran': 'f90',
    'f90': 'f90',
    'assembly': 'asm',
    'asm': 'asm',
    'actionscript': 'as',
    'vim': 'vim',
    'log': 'log',
    'ini': 'ini',
    'makefile': 'mk',
    'dockerfile': 'dockerfile',
    'toml': 'toml',
    'config': 'conf',
    'conf': 'conf',
    'tsx': 'tsx',
    'jsx': 'jsx',
}


# Função para enviar prompt ao servidor Ollama
def enviar_para_ollama(prompt):
    return llm.get(OLLAMA_MODEL, prompt)

# Identifica se o prompt é para gerar código ou responder pergunta
def identificar_intencao(prompt):
    palavras_chave_codigo = ['crie', 'cria', 'criar', 'gera', 'gerar', 'escreve', 'escrever', 'exemplo', 'arquivo', 'script', 'código']
    if any(palavra in prompt.lower() for palavra in palavras_chave_codigo):
        return 'gerar_codigo'
    return 'responder_pergunta'

def identificar_comando_terminal(prompt):
    comando = prompt.split()[0].lower()
    comandos_validos = [
        'ls', 'pwd', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'echo', 'cat', 'python', 'python3',
        'git', 'curl', 'npm', 'node', 'bash', 'sh', 'chmod', 'top', 'ps', 'df', 'du',
        'ifconfig', 'ip', 'tar', 'zip', 'unzip', 'grep', 'sed', 'awk', 'find', 'man', 'nano',
        'clear'
    ]
    
    if comando in comandos_validos:
        return True
    return False

# Função para executar comandos do terminal
def executar_comando_terminal(comando):
    try:
        resultado = subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return resultado.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"[Erro] Comando falhou: {e.stderr.decode('utf-8')}"

# Processa resposta do Ollama: salva código se válido, ou mostra resposta
def processar_resposta(resposta, intencao):
    conteudo = resposta
    print("[DEBUG] Resposta:\n", conteudo)

    arquivos_gerados = []

    if intencao == 'gerar_codigo':
        blocos = re.findall(r'```([a-zA-Z0-9]*)\s*\n(.*?)\s*```', conteudo, re.DOTALL)

        if not blocos:
            print("[!] Nenhum bloco de código detectado.")
            return arquivos_gerados

        for idx, (linguagem, codigo) in enumerate(blocos):
            codigo = codigo.strip()
            linhas = codigo.splitlines()
            primeira_linha = linhas[0].strip() if linhas else ""

            nome_arquivo = None
            match_nome = re.match(r'[#/]+ ?(.+\.(?:py|js|sh|html|cpp|c|java|json|txt|css|rb|go|rs|php|ts|scala|swift|kt|r|lua|hs|m|pl|ex|clj|groovy|sql|md|yaml|xml|csv|tex|latex|vhd|v|dart|coffee|ps1|bat|f90|asm|as|vim|log|ini))', primeira_linha)
            if match_nome:
                nome_arquivo = match_nome.group(1)
                codigo = '\n'.join(linhas[1:])
            else:
                ext = EXT_POR_LINGUAGEM.get(linguagem.lower(), 'txt') if linguagem else 'txt'
                nome_arquivo = f"arquivo{idx+1}.{ext}"

            try:
                with open(nome_arquivo, "w") as f:
                    f.write(codigo)
                print(f"[✓] Arquivo '{nome_arquivo}' criado.")
                arquivos_gerados.append((nome_arquivo, codigo))
            except Exception as e:
                print(f"[x] Falha ao criar '{nome_arquivo}': {e}")
    
    else:
        print(f"Ollama: {conteudo}")
    
    return arquivos_gerados


# Função para executar código gerado
def executar_codigo(codigo, nome_arquivo):
    try:
        if nome_arquivo.endswith('.py'):
            resultado = subprocess.run(['python3', nome_arquivo], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            resultado = subprocess.run(codigo, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return resultado.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"[Erro] Comando falhou: {e.stderr.decode('utf-8')}"

# Loop principal do terminal
def terminal_inteligente():
    print("Terminal Inteligente com Ollama - Digite 'sair' para encerrar.")
    while True:
        prompt = input("Você: ")

        if prompt.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando o terminal.")
            break
        
        if identificar_comando_terminal(prompt):
            resultado = executar_comando_terminal(prompt)
            print(f"Resultado do comando:\n{resultado}")
        else:
            intencao = identificar_intencao(prompt)
            resposta = enviar_para_ollama(prompt)
            arquivos_gerados = processar_resposta(resposta, intencao)

            for nome_arquivo, codigo in arquivos_gerados:
                while True:
                    executar = input(f"Deseja rodar o código gerado em '{nome_arquivo}'? (s/n): ").lower()
                    if executar == 's':
                        resultado = executar_codigo(codigo, nome_arquivo)
                        if "Erro" in resultado:
                            print(f"[!] Erro ao executar o código de '{nome_arquivo}'. Tentando regenerar...")
                            resposta = enviar_para_ollama(prompt)
                            novos_arquivos = processar_resposta(resposta, intencao)
                            arquivos_gerados.extend(novos_arquivos)
                        else:
                            print(f"[✓] Código executado com sucesso em '{nome_arquivo}'!\nResultado: {resultado}")
                            break
                    elif executar == 'n':
                        print(f"Código em '{nome_arquivo}' não executado.")
                        break
                    else:
                        print("Opção inválida. Responda com 's' ou 'n'.")

if __name__ == "__main__":
    terminal_inteligente()
