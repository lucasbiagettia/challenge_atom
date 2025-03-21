"""
Módulo para la extracción de entidades e información del lead
"""
from src.llm.model import extract_entities
from src.database.models import Lead, LeadDetails


def extract_lead_info(text, existing_lead_info=None):
    """
    Extraer información del lead del texto proporcionado
    
    Args:
        text (str): Texto del lead
        existing_lead_info (dict): Información existente del lead
        
    Returns:
        dict: Información actualizada del lead
    """
    if not text:
        return existing_lead_info or {}
    
    # Extraer entidades usando el LLM
    extracted_info = extract_entities(text, existing_lead_info)
    
    # Si no hay información existente, inicializar un diccionario vacío
    if existing_lead_info is None:
        existing_lead_info = {}
    
    # Actualizar la información existente con la nueva información
    updated_info = {**existing_lead_info}
    
    # Mapear campos específicos
    field_mapping = {
        "nombre": "name",
        "name": "name",
        "empresa": "company",
        "company": "company",
        "email": "email",
        "correo": "email",
        "teléfono": "phone",
        "telefono": "phone",
        "phone": "phone",
        "necesidades": "needs",
        "needs": "needs",
        "problemas": "needs",
        "presupuesto": "budget",
        "budget": "budget",
        "producto": "product_interest",
        "product_interest": "product_interest",
        "servicio": "product_interest",
        "plazo": "timeline",
        "timeline": "timeline",
        "tiempo": "timeline"
    }
    
    # Actualizar la información con las entidades extraídas
    for key, value in extracted_info.items():
        normalized_key = key.lower()
        if normalized_key in field_mapping and value:
            mapped_key = field_mapping[normalized_key]
            updated_info[mapped_key] = value
    
    return updated_info


def create_lead_from_info(lead_info):
    """
    Crear un objeto Lead a partir de la información extraída
    
    Args:
        lead_info (dict): Información del lead
        
    Returns:
        tuple: (Lead, LeadDetails) objetos creados
    """
    # Extraer información básica del lead
    lead_data = {
        "name": lead_info.get("name", ""),
        "company": lead_info.get("company", None),
        "email": lead_info.get("email", None),
        "phone": lead_info.get("phone", None)
    }
    
    # Crear objeto Lead
    lead = Lead(**lead_data)
    
    # Extraer detalles adicionales del lead
    details_data = {
        "lead_id": None,  # Se asignará después de crear el lead
        "budget": lead_info.get("budget", None),
        "needs": lead_info.get("needs", None),
        "product_interest": lead_info.get("product_interest", None),
        "timeline": lead_info.get("timeline", None)
    }
    
    # Crear objeto LeadDetails
    lead_details = LeadDetails(**details_data)
    
    return lead, lead_details


def update_lead_from_info(lead, lead_details, lead_info):
    """
    Actualizar objetos Lead y LeadDetails con nueva información
    
    Args:
        lead (Lead): Objeto Lead existente
        lead_details (LeadDetails): Objeto LeadDetails existente
        lead_info (dict): Nueva información del lead
        
    Returns:
        tuple: (Lead, LeadDetails) objetos actualizados
    """
    # Actualizar información básica del lead
    if "name" in lead_info and lead_info["name"]:
        lead.name = lead_info["name"]
    if "company" in lead_info and lead_info["company"]:
        lead.company = lead_info["company"]
    if "email" in lead_info and lead_info["email"]:
        lead.email = lead_info["email"]
    if "phone" in lead_info and lead_info["phone"]:
        lead.phone = lead_info["phone"]
    
    # Actualizar detalles adicionales del lead
    if "budget" in lead_info and lead_info["budget"]:
        lead_details.budget = lead_info["budget"]
    if "needs" in lead_info and lead_info["needs"]:
        lead_details.needs = lead_info["needs"]
    if "product_interest" in lead_info and lead_info["product_interest"]:
        lead_details.product_interest = lead_info["product_interest"]
    if "timeline" in lead_info and lead_info["timeline"]:
        lead_details.timeline = lead_info["timeline"]
    
    return lead, lead_details