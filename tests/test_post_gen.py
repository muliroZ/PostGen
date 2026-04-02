import os
import pytest
from unittest.mock import patch, MagicMock
from core.post_gen import save_on_history, generate_post
from core.cli import run_cli

# Teste 01 - Salvar na pasta local quando a variável DIR_HISTORY_PATH não está especificada
def test_save_on_history_local(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """
    Testa se o ficheiro é salvo corretamente no diretório atual 
    quando a variável DIR_HISTORY_PATH não está definida.
    """
    monkeypatch.chdir(tmp_path)
    
    monkeypatch.setattr("core.post_gen.dir_history_path", None)

    tema = "Testes Unitários com Pytest"
    conteudo = "Conteúdo simulado do post."
    
    filepath = save_on_history(tema, conteudo)
    
    assert filepath.startswith("post_")
    assert filepath.endswith(".md")
    assert os.path.exists(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        file_content = f.read()
        assert tema in file_content
        assert conteudo in file_content

# Teste 02 - Salvar na pasta especificada no DIR_HISTORY_PATH
def test_save_on_history_with_custom_dir(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """
    Testa se o ficheiro é movido corretamente quando DIR_HISTORY_PATH está configurado.
    """
    monkeypatch.chdir(tmp_path)
    
    history_dir = tmp_path / "meu_historico"
    history_dir.mkdir()
    
    monkeypatch.setattr("core.post_gen.dir_history_path", str(history_dir))

    filepath = save_on_history("Tema Mover", "Conteúdo a ser movido")
    
    assert str(history_dir) in filepath
    assert os.path.exists(filepath)

# Teste 03 - Geração do post com resposta de sucesso da API
@patch("core.post_gen.genai.Client")
def test_generate_post_success(mock_client_class):
    """
    Testa a geração de postagem simulando uma resposta de sucesso da API do Gemini.
    """
    mock_response = MagicMock()
    mock_response.text = "Este é um post gerado pelo mock."
    
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client_instance

    with patch.dict(os.environ, {"GEMINI_API_KEY": "chave-falsa-teste"}):
        resultado = generate_post("Tópico de Sucesso")
        
    assert resultado == "Este é um post gerado pelo mock."
    mock_client_instance.models.generate_content.assert_called_once()

# Teste 04 - Injetar conteúdo do arquivo no prompt
@patch("core.post_gen.genai.Client")
def test_generate_post_with_file_context(mock_client_class):
    """
    Testa a geração de postagem garantindo que o conteúdo do ficheiro é injetado no prompt.
    """
    mock_response = MagicMock()
    mock_response.text = "Post baseado no código fornecido."
    
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client_instance

    topic_mock = "Refatoração de Classe"
    file_context_mock = "public class Example { private int id; }"

    with patch.dict(os.environ, {"GEMINI_API_KEY": "chave-falsa-teste"}):
        resultado = generate_post(topic=topic_mock, file_context=file_context_mock)
        
    assert resultado == "Post baseado no código fornecido."
    
    chamada_api = mock_client_instance.models.generate_content.call_args
    argumentos = chamada_api.kwargs
    prompt_enviado = argumentos.get("contents", "")
    
    assert topic_mock in prompt_enviado
    assert file_context_mock in prompt_enviado
    assert "Utilize o seguinte trecho de código" in prompt_enviado

# Teste 05 - Tratamento de exceções lançadas pela API
@patch("core.post_gen.genai.Client")
def test_generate_post_api_error(mock_client_class):
    """
    Testa o comportamento da função quando a API lança uma exceção.
    """
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.side_effect = Exception("Timeout da API")
    mock_client_class.return_value = mock_client_instance

    with patch.dict(os.environ, {"GEMINI_API_KEY": "chave-falsa-teste"}):
        resultado = generate_post("Tópico de Erro")
        
    assert isinstance(resultado, str)
    assert "Erro na API:" in resultado
    assert "Timeout da API" in resultado

# Teste 06 - Sobrescrita de gravações de posts idênticos no histórico
@patch("core.post_gen.datetime")
def test_save_on_history_collision_overwrite(mock_datetime, monkeypatch, tmp_path):
    """
    Testa se o sistema lida corretamente com colisões de nomes de ficheiros.
    Simula duas gravações ocorrendo no exato mesmo segundo.
    A segunda gravação deve sobrescrever a primeira sem lançar shutil.Error.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    fixed_date = datetime(2026, 4, 2, 13, 28, 15, tzinfo=ZoneInfo("America/Sao_Paulo"))
    
    mock_datetime.now.return_value = fixed_date
    
    history_dir = tmp_path / "historico_colisao"
    history_dir.mkdir()
    monkeypatch.setattr("core.post_gen.dir_history_path", str(history_dir))
    monkeypatch.chdir(tmp_path)

    path1 = save_on_history("Primeiro Tema", "Este é o conteúdo original.")
    
    path2 = save_on_history("Tema Atualizado", "Conteúdo que deve sobrescrever o original.")
    
    assert path1 == path2
    assert os.path.exists(path2)
    
    with open(path2, "r", encoding="utf-8") as f:
        content_read = f.read()
        assert "Conteúdo que deve sobrescrever o original." in content_read
        assert "Este é o conteúdo original." not in content_read

# TESTES DO MÓDULO DE CLI #

# Teste 07 - Interrupção da operação quando não há nenhum assunto
def test_run_cli_empty_topic(capsys):
    """
    Testa se o CLI é interrompido corretamente quando o utilizador 
    não fornece um assunto (pressiona apenas Enter).
    """
    with patch("builtins.input", return_value=""):
        run_cli()

    captured = capsys.readouterr()
    assert "Operação cancelada. Nenhum assunto fornecido." in captured.out

# Teste 08 - Fluxo padrão do CLI (assunto: OK, contexto: Vazio, salvar: NÃO)
@patch("core.cli.generate_post")
def test_run_cli_success_no_file(mock_generate, capsys):
    """
    Testa o fluxo padrão: Tópico válido, sem ficheiro de contexto, recusando salvar.
    """
    mock_generate.return_value = "Texto do post gerado pelo mock."
    
    entradas_simuladas = ["Boas práticas em Java", "", "n"]
    
    with patch("builtins.input", side_effect=entradas_simuladas):
        run_cli()
        
    captured = capsys.readouterr()
    
    # Verificações visuais no terminal
    assert "Conectando com a API do Gemini. Aguarde..." in captured.out
    assert "Texto do post gerado pelo mock." in captured.out
    
    # Garante que a função central foi chamada com os argumentos corretos
    mock_generate.assert_called_once_with("Boas práticas em Java", None)

# Teste 09 - Fluxo completo do CLI
@patch("core.cli.save_on_history")
@patch("core.cli.generate_post")
def test_run_cli_with_file_and_save(mock_generate, mock_save, capsys, tmp_path):
    """
    Testa o fluxo completo: Tópico válido, com ficheiro de contexto válido 
    (testando sanitização de aspas) e aceitando guardar o histórico.
    """
    mock_generate.return_value = "Post altamente técnico."
    mock_save.return_value = "/mock/path/post_mock.md"
    
    arquivo_temp = tmp_path / "Config.java"
    arquivo_temp.write_text("public class Config {}", encoding="utf-8")
    
    entradas_simuladas = [
        "Injeção de Dependências", 
        f"'{arquivo_temp}'",
        "s"
    ]
    
    with patch("builtins.input", side_effect=entradas_simuladas):
        run_cli()
        
    captured = capsys.readouterr()
    
    assert "Arquivo 'Config.java' carregado com sucesso." in captured.out
    assert "Post salvo: /mock/path/post_mock.md" in captured.out
    
    mock_generate.assert_called_once_with("Injeção de Dependências", "public class Config {}")
    mock_save.assert_called_once_with("Injeção de Dependências", "Post altamente técnico.")

# Teste 10 - Tratamento de caminhos de contexto não existentes
@patch("core.cli.generate_post")
def test_run_cli_file_not_found(mock_generate, capsys):
    """
    Testa a resiliência do CLI caso o utilizador passe um caminho que não existe.
    """
    mock_generate.return_value = "Post gerado."
    
    entradas_simuladas = ["Tópico de teste", "/caminho/falso/ficheiro.txt", "n"]
    
    with patch("builtins.input", side_effect=entradas_simuladas):
        run_cli()
        
    captured = capsys.readouterr()
    assert "[AVISO] Arquivo não encontrado. Prosseguindo sem o contexto do arquivo." in captured.out
    
    mock_generate.assert_called_once_with("Tópico de teste", None)

# Teste 11 - Cancelar a operação de forma segura quando a chave de API estiver faltando
def test_generate_post_missing_api_key(monkeypatch):
    """
    Testa se o sistema aborta a operação de forma segura e devolve o erro correto
    caso a chave GEMINI_API_KEY não exista nas variáveis de ambiente.
    """
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    resultado = generate_post("Tópico qualquer", "Contexto qualquer")
    
    assert isinstance(resultado, str)
    assert "Erro na API: Chave GEMINI_API_KEY não encontrada" in resultado

# Teste 12 - Ignorar contextos que sejam strings vazias
@patch("core.post_gen.genai.Client")
def test_generate_post_empty_file_context(mock_client_class):
    """
    Testa se a função ignora corretamente contextos de ficheiros que 
    sejam strings vazias, não sujando o prompt enviado à IA.
    """
    mock_response = MagicMock()
    mock_response.text = "Post sem contexto de ficheiro."
    
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client_instance

    with patch.dict(os.environ, {"GEMINI_API_KEY": "chave-falsa-teste"}):
        resultado = generate_post(topic="Tópico de Teste", file_context="")
        
    assert resultado == "Post sem contexto de ficheiro."
    
    chamada_api = mock_client_instance.models.generate_content.call_args
    argumentos = chamada_api.kwargs
    prompt_enviado = argumentos.get("contents", "")
    
    assert "Tópico de Teste" in prompt_enviado
    assert "Utilize o seguinte trecho de código" not in prompt_enviado
