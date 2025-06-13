import os
import tempfile
import shutil
from tts_generator.generator import TTSGenerator

def test_synthesize_gtts_monkeypatch(monkeypatch):
    # Monkeypatch gTTS to avoid real network calls
    class DummyGTTS:
        def __init__(self, text, lang):
            self.text = text
            self.lang = lang
        def save(self, filename):
            with open(filename, "wb") as f:
                f.write(b"DUMMY AUDIO CONTENT")

    import tts_generator.generator as tts_gen_mod
    monkeypatch.setattr(tts_gen_mod, "gTTS", DummyGTTS)

    temp_dir = tempfile.mkdtemp()
    try:
        generator = TTSGenerator(output_dir=temp_dir)
        text = "Bonjour le monde"
        lang = "fr"
        file_path = generator.synthesize(text, lang, output_dir=temp_dir)
        assert os.path.exists(file_path), "Audio file was not created"
        with open(file_path, "rb") as f:
            content = f.read()
            assert content == b"DUMMY AUDIO CONTENT"
    finally:
        shutil.rmtree(temp_dir)

def test_synthesize_wolof_coqui_monkeypatch(monkeypatch):
    # Monkeypatch TTS (Coqui) to avoid real model loading and audio generation
    class DummyTTS:
        def __init__(self, model_name):
            self.model_name = model_name
        def tts_to_file(self, text, speaker_wav, language, file_path):
            with open(file_path, "wb") as f:
                f.write(b"WOLOF COQUI DUMMY AUDIO")

    # Patch TTS import in generator
    import sys
    import types
    dummy_tts_module = types.SimpleNamespace(api=types.SimpleNamespace(TTS=DummyTTS))
    sys.modules["TTS"] = dummy_tts_module
    sys.modules["TTS.api"] = types.SimpleNamespace(TTS=DummyTTS)

    # Patch WOLOF_MODEL config to a dummy value
    monkeypatch.setattr("tts_generator.config.WOLOF_MODEL", "dummy_model")

    temp_dir = tempfile.mkdtemp()
    try:
        generator = TTSGenerator(output_dir=temp_dir)
        text = "Jaam nga am"
        lang = "wo"
        file_path = generator.synthesize(text, lang, output_dir=temp_dir)
        assert os.path.exists(file_path), "Audio file was not created"
        with open(file_path, "rb") as f:
            content = f.read()
            assert content == b"WOLOF COQUI DUMMY AUDIO"
    finally:
        shutil.rmtree(temp_dir)