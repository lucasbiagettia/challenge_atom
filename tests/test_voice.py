import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Asegurar que la raíz del proyecto esté en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice.asr import transcribe_audio, transcribe_with_whisper, record_audio
from src.voice.tts import text_to_speech, text_to_speech_stream, cleanup_audio_files


@pytest.fixture
def mock_speech_recognition():
    """Fixture para simular reconocimiento de voz"""
    with patch('src.voice.asr.sr.Recognizer') as mock_recognizer, \
         patch('src.voice.asr.sr.Microphone') as mock_microphone:
        
        # Configurar los mocks
        mock_instance = MagicMock()
        mock_recognizer.return_value = mock_instance
        
        mock_audio = MagicMock()
        mock_audio.get_wav_data.return_value = b'dummy_audio_data'
        mock_instance.listen.return_value = mock_audio
        
        yield {
            "recognizer": mock_recognizer,
            "microphone": mock_microphone,
            "instance": mock_instance
        }


@pytest.fixture
def mock_openai_whisper():
    """Fixture para simular la transcripción con Whisper"""
    with patch('src.voice.asr.client.audio.transcriptions.create') as mock_whisper:
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.text = "Texto transcrito de prueba"
        mock_whisper.return_value = mock_response
        
        yield mock_whisper


@pytest.fixture
def mock_gtts():
    """Fixture para simular la síntesis de voz con gTTS"""
    with patch('src.voice.tts.gTTS') as mock_gtts, \
         patch('src.voice.tts.AudioSegment.from_mp3') as mock_audio, \
         patch('src.voice.tts.play') as mock_play, \
         patch('builtins.open', mock_open()):
        
        # Configurar los mocks
        mock_instance = MagicMock()
        mock_gtts.return_value = mock_instance
        
        mock_audio_segment = MagicMock()
        mock_audio.return_value = mock_audio_segment
        
        yield {
            "gtts": mock_gtts,
            "audio": mock_audio,
            "play": mock_play
        }


def test_record_audio(mock_speech_recognition):
    """Probar la grabación de audio"""
    # Simular la apertura de archivo con mock_open
    with patch('builtins.open', mock_open()) as mock_file:
        # Llamar a la función
        audio_file = record_audio(timeout=3)
        
        # Verificar que se h