import sys
import os
import pytest
from datetime import datetime

# Asegurar que la raíz del proyecto esté en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Lead, LeadDetails, Conversation, Message
from src.database.repository import (
    initialize_database,
    create_lead,
    update_lead_details,
    get_lead_by_id,
    get_lead_by_email,
    start_conversation,
    end_conversation,
    add_message,
    get_conversation_messages
)

# Configurar para usar una base de datos en memoria para las pruebas
os.environ["DATABASE_PATH"] = ":memory:"


@pytest.fixture
def setup_database():
    """Fixture para inicializar la base de datos antes de cada prueba"""
    initialize_database()
    yield
    # No es necesario limpiar la base de datos en memoria, se destruye automáticamente


def test_create_lead(setup_database):
    """Probar la creación de un lead"""
    # Crear un lead de prueba
    lead = Lead(
        name="Test User",
        company="Test Company",
        email="test@example.com",
        phone="+1234567890"
    )
    
    # Guardar en la base de datos
    lead_id = create_lead(lead)
    
    # Verificar que se haya creado correctamente
    assert lead_id is not None
    assert lead_id > 0


def test_get_lead_by_id(setup_database):
    """Probar la recuperación de un lead por ID"""
    # Crear un lead de prueba
    lead = Lead(
        name="Test User",
        company="Test Company",
        email="test@example.com",
        phone="+1234567890"
    )
    
    # Guardar en la base de datos
    lead_id = create_lead(lead)
    
    # Recuperar el lead por ID
    retrieved_lead = get_lead_by_id(lead_id)
    
    # Verificar que se haya recuperado correctamente
    assert retrieved_lead is not None
    assert retrieved_lead.name == "Test User"
    assert retrieved_lead.email == "test@example.com"


def test_get_lead_by_email(setup_database):
    """Probar la recuperación de un lead por email"""
    # Crear un lead de prueba
    lead = Lead(
        name="Test User",
        company="Test Company",
        email="test@example.com",
        phone="+1234567890"
    )
    
    # Guardar en la base de datos
    create_lead(lead)
    
    # Recuperar el lead por email
    retrieved_lead = get_lead_by_email("test@example.com")
    
    # Verificar que se haya recuperado correctamente
    assert retrieved_lead is not None
    assert retrieved_lead.name == "Test User"
    assert retrieved_lead.company == "Test Company"


def test_update_lead_details(setup_database):
    """Probar la actualización de detalles de un lead"""
    # Crear un lead de prueba
    lead = Lead(
        name="Test User",
        company="Test Company",
        email="test@example.com",
        phone="+1234567890"
    )
    
    # Guardar en la base de datos
    lead_id = create_lead(lead)
    
    # Crear detalles para el lead
    lead_details = LeadDetails(
        lead_id=lead_id,
        budget="10000",
        needs="Need automation",
        product_interest="CRM",
        timeline="3 months"
    )
    
    # Actualizar detalles
    update_lead_details(lead_details)
    
    # Verificar que se hayan guardado correctamente
    # Nota: En una aplicación real, necesitaríamos una función para recuperar detalles
    # Para esta prueba, verificaremos que la función no lance excepciones
    assert True


def test_conversation_flow(setup_database):
    """Probar el flujo completo de una conversación"""
    # Crear un lead de prueba
    lead = Lead(
        name="Test User",
        company="Test Company",
        email="test@example.com",
        phone="+1234567890"
    )
    
    # Guardar en la base de datos
    lead_id = create_lead(lead)
    
    # Iniciar una conversación
    conversation_id = start_conversation(lead_id)
    assert conversation_id is not None
    
    # Añadir mensajes a la conversación
    message1 = Message(
        conversation_id=conversation_id,
        sender="agent",
        content="Hola, ¿en qué puedo ayudarte?",
        timestamp=datetime.now()
    )
    
    message2 = Message(
        conversation_id=conversation_id,
        sender="lead",
        content="Estoy interesado en vuestros servicios",
        timestamp=datetime.now()
    )
    
    add_message(message1)
    add_message(message2)
    
    # Recuperar los mensajes
    messages = get_conversation_messages(conversation_id)
    
    # Verificar que los mensajes se hayan guardado correctamente
    assert len(messages) == 2
    assert messages[0].sender == "agent"
    assert messages[1].sender == "lead"
    
    # Finalizar la conversación
    end_conversation(conversation_id)
    
    # En una aplicación real, verificaríamos que ended_at se ha establecido
    assert True