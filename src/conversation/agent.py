"""
Módulo principal del agente de voz para nutrición de leads
"""
import json
from datetime import datetime
from src.llm.model import generate_response
from src.voice.asr import transcribe_audio
from src.voice.tts import text_to_speech, cleanup_audio_files
from src.conversation.intent import detect_intent
from src.conversation.entities import extract_lead_info, create_lead_from_info, update_lead_from_info
from src.database.models import Lead, LeadDetails, Conversation, Message
from src.database.repository import (
    create_lead,
    update_lead_details,
    get_lead_by_id,
    get_lead_by_email,
    start_conversation,
    end_conversation,
    add_message,
    get_conversation_messages
)


class VoiceAgent:
    """
    Agente de voz para nutrición de leads
    """
    
    def __init__(self):
        """
        Inicializar el agente de voz
        """
        self.current_lead = None
        self.lead_info = {}
        self.conversation_id = None
        self.conversation_history = []
        self.audio_files = []
    
    def start_session(self, lead_id=None):
        """
        Iniciar una sesión con un lead
        
        Args:
            lead_id (int, optional): ID del lead si ya existe
            
        Returns:
            str: Mensaje de bienvenida del agente
        """
        # Si se proporciona un ID de lead, cargar el lead existente
        if lead_id:
            self.current_lead = get_lead_by_id(lead_id)
            if self.current_lead:
                self.lead_info = {
                    "name": self.current_lead.name,
                    "company": self.current_lead.company,
                    "email": self.current_lead.email,
                    "phone": self.current_lead.phone
                }
        
        # Iniciar una nueva conversación
        if self.current_lead:
            self.conversation_id = start_conversation(self.current_lead.id)
        else:
            # Si no hay lead, crearemos uno temporal durante la conversación
            self.conversation_id = None
        
        # Limpiar el historial de conversación
        self.conversation_history = []
        
        # Generar mensaje de bienvenida
        greeting = self._generate_greeting()
        
        # Agregar mensaje a la conversación
        self._add_to_history("agent", greeting)
        
        return greeting
    
    def process_voice_input(self):
        """
        Procesar entrada de voz del usuario
        
        Returns:
            tuple: (texto_transcrito, respuesta_del_agente)
        """
        # Transcribir audio a texto
        transcribed_text = transcribe_audio()
        
        if not transcribed_text:
            response = "Lo siento, no pude entender lo que dijiste. ¿Podrías repetirlo?"
            self._add_to_history("agent", response)
            return "", response
        
        # Procesar el texto y generar respuesta
        return transcribed_text, self.process_text_input(transcribed_text)
    
    def process_text_input(self, user_input):
        """
        Procesar entrada de texto del usuario
        
        Args:
            user_input (str): Texto del usuario
            
        Returns:
            str: Respuesta del agente
        """
        # Agregar entrada del usuario al historial
        self._add_to_history("lead", user_input)
        
        # Detectar intención del usuario
        intent = detect_intent(user_input)
        
        # Extraer información del lead
        updated_lead_info = extract_lead_info(user_input, self.lead_info)
        self.lead_info = updated_lead_info
        
        # Actualizar o crear el lead en la base de datos
        self._update_lead_in_db()
        
        # Generar respuesta basada en la intención y el contexto
        response = generate_response(
            user_input,
            self.conversation_history,
            self.lead_info
        )
        
        # Agregar respuesta al historial
        self._add_to_history("agent", response)
        
        return response
    
    def respond_with_voice(self, text):
        """
        Responder al usuario con voz
        
        Args:
            text (str): Texto a convertir en voz
            
        Returns:
            str: Ruta al archivo de audio generado
        """
        audio_file = text_to_speech(text)
        if audio_file:
            self.audio_files.append(audio_file)
        return audio_file
    
    def end_session(self):
        """
        Finalizar la sesión actual
        
        Returns:
            bool: True si la sesión se cerró correctamente
        """
        # Finalizar la conversación en la base de datos
        if self.conversation_id:
            end_conversation(self.conversation_id)
        
        # Limpiar archivos de audio temporales
        cleanup_audio_files(self.audio_files)
        self.audio_files = []
        
        # Reiniciar estado del agente
        self.current_lead = None
        self.lead_info = {}
        self.conversation_id = None
        self.conversation_history = []
        
        return True
    
    def get_lead_summary(self):
        """
        Obtener un resumen de la información del lead
        
        Returns:
            dict: Resumen del lead
        """
        return self.lead_info
    
    def _generate_greeting(self):
        """
        Generar un mensaje de bienvenida para el lead
        
        Returns:
            str: Mensaje de bienvenida
        """
        if self.current_lead and self.current_lead.name:
            return f"Hola {self.current_lead.name}, soy AsistenteATOM. ¿En qué puedo ayudarte hoy con respecto a nuestros servicios de tecnología?"
        else:
            return "Hola, soy AsistenteATOM, el asistente virtual de ATOM. Estoy aquí para conocer más sobre tus necesidades tecnológicas y cómo podemos ayudarte. ¿Podrías contarme un poco sobre ti y tu empresa?"
    
    def _add_to_history(self, sender, content):
        """
        Agregar un mensaje al historial de conversación
        
        Args:
            sender (str): Remitente del mensaje ('agent' o 'lead')
            content (str): Contenido del mensaje
        """
        # Agregar al historial en memoria
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        
        # Agregar a la base de datos si hay una conversación activa
        if self.conversation_id:
            message_obj = Message(
                conversation_id=self.conversation_id,
                sender=sender,
                content=content,
                timestamp=datetime.now()
            )
            add_message(message_obj)
    
    def _update_lead_in_db(self):
        """
        Actualizar o crear el lead en la base de datos
        """
        # Si ya tenemos un lead, actualizarlo
        if self.current_lead:
            lead = self.current_lead
            lead_details = LeadDetails(lead_id=lead.id)  # Temporal, se actualizará con datos reales
            lead, lead_details = update_lead_from_info(lead, lead_details, self.lead_info)
            update_lead_details(lead_details)
        else:
            # Si hay suficiente información, crear un nuevo lead
            if "name" in self.lead_info and self.lead_info["name"]:
                # Comprobar si ya existe un lead con el mismo email
                if "email" in self.lead_info and self.lead_info["email"]:
                    existing_lead = get_lead_by_email(self.lead_info["email"])
                    if existing_lead:
                        self.current_lead = existing_lead
                        # Actualizar con la nueva información
                        self._update_lead_in_db()
                        return
                
                # Crear un nuevo lead
                lead, lead_details = create_lead_from_info(self.lead_info)
                lead_id = create_lead(lead)
                if lead_id:
                    self.current_lead = get_lead_by_id(lead_id)
                    lead_details.lead_id = lead_id
                    update_lead_details(lead_details)
                    
                    # Iniciar una conversación si no hay una activa
                    if not self.conversation_id:
                        self.conversation_id = start_conversation(lead_id)