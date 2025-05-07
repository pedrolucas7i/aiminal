import requests
import re
import os
import subprocess
from dotenv import load_dotenv
import llm

# Define the model to be used with Ollama server
OLLAMA_MODEL = "llama3.2:3b"

# Default extensions for detected languages
EXT_BY_LANGUAGE = {
    'python': 'py', 'javascript': 'js', 'html': 'html', 'bash': 'sh', 'shell': 'sh',
    'shellscript': 'sh', 'c': 'c', 'cpp': 'cpp', 'java': 'java', 'json': 'json',
    'txt': 'txt', 'text': 'txt', 'css': 'css', 'ruby': 'rb', 'go': 'go', 'rust': 'rs',
    'php': 'php', 'typescript': 'ts', 'scala': 'scala', 'swift': 'swift', 'kotlin': 'kt',
    'r': 'r', 'lua': 'lua', 'haskell': 'hs', 'matlab': 'm', 'perl': 'pl',
    'objective-c': 'm', 'elixir': 'ex', 'clojure': 'clj', 'groovy': 'groovy',
    'sql': 'sql', 'markdown': 'md', 'yaml': 'yaml', 'yml': 'yml', 'xml': 'xml',
    'csv': 'csv', 'tex': 'tex', 'latex': 'latex', 'vhdl': 'vhd', 'verilog': 'v',
    'dart': 'dart', 'coffee': 'coffee', 'coffeescript': 'coffee', 'powershell': 'ps1',
    'batch': 'bat', 'bat': 'bat', 'fortran': 'f90', 'f90': 'f90', 'assembly': 'asm',
    'asm': 'asm', 'actionscript': 'as', 'vim': 'vim', 'log': 'log', 'ini': 'ini',
    'makefile': 'mk', 'dockerfile': 'dockerfile', 'toml': 'toml', 'config': 'conf',
    'conf': 'conf', 'tsx': 'tsx', 'jsx': 'jsx',
}

def send_to_ollama(prompt):
    return llm.get(OLLAMA_MODEL, prompt)

def execute_terminal_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.stdout.decode('utf-8'), e.stderr.decode('utf-8')

def process_response(response, intent):
    content = response
    print("[DEBUG] Response:\n", content)

    generated_files = []

    if intent == 'generate_code':
        blocks = re.findall(r'```([a-zA-Z0-9]*)\s*\n(.*?)\s*```', content, re.DOTALL)
        if not blocks:
            print("[!] No code blocks detected.")
            return generated_files

        for idx, (language, code) in enumerate(blocks):
            code = code.strip()
            lines = code.splitlines()
            first_line = lines[0].strip() if lines else ""

            match = re.match(r'[#/]+ ?(.+\.(?:\w+))', first_line)
            if match:
                filename = match.group(1)
                code = '\n'.join(lines[1:])
            else:
                ext = EXT_BY_LANGUAGE.get(language.lower(), 'txt') if language else 'txt'
                filename = f"file{idx+1}.{ext}"

            try:
                with open(filename, "w") as f:
                    f.write(code)
                print(f"[✓] File '{filename}' created.")
                generated_files.append((filename, code))
            except Exception as e:
                print(f"[x] Failed to create '{filename}': {e}")
    else:
        print(f"Ollama: {content}")

    return generated_files

def run_generated_code(code, filename):
    try:
        if filename.endswith('.py'):
            result = subprocess.run(['python3', filename], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(code, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"[Error] Command failed: {e.stderr.decode('utf-8')}"

def intelligent_terminal():
    print("Aiminal (AI + TERMINAL) - Use /code, /question ou /fix. Digite 'exit' para sair.")
    while True:
        prompt = input(f"{os.getcwd()} $> ").strip()

        if prompt.lower() in ['exit', 'quit']:
            print("Shutting down the terminal.")
            break

        if prompt.startswith('/code'):
            clean_prompt = prompt[len('/code'):].strip()
            response = send_to_ollama(clean_prompt)
            files = process_response(response, 'generate_code')

            for filename, code in files:
                while True:
                    run = input(f"Do you want to run the generated code in '{filename}'? (y/n): ").lower()
                    if run == 'y':
                        result = run_generated_code(code, filename)
                        print(f"[✓] Output from '{filename}':\n{result}")
                        break
                    elif run == 'n':
                        break
                    else:
                        print("Please enter 'y' or 'n'.")

        elif prompt.startswith('/question'):
            clean_prompt = prompt[len('/question'):].strip()
            response = send_to_ollama(clean_prompt)
            print(f"Ollama: {response}")

        elif prompt.startswith('/fix'):
            print("[!] Capturing terminal context to send to AI...")
            output, error = execute_terminal_command("history | tail -n 10")
            terminal_state = f"Últimos comandos:\n{output}\nErros recentes:\n{error}"
            fix_prompt = f"Análise os comandos e erros abaixo e sugira correções:\n{terminal_state}"
            response = send_to_ollama(fix_prompt)
            print(f"[AI Fix Suggestion]\n{response}")

        else:
            output, error = execute_terminal_command(prompt)
            if output:
                print(f"[Output]\n{output}")
            if error:
                print(f"[Error]\n{error}")

if __name__ == "__main__":
    intelligent_terminal()
