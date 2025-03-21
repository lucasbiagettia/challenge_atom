import os
import time
import tempfile
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from src.config import TTS_LANGUAGE, AUDIO_TEMP_FOLDER


def text_to_speech(text, language=TTS_LANGUAGE, play_audio=True):
    """
    Convertir texto a voz usando gTTS
    
    Args:
        text (str): Texto a convertir a voz
        language (str): Idioma para la síntesis de voz
        play_audio (bool): Indica si se debe reproducir el audio generado
        
    Returns:
        str: Ruta al archivo de audio generado o None si hay error
    """
    if not text:
        return None
    
    try:
        # Crear un archivo temporal para el audio
        audio_file = os.path.join(AUDIO_TEMP_FOLDER, f"speech_{int(time.time())}.mp3")
        
        # Generar la voz
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(audio_file)
        
        # Reproducir el audio si se solicita
        if play_audio:
            audio = AudioSegment.from_mp3(audio_file)
            play(audio)
        
        return audio_file
    except Exception as e:
        print(f"Error en la síntesis de voz: {e}")
        return None


def text_to_speech_stream(text_chunks, language=TTS_LANGUAGE):
    """
    Transmitir chunks de texto a voz para respuestas largas
    
    Args:
        text_chunks (list): Lista de fragmentos de texto
        language (str): Idioma para la síntesis de voz
        
    Returns:
        list: Lista de rutas a los archivos de audio generados
    """
    audio_files = []
    
    for chunk in text_chunks:
        audio_file = text_to_speech(chunk, language, play_audio=True)
        if audio_file:
            audio_files.append(audio_file)
    
    return audio_files


def cleanup_audio_files(audio_files):
    """
    Limpiar archivos de audio temporales
    
    Args:
        audio_files (list): Lista de rutas a archivos de audio
    """
    for file in audio_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Error al eliminar archivo de audio: {e}")