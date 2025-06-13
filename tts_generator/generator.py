import os
import uuid
import logging

from gtts import gTTS
from .config import DEFAULT_OUTPUT_DIR, SUPPORTED_LANGS

class TTSGenerator:
    def __init__(self, output_dir=DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def synthesize(self, text, lang, output_dir=None, filename_prefix=None):
        """Synthesize speech from text and save to file.

        Args:
            text (str): The text to be synthesized.
            lang (str): The language code ('fr', 'wo').
            output_dir (str, optional): Output directory for the audio file.
            filename_prefix (str, optional): Prefix for the audio filename.

        Returns:
            str: Path to the generated audio file.
        """
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)

        unique_id = uuid.uuid4().hex
        prefix = f"{filename_prefix}_" if filename_prefix else ""
        ext = "mp3"
        # Tag filename with '_wo' for wolof for clarity.
        tag = f"_{lang}" if lang == "wo" else f"_{lang}"
        filename = f"{prefix}{unique_id}{tag}.{ext}"
        file_path = os.path.join(output_dir, filename)

        if lang == "fr":
            tts = gTTS(text=text, lang='fr')
            tts.save(file_path)
        elif lang == "wo":
            # Wolof not supported by Google, fallback to French with a warning.
            logging.warning(
                "Wolof (wo) is not supported by gTTS. Using French as fallback. "
                "TODO: Integrate real Wolof TTS model when available."
            )
            tts = gTTS(text=text, lang='fr')
            tts.save(file_path)
            # TODO: Integrate real Wolof TTS (e.g., using TTS library or custom model).
        else:
            raise ValueError(f"Unsupported language code: {lang}")

        return file_path