import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración de la aplicación
APP_NAME = "Lead Voice Agent"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Configuración de la base de datos
DATABASE_PATH = os.getenv("DATABASE_PATH", ":memory:")  # Usar base de datos en memoria por defecto

# Configuración del modelo de lenguaje
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Configuración de la voz
ASR_MODEL = os.getenv("ASR_MODEL", "whisper-1")
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "es")  # Idioma para la síntesis de voz
AUDIO_TEMP_FOLDER = os.getenv("AUDIO_TEMP_FOLDER", "temp_audio")

# Creación de directorios temporales si no existen
os.makedirs(AUDIO_TEMP_FOLDER, exist_ok=True)

# Configuración del agente
AGENT_NAME = os.getenv("AGENT_NAME", "Asistente de Ventas")
COMPANY_NAME = os.getenv("COMPANY_NAME", "ATOM")
COMPANY_DESCRIPTION = os.getenv("COMPANY_DESCRIPTION", "Una empresa líder en soluciones tecnológicas")