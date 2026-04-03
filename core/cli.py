#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
#   "python-dotenv",
#   "rich",
# ]
# ///

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.post_gen import generate_post, save_on_history
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def run_cli():
    console.print(Panel.fit("[bold #00fa9a]PostGen[/bold #00fa9a]", border_style="#00fa9a"))

    topic = Prompt.ask("[bold white]Sobre qual assunto vamos falar hoje?\n[/bold white]").strip()
    if not topic:
        console.print("[bold red][SISTEMA] Operação cancelada. Nenhum assunto fornecido.[/bold red]")
        return

    console.print("\n[dim][OPCIONAL] Anexar arquivo de código ou configuração como contexto?[/dim]")
    console.print("[dim]Dica: Pode arrastar o arquivo para o terminal ou digitar o caminho.[/dim]")

    file_path_input = Prompt.ask("[bold white]Caminho do arquivo (ou pressione Enter para pular)[/bold white]").strip()

    file_context_content = None

    if file_path_input:
        clean_path = file_path_input.strip("'\" ")

        if os.path.exists(clean_path):
            try:
                with open(clean_path, "r", encoding="utf-8") as f:
                    file_context_content = f.read()
                filename = os.path.basename(clean_path)
                console.print(f"[bold green][SISTEMA] Arquivo '{filename}' carregado com sucesso.[/bold green]")
            except Exception as e:
                print(f"[bold red][ERRO] Falha ao ler o arquivo: {e}[/bold red]")
                print("[yellow][SISTEMA] Prosseguindo sem o contexto do arquivo.[/yellow]")
        else:
            print("[bold yellow][AVISO] Arquivo não encontrado. Prosseguindo sem o contexto do arquivo.[/bold yellow]")

    with console.status("\n[bold cyan]Conectando com a API do Gemini. Aguarde...[/bold cyan]", spinner="dots"):
        post = generate_post(topic, file_context_content)
    
    if post is None or "Erro na API" in post:
        console.print(f"\n[bold red][ERRO FATAL][/bold red] {post}")
        return
    
    console.print()
    console.print(Panel(post, title="[bold #00fa9a]Post Gerado[/bold #00fa9a]", border_style="#00fa9a", expand=False))
    console.print()

    option = Prompt.ask("[bold white]Deseja salvar esse post no histórico?[/bold white]", choices=["s", "n"], default="n", case_sensitive=False)
    if option == 's':
        path = save_on_history(topic, post)
        console.print(f"[bold green][SISTEMA] Post salvo: {path}[/bold green]")

if __name__ == "__main__":
    try:
        run_cli()
    except (Exception, KeyboardInterrupt):
        console.print("\n[bold yellow][SISTEMA] Encerrando PostGen...[/bold yellow]")