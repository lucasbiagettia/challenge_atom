# AI Agent de Voz para Nutrición de Leads

Este proyecto implementa un agente de voz basado en inteligencia artificial diseñado para interactuar con prospectos (leads), recopilar información relevante y nutrir la relación con ellos a través de una conversación natural y fluida.

## Descripción del Proyecto

El asistente virtual permite:
- Interactuar con prospectos a través de voz para recopilar información relevante
- Gestionar y analizar datos de los leads para mejorar la segmentación
- Manejar entradas en lenguaje natural, identificando información clave
- Mantener el contexto en conversaciones de múltiples turnos
- Almacenar la información recopilada en una base de datos

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal
- **LangChain**: Framework para orquestación de modelos de lenguaje
- **OpenAI**: Modelos GPT para procesamiento de lenguaje natural
- **Whisper**: Reconocimiento de voz (ASR)
- **gTTS**: Síntesis de voz (TTS)
- **SQLite**: Base de datos para almacenamiento de leads
- **Streamlit**: Interfaz de usuario web

## Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI y API Key
- Micrófono y altavoces para interacción por voz
- Dependencias del sistema para PyAudio:
  - En Ubuntu/Debian: `sudo apt-get install python3-dev portaudio19-dev`
  - En macOS: `brew install portaudio`
  - En Manjaro/Arch: `sudo pacman -Sy portaudio python-pip gcc`

## Instalación

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno:
   - Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
     ```
     OPENAI_API_KEY=tu_clave_api_de_openai
     LLM_MODEL_NAME=gpt-4o-mini
     TTS_LANGUAGE=es
     ```

## Ejecución

Para iniciar la aplicación:
```bash
streamlit run app.py
```

La interfaz web se abrirá en tu navegador (generalmente en http://localhost:8501).



## Funcionalidades

1. **Interacción por voz y texto**:
   - Reconocimiento de voz utilizando Whisper de OpenAI
   - Síntesis de voz con gTTS (Google Text-to-Speech)
   - Entrada de texto para conversaciones híbridas

2. **Procesamiento de lenguaje natural**:
   - Detección de intenciones del usuario
   - Extracción de entidades e información relevante
   - Generación de respuestas contextuales

3. **Gestión de datos de leads**:
   - Almacenamiento en SQLite
   - Actualización en tiempo real de la información
   - Seguimiento de conversaciones

4. **Interfaz de usuario**:
   - Panel principal de conversación
   - Visualización de información recopilada
   - Controles para interacción por voz y texto

## Tests

Para ejecutar las pruebas unitarias:
```bash
pytest
```

## Funcionalidades futuras

- Implementación de autenticación para acceso a diferentes perfiles de agentes
- Integración con CRMs populares (Salesforce, HubSpot, etc.)
- Personalización del asistente según preferencias de usuario
- Análisis de sentimientos para adaptar respuestas
- Soporte para múltiples idiomas

## Licencia

[MIT](LICENSE)

