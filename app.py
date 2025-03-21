import streamlit as st
import os
import time
import base64
import sys

# Asegurarnos de que la carpeta raíz del proyecto esté en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.conversation import VoiceAgent
from src.database.repository import initialize_database
from src.voice.tts import text_to_speech
from src.config import COMPANY_NAME, APP_NAME

# Crear carpeta temporal para audio si no existe
os.makedirs("temp_audio", exist_ok=True)

# Inicializar la base de datos
initialize_database()

# Configuración de la página
st.set_page_config(
    page_title=f"{APP_NAME} - {COMPANY_NAME}",
    page_icon="🤖",
    layout="wide"
)

# Función para mostrar un audio en la interfaz
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    
    audio_base64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Función para formatear el historial de conversación
def format_conversation_history(history):
    formatted = ""
    for msg in history:
        if msg["sender"] == "agent":
            formatted += f"<div style='background-color: #E8F4F8; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>AsistenteATOM:</strong> {msg['content']}</div>"
        else:
            formatted += f"<div style='background-color: #F0F0F0; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>Tú:</strong> {msg['content']}</div>"
    return formatted

# Inicializar el agente si no existe
if 'agent' not in st.session_state:
    st.session_state.agent = VoiceAgent()
    st.session_state.conversation_started = False
    st.session_state.waiting_for_input = False
    st.session_state.last_update = time.time()

# Función para iniciar una nueva conversación
def start_new_conversation():
    st.session_state.conversation_started = True
    greeting = st.session_state.agent.start_session()
    st.session_state.waiting_for_input = True
    
    # Convertir saludo a voz
    audio_file = st.session_state.agent.respond_with_voice(greeting)
    if audio_file:
        st.session_state.current_audio = audio_file
    
    st.session_state.last_update = time.time()

# Función para procesar la entrada de texto
def process_text_input():
    user_input = st.session_state.text_input
    if user_input:
        st.session_state.text_input = ""
        st.session_state.waiting_for_input = False
        
        # Procesar entrada y obtener respuesta
        response = st.session_state.agent.process_text_input(user_input)
        
        # Convertir respuesta a voz
        audio_file = st.session_state.agent.respond_with_voice(response)
        if audio_file:
            st.session_state.current_audio = audio_file
        
        st.session_state.waiting_for_input = True
        st.session_state.last_update = time.time()

# Función para procesar la entrada de voz
def process_voice_input():
    st.session_state.waiting_for_input = False
    
    # Mostrar mensaje de espera
    with st.spinner("Escuchando..."):
        # Procesar entrada de voz y obtener respuesta
        transcribed_text, response = st.session_state.agent.process_voice_input()
    
    if transcribed_text:
        # Convertir respuesta a voz
        audio_file = st.session_state.agent.respond_with_voice(response)
        if audio_file:
            st.session_state.current_audio = audio_file
    
    st.session_state.waiting_for_input = True
    st.session_state.last_update = time.time()

# Función para finalizar la conversación
def end_conversation():
    st.session_state.agent.end_session()
    st.session_state.conversation_started = False
    st.session_state.waiting_for_input = False
    st.session_state.last_update = time.time()

# Diseño de la interfaz
st.title(f"{APP_NAME}")
st.subheader(f"Un asistente virtual para {COMPANY_NAME}")

# Contenedor principal
main_container = st.container()

# Contenedor para el historial de la conversación
conversation_container = main_container.container()

# Contenedor para controles
control_container = st.container()

# Mostrar el historial de conversación
if st.session_state.conversation_started:
    conversation_history = format_conversation_history(st.session_state.agent.conversation_history)
    conversation_container.markdown(conversation_history, unsafe_allow_html=True)
    
    # Reproducir audio si hay uno disponible
    if hasattr(st.session_state, 'current_audio') and st.session_state.current_audio:
        autoplay_audio(st.session_state.current_audio)
        st.session_state.current_audio = None  # Limpiar después de reproducir

# Mostrar controles según el estado de la conversación
with control_container:
    if not st.session_state.conversation_started:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Presiona el botón para iniciar una conversación con el asistente virtual.")
        with col2:
            if st.button("Iniciar Conversación", type="primary", key="start_button"):
                start_new_conversation()
    else:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if st.session_state.waiting_for_input:
                st.text_input("Tu mensaje:", key="text_input", on_change=process_text_input)
        
        with col2:
            if st.session_state.waiting_for_input:
                if st.button("Hablar", key="voice_button"):
                    process_voice_input()
        
        with col3:
            if st.button("Finalizar", key="end_button"):
                end_conversation()

# Información del lead
if st.session_state.conversation_started:
    with st.expander("Información recopilada del lead"):
        lead_info = st.session_state.agent.get_lead_summary()
        
        if lead_info:
            st.json(lead_info)
        else:
            st.write("Aún no se ha recopilado información.")

# Pie de página
st.markdown("---")
st.caption(f"© 2025 {COMPANY_NAME} - AI Agent de Voz para Nutrición de Leads")