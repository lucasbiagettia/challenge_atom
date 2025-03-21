import os
import time
import tempfile
import speech_recognition as sr
from openai import OpenAI
from src.config import OPENAI_API_KEY, ASR_MODEL, AUDIO_TEMP_FOLDER

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


def record_audio(timeout=5):
    """
    Grabar audio del micrófono
    
    Args:
        timeout (int): Tiempo máximo de grabación en segundos
        
    Returns:
        bytes: Datos de audio grabados o None si hay error
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
            
        # Guardar el audio en un archivo temporal
        temp_file = os.path.join(AUDIO_TEMP_FOLDER, f"recording_{int(time.time())}.wav")
        with open(temp_file, "wb") as f:
            f.write(audio.get_wav_data())
            
        return temp_file
    except Exception as e:
        print(f"Error al grabar audio: {e}")
        return None


def transcribe_with_whisper(audio_file_path):
    """
    Transcribir audio usando OpenAI Whisper
    
    Args:
        audio_file_path (str): Ruta al archivo de audio
        
    Returns:
        str: Texto transcrito o cadena vacía si hay error
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=ASR_MODEL,
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        print(f"Error al transcribir con Whisper: {e}")
        return ""


def transcribe_audio():
    """
    Función principal para grabar y transcribir audio
    
    Returns:
        str: Texto transcrito del audio o cadena vacía si hay error
    """
    audio_file = record_audio()
    if audio_file:
        text = transcribe_with_whisper(audio_file)
        # Limpiar el archivo temporal
        try:
            os.remove(audio_file)
        except:
            pass
        return text
    return ""


# Función para usar en pruebas o cuando se tiene un archivo de audio existente
def transcribe_from_file(audio_file_path):
    """
    Transcribir desde un archivo de audio existente
    
    Args:
        audio_file_path (str): Ruta al archivo de audio
        
    Returns:
        str: Texto transcrito o cadena vacía si hay error
    """
    if os.path.exists(audio_file_path):
        return transcribe_with_whisper(audio_file_path)
    return ""