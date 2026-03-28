#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
#   "python-dotenv",
# ]
# ///

from post_gen import generate_post, save_on_history

def run_cli():
    topic = input("Sobre qual assunto vamos falar hoje?\n> ")
    print("\nGerando post...\n")

    post = generate_post(topic)
    if post is None:
        print("Erro ao criar post. Tente novamente (caso persista, confira sua chave de API)")
        return
    
    print("\n" + "=" * 30 + "\n" + post + "\n" + "=" * 30 + "\n")

    option = input("Deseja salvar esse post no histórico (S/N): ").lower()
    if option == 's':
        path = save_on_history(topic, post)
        print(f"Post salvo: {path}")

if __name__ == "__main__":
    run_cli()