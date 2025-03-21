import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from src.config import OPENAI_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE
from src.llm.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, ENTITY_EXTRACTION_PROMPT

# Inicializar el modelo de lenguaje
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=LLM_MODEL_NAME,
    temperature=LLM_TEMPERATURE
)


def generate_response(user_input, conversation_history=None, lead_info=None):
    """
    Generar una respuesta usando el LLM
    
    Args:
        user_input (str): Entrada del usuario
        conversation_history (list): Historial de la conversación
        lead_info (dict): Información conocida del lead
        
    Returns:
        str: Respuesta generada por el LLM
    """
    if conversation_history is None:
        conversation_history = []
    
    if lead_info is None:
        lead_info = {}
    
    # Formatear el prompt con la información del lead y el historial de conversación
    formatted_history = "\n".join([f"{'Agente' if msg['sender'] == 'agent' else 'Lead'}: {msg['content']}" for msg in conversation_history])
    lead_info_str = json.dumps(lead_info, ensure_ascii=False) if lead_info else "{}"
    
    # Formatear el prompt del usuario
    user_prompt = USER_PROMPT_TEMPLATE.format(
        conversation_history=formatted_history,
        lead_info=lead_info_str,
        user_input=user_input
    )
    
    # Crear los mensajes para el LLM
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    
    # Generar la respuesta
    response = llm.invoke(messages)
    
    return response.content


def extract_entities(user_input, existing_info=None):
    """
    Extraer entidades e información relevante del texto del usuario
    
    Args:
        user_input (str): Entrada del usuario
        existing_info (dict): Información existente del lead
        
    Returns:
        dict: Entidades extraídas
    """
    if existing_info is None:
        existing_info = {}
    
    # Formatear el prompt para extracción de entidades
    try:
        entity_prompt = ENTITY_EXTRACTION_PROMPT.format(
            user_input=user_input,
            existing_info=json.dumps(existing_info, ensure_ascii=False)
        )
    except KeyError as e:
        print(f"Error formateando prompt de extracción: {e}")
        entity_prompt = f"""
        Analiza el siguiente texto del usuario y extrae toda la información relevante sobre el lead.
        
        Texto del usuario: "{user_input}"
        
        Información existente del lead: {json.dumps(existing_info, ensure_ascii=False)}
        
        Responde únicamente con un objeto JSON que contenga los campos encontrados.
        """
    
    # Crear los mensajes para el LLM
    messages = [
        SystemMessage(content="Eres un asistente especializado en extraer información relevante de leads."),
        HumanMessage(content=entity_prompt)
    ]
    
    # Generar la respuesta
    response = llm.invoke(messages)
    
    try:
        # Intentar parsear la respuesta como JSON
        extracted_info = json.loads(response.content)
        return extracted_info
    except json.JSONDecodeError:
        # Si falla, intentar extraer solo la parte JSON de la respuesta
        try:
            # Buscar contenido entre corchetes que parezca JSON
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group(0))
                return extracted_info
        except:
            pass
        
        print("Error al parsear la respuesta JSON.")
        return {}