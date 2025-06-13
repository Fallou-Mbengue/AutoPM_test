import os
import uuid
import logging

from gtts import gTTS
from .config import DEFAULT_OUTPUT_DIR, SUPPORTED_LANGS, WOLOF_MODEL

class TTSGenerator:
    def __init__(self, output_dir=DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.wolof_tts = None
        # Try to load Coqui TTS for Wolof only once
        try:
            from TTS.api import TTS
            self.wolof_tts = TTS(WOLOF_MODEL)
        except Exception as e:
            logging.warning(f"Could not load Wolof TTS model ({WOLOF_MODEL}): {e}. Will fallback to gTTS for Wolof.")

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
            if self.wolof_tts is not None:
                try:
                    # XTTS v2 expects language code like 'wol'
                    self.wolof_tts.tts_to_file(
                        text=text,
                        speaker_wav=None,
                        language="wol",
                        file_path=file_path
                    )
                except Exception as e:
                    logging.warning(
                        f"Failed to synthesize Wolof with Coqui TTS: {e}. Falling back to gTTS (fr)."
                    )
                    tts = gTTS(text=text, lang='fr')
                    tts.save(file_path)
            else:
                logging.warning(
                    "Wolof (wo) TTS model not available. Falling back to gTTS (fr)."
                )
                tts = gTTS(text=text, lang='fr')
                tts.save(file_path)
        else:
            raise ValueError(f"Unsupported language code: {lang}")

        return file_path