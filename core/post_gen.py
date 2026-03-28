from google import genai
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import shutil

load_dotenv()

dir_history_path: str | None = os.getenv("DIR_HISTORY_PATH") # opcional, adicione "DIR_HISTORY_PATH" no seu .env

def save_on_history(theme: str, content: str) -> str:
    tz = ZoneInfo("America/Sao_Paulo")
    now = datetime.now(tz=tz).strftime("%Y-%m-%d_%H-%M")

    file_path = f"post_{now}.md"

    with open(file=file_path, mode="w", encoding="utf-8") as f:
        f.write(f"# Post para LinkedIn - {datetime.now(tz=tz).strftime("%d-%m-%Y")}\n")
        f.write(f"**Tema sugerido:** {theme}\n\n")
        f.write("---\n\n")
        f.write(content)

    if dir_history_path is not None:
        shutil.move(file_path, dir_history_path)
        return f"{dir_history_path}/{file_path}"

    return file_path

def generate_post(topic: str) -> str | None:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tone = "pragmático, técnico e direto ao ponto, não tão formal, com uma pitada de entusiasmo" # defina como quiser

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=f"""
                    Você é um estudante de Engenharia de Software e Desenvolvedor Backend especializado em Java e Spring Boot.
                    Você gosta de compartilhar seus aprendizados, dúvidas, desafios reais de arquitetura e código limpo no LinkedIn.
                    
                    As postagens criadas devem seguir as diretrizes especificadas abaixo
                    
                    Diretrizes:
                    - O tom deve ser {tone}.
                    - O texto deve ser formatado para leitura dinâmica (use parágrafos curtos e espaçados).
                    - Se aplicável, mencione conceitos práticos de backend (ex: Docker, persistência de dados, APIs REST, lógica de domínio).
                    - Inclua 3 a 5 hashtags relevantes no final.
                    - Termine com uma pergunta para incentivar os comentários.
                    - Não use saudações genéricas de IA (como "Aqui está o seu post"). Retorne apenas o conteúdo final da postagem.
                    - Tente não usar muitos emojis (max: 2).
                    - Fale sobre boas práticas (Clean Code, SOLID e etc.) somente quando for requisitado ou extremamente necessário para o tema.
                    - Formate com espaçamento para leitura fácil no celular.
                    - Lembre-se, você é um Estudante/Júnior, por isso não deve impor verdades absolutas ou soluções "perfeitas"
                """
            ),
            contents=f"Crie uma postagem para o LinkedIn sobre o seguinte tópico (seguindo as diretrizes): {topic}"
        )
        return response.text
    except Exception as e:
        return f"Erro na API: {e}"
