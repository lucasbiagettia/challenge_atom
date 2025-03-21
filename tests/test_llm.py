import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Asegurar que la raíz del proyecto esté en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.model import generate_response, extract_entities
from src.llm.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


@pytest.fixture
def mock_openai_response():
    """Fixture para simular respuestas de OpenAI"""
    with patch('langchain_openai.ChatOpenAI') as mock_chat:
        # Configurar el mock para devolver una respuesta simulada
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Esta es una respuesta simulada del LLM."
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance
        yield mock_chat


def test_generate_response(mock_openai_response):
    """Probar la generación de respuestas del LLM"""
    # Configurar datos de prueba
    user_input = "Hola, estoy interesado en vuestros servicios"
    conversation_history = [
        {"sender": "agent", "content": "Hola, ¿en qué puedo ayudarte?", "timestamp": "2023-01-01T12:00:00"},
        {"sender": "lead", "content": "Quiero información sobre vuestros servicios", "timestamp": "2023-01-01T12:01:00"}
    ]
    lead_info = {
        "name": "Test User",
        "company": "Test Company"
    }
    
    # Llamar a la función
    response = generate_response(user_input, conversation_history, lead_info)
    
    # Verificar que se haya llamado a OpenAI con los parámetros correctos
    mock_openai_response.assert_called_once()
    
    # Verificar que la respuesta sea la esperada
    assert response == "Esta es una respuesta simulada del LLM."


def test_extract_entities(mock_openai_response):
    """Probar la extracción de entidades del texto"""
    # Configurar el mock para devolver JSON
    mock_instance = mock_openai_response.return_value
    mock_response = MagicMock()
    mock_response.content = '{"nombre": "Juan Pérez", "empresa": "TechCorp", "email": "juan@example.com"}'
    mock_instance.invoke.return_value = mock_response
    
    # Configurar datos de prueba
    user_input = "Me llamo Juan Pérez y trabajo en TechCorp. Mi email es juan@example.com"
    existing_info = {}
    
    # Llamar a la función
    entities = extract_entities(user_input, existing_info)
    
    # Verificar que se haya llamado a OpenAI
    assert mock_instance.invoke.called
    
    # Verificar que las entidades extraídas sean correctas
    assert entities["nombre"] == "Juan Pérez"
    assert entities["empresa"] == "TechCorp"
    assert entities["email"] == "juan@example.com"


def test_extract_entities_with_existing_info(mock_openai_response):
    """Probar la extracción de entidades con información existente"""
    # Configurar el mock para devolver JSON
    mock_instance = mock_openai_response.return_value
    mock_response = MagicMock()
    mock_response.content = '{"telefono": "+1234567890", "necesidades": "Automatización"}'
    mock_instance.invoke.return_value = mock_response
    
    # Configurar datos de prueba
    user_input = "Mi número es +1234567890 y necesito soluciones de automatización"
    existing_info = {
        "nombre": "Juan Pérez",
        "empresa": "TechCorp"
    }
    
    # Llamar a la función
    entities = extract_entities(user_input, existing_info)
    
    # Verificar que se haya llamado a OpenAI
    assert mock_instance.invoke.called
    
    # Verificar que las entidades extraídas sean correctas
    assert entities["telefono"] == "+1234567890"
    assert entities["necesidades"] == "Automatización"


def test_extract_entities_malformed_response(mock_openai_response):
    """Probar el manejo de respuestas malformadas"""
    # Configurar el mock para devolver una respuesta no JSON
    mock_instance = mock_openai_response.return_value
    mock_response = MagicMock()
    mock_response.content = "Esto no es un JSON válido"
    mock_instance.invoke.return_value = mock_response
    
    # Configurar datos de prueba
    user_input = "Texto de prueba"
    existing_info = {}
    
    # Llamar a la función
    entities = extract_entities(user_input, existing_info)
    
    # Verificar que se devuelva un diccionario vacío en caso de error
    assert entities == {}