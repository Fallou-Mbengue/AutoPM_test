# Configuration for TTSGenerator
import os

DEFAULT_OUTPUT_DIR = "audio_output"
SUPPORTED_LANGS = ["fr", "wo"]

# Environment variable for Wolof TTS model (Coqui TTS/XTTS v2)
WOLOF_MODEL = os.getenv("WOLOF_MODEL", "tts_models/multilingual/xtts_v2")