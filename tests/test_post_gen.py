import os
import pytest
from unittest.mock import patch, MagicMock
from core.post_gen import save_on_history, generate_post

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