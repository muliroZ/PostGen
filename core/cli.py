#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
#   "python-dotenv",
# ]
# ///

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.post_gen import generate_post, save_on_history

def run_cli():
    topic = input("Sobre qual assunto vamos falar hoje?\n> ").strip()
    if not topic:
        print("Operação cancelada. Nenhum assunto fornecido.")
        return

    print("\n[OPCIONAL] Anexar arquivo de código ou configuração como contexto?")
    print("Dica: Pode arrastar o arquivo para o terminal ou digitar o caminho.")
    file_path_input = input("Caminho do arquivo (ou pressione Enter para pular):\n> ").strip()

    file_context_content = None

    if file_path_input:
        clean_path = file_path_input.strip("'\" ")

        if os.path.exists(clean_path):
            try:
                with open(clean_path, "r", encoding="utf-8") as f:
                    file_context_content = f.read()
                filename = os.path.basename(clean_path)
                print(f"[SISTEMA] Arquivo '{filename}' carregado com sucesso.")
            except Exception as e:
                print(f"[ERRO] Falha ao ler o arquivo: {e}")
                print("[SISTEMA] Prosseguindo sem o contexto do arquivo.")
        else:
            print("[AVISO] Arquivo não encontrado. Prosseguindo sem o contexto do arquivo.")

    print("\nConectando com a API do Gemini. Aguarde...")

    post = generate_post(topic, file_context_content)
    if post is None or "Erro na API" in post:
        print(f"\n[ERRO FATAL] {post}")
        return
    
    print("\n" + "=" * 40 + "\n" + post + "\n" + "=" * 40 + "\n")

    option = input("Deseja salvar esse post no histórico (S/N): ").strip().lower()
    if option == 's':
        path = save_on_history(topic, post)
        print(f"[SISTEMA] Post salvo: {path}")

if __name__ == "__main__":
    run_cli()