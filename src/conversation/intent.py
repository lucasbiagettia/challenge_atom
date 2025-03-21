"""
Módulo para la detección de intenciones del usuario
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
from src.config import OPENAI_API_KEY, LLM_MODEL_NAME

# Inicializar el modelo de lenguaje
intent_model = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=LLM_MODEL_NAME,
    temperature=0.3  # Temperatura baja para respuestas más deterministas
)

# Definir las posibles intenciones
INTENTS = {
    "GREETING": "Saludo inicial o presentación",
    "INQUIRY": "Consulta sobre productos o servicios",
    "PRICING": "Consulta sobre precios o presupuestos",
    "TIMELINE": "Consulta sobre plazos o tiempos de entrega",
    "REQUIREMENTS": "Explicación de necesidades o requisitos",
    "CONTACT_INFO": "Proporcionando información de contacto",
    "COMPETITOR": "Mencionando o comparando con competidores",
    "OBJECTION": "Expresando una objeción o preocupación",
    "INTEREST": "Mostrando interés por seguir adelante",
    "CLOSING": "Finalizando la conversación",
    "IRRELEVANT": "Tema no relacionado con el negocio"
}

# Sistema prompt para la detección de intenciones
INTENT_SYSTEM_PROMPT = f"""
Eres un sistema de detección de intenciones para un asistente de ventas. Tu trabajo es analizar el texto del usuario 
y determinar cuál es la intención principal entre las siguientes opciones:

{json.dumps(INTENTS, indent=2)}

Responde únicamente con el identificador de la intención (por ejemplo, "GREETING").
"""


def detect_intent(text):
    """
    Detectar la intención principal en el texto del usuario
    
    Args:
        text (str): Texto del usuario
        
    Returns:
        str: Identificador de la intención detectada
    """
    if not text:
        return "IRRELEVANT"
    
    # Crear mensajes para el modelo
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=f"Analiza la siguiente entrada del usuario y determina su intención principal:\n\n\"{text}\"")
    ]
    
    # Obtener la respuesta del modelo
    try:
        response = intent_model.invoke(messages)
        intent = response.content.strip().upper()
        
        # Verificar que la intención devuelta sea válida
        if intent in INTENTS:
            return intent
        else:
            return "IRRELEVANT"
    except Exception as e:
        print(f"Error en la detección de intención: {e}")
        return "IRRELEVANT"