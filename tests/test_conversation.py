import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Asegurar que la raíz del proyecto esté en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversation.intent import detect_intent
from src.conversation.entities import extract_lead_info, create_lead_from_info, update_lead_from_info
from src.conversation.agent import VoiceAgent
from src.database.models import Lead, LeadDetails


@pytest.fixture
def mock_llm():
    """Fixture para simular respuestas del LLM"""
    with patch('src.llm.model.generate_response') as mock_generate:
        mock_generate.return_value = "Esta es una respuesta simulada del agente."
        yield mock_generate


@pytest.fixture
def mock_intent_detection():
    """Fixture para simular detección de intenciones"""
    with patch('src.conversation.intent.intent_model') as mock_model:
        mock_response = MagicMock()
        mock_response.content = "INQUIRY"
        mock_model.invoke.return_value = mock_response
        yield mock_model


@pytest.fixture
def mock_entity_extraction():
    """Fixture para simular extracción de entidades"""
    with patch('src.llm.model.extract_entities') as mock_extract:
        mock_extract.return_value = {
            "nombre": "Juan Pérez",
            "empresa": "TechCorp",
            "email": "juan@example.com"
        }
        yield mock_extract


@pytest.fixture
def mock_database():
    """Fixture para simular operaciones de base de datos"""
    with patch('src.conversation.agent.create_lead') as mock_create_lead, \
         patch('src.conversation.agent.update_lead_details') as mock_update_details, \
         patch('src.conversation.agent.start_conversation') as mock_start_conv, \
         patch('src.conversation.agent.add_message') as mock_add_msg, \
         patch('src.conversation.agent.get_lead_by_id') as mock_get_lead:
        
        mock_create_lead.return_value = 1
        mock_update_details.return_value = None
        mock_start_conv.return_value = 1
        mock_add_msg.return_value = 1
        
        lead = Lead(
            id=1,
            name="Juan Pérez",
            company="TechCorp",
            email="juan@example.com",
            phone=None
        )
        mock_get_lead.return_value = lead
        
        yield {
            "create_lead": mock_create_lead,
            "update_details": mock_update_details,
            "start_conversation": mock_start_conv,
            "add_message": mock_add_msg,
            "get_lead": mock_get_lead
        }


def test_detect_intent(mock_intent_detection):
    """Probar la detección de intenciones"""
    # Configurar datos de prueba
    text = "Me gustaría saber más sobre vuestros servicios"
    
    # Llamar a la función
    intent = detect_intent(text)
    
    # Verificar que se haya llamado al modelo
    assert mock_intent_detection.invoke.called
    
    # Verificar que la intención sea la esperada
    assert intent == "INQUIRY"


def test_extract_lead_info(mock_entity_extraction):
    """Probar la extracción de información del lead"""
    # Configurar datos de prueba
    text = "Me llamo Juan Pérez y trabajo en TechCorp. Mi email es juan@example.com"
    existing_info = {}
    
    # Llamar a la función
    lead_info = extract_lead_info(text, existing_info)
    
    # Verificar que se haya llamado a la función de extracción
    mock_entity_extraction.assert_called_once()
    
    # Verificar que la información extraída sea correcta
    assert lead_info["name"] == "Juan Pérez"
    assert lead_info["company"] == "TechCorp"
    assert lead_info["email"] == "juan@example.com"


def test_create_lead_from_info():
    """Probar la creación de objetos Lead a partir de información extraída"""
    # Configurar datos de prueba
    lead_info = {
        "name": "Juan Pérez",
        "company": "TechCorp",
        "email": "juan@example.com",
        "phone": "+1234567890",
        "budget": "10000",
        "needs": "Automatización",
        "product_interest": "CRM",
        "timeline": "3 meses"
    }
    
    # Llamar a la función
    lead, lead_details = create_lead_from_info(lead_info)
    
    # Verificar que los objetos creados sean correctos
    assert lead.name == "Juan Pérez"
    assert lead.company == "TechCorp"
    assert lead.email == "juan@example.com"
    assert lead.phone == "+1234567890"
    
    assert lead_details.budget == "10000"
    assert lead_details.needs == "Automatización"
    assert lead_details.product_interest == "CRM"
    assert lead_details.timeline == "3 meses"


def test_update_lead_from_info():
    """Probar la actualización de objetos Lead con nueva información"""
    # Configurar objetos existentes
    lead = Lead(
        id=1,
        name="Juan",
        company="Tech",
        email="juan@example.com",
        phone=None
    )
    
    lead_details = LeadDetails(
        lead_id=1,
        budget=None,
        needs=None,
        product_interest=None,
        timeline=None
    )
    
    # Nueva información
    lead_info = {
        "name": "Juan Pérez",
        "company": "TechCorp",
        "phone": "+1234567890",
        "budget": "10000",
        "needs": "Automatización"
    }
    
    # Llamar a la función
    updated_lead, updated_details = update_lead_from_info(lead, lead_details, lead_info)
    
    # Verificar que los objetos se hayan actualizado correctamente
    assert updated_lead.name == "Juan Pérez"
    assert updated_lead.company == "TechCorp"
    assert updated_lead.phone == "+1234567890"
    
    assert updated_details.budget == "10000"
    assert updated_details.needs == "Automatización"


def test_voice_agent_start_session(mock_database):
    """Probar el inicio de sesión del agente de voz"""
    # Crear una instancia del agente
    agent = VoiceAgent()
    
    # Iniciar sesión sin ID de lead
    greeting = agent.start_session()
    
    # Verificar que se haya generado un saludo
    assert greeting is not None
    assert len(greeting) > 0
    
    # Iniciar sesión con ID de lead
    greeting = agent.start_session(lead_id=1)
    
    # Verificar que se haya llamado a get_lead_by_id
    mock_database["get_lead"].assert_called_once_with(1)
    
    # Verificar que se haya llamado a start_conversation
    mock_database["start_conversation"].assert_called_once()


def test_voice_agent_process_text_input(mock_llm, mock_entity_extraction, mock_database):
    """Probar el procesamiento de entrada de texto del agente"""
    # Crear una instancia del agente
    agent = VoiceAgent()
    agent.start_session()
    
    # Configurar entrada de texto
    user_input = "Me llamo Juan Pérez y trabajo en TechCorp"
    
    # Procesar la entrada
    response = agent.process_text_input(user_input)
    
    # Verificar que se haya llamado a generate_response
    mock_llm.assert_called_once()
    
    # Verificar que se haya actualizado el historial de conversación
    assert len(agent.conversation_history) == 2  # Saludo + respuesta
    assert agent.conversation_history[1]["sender"] == "lead"
    assert agent.conversation_history[1]["content"] == user_input


def test_voice_agent_end_session():
    """Probar la finalización de sesión del agente"""
    # Crear una instancia del agente
    agent = VoiceAgent()
    agent.start_session()
    
    # Configurar estado del agente
    agent.lead_info = {"name": "Test User"}
    agent.conversation_history = [{"sender": "agent", "content": "Hola"}]
    
    # Finalizar sesión
    with patch('src.conversation.agent.end_conversation') as mock_end:
        mock_end.return_value = None
        result = agent.end_session()
    
    # Verificar que se haya reiniciado el estado
    assert result is True
    assert agent.lead_info == {}
    assert agent.conversation_history == []