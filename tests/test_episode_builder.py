import os
import tempfile
import pytest
from pydub import AudioSegment
from episode_builder.builder import EpisodeBuilder

class DummyTTSGenerator:
    def synthesize(self, text, lang):
        # Create a short silent mp3 file and return its path
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        AudioSegment.silent(duration=300).export(path, format="mp3")
        return path

@pytest.fixture
def dummy_tts():
    return DummyTTSGenerator()

def test_episode_builder_returns_chapter_json_path(dummy_tts, tmp_path):
    builder = EpisodeBuilder(tts_generator=dummy_tts, work_dir=tmp_path)
    chapters = [
        {"title": "Chapitre 1", "text": "Ceci est le texte du chapitre 1.", "lang": "fr"},
        {"title": "Kàddu 2", "text": "Li ci ci kàddu 2 la.", "lang": "wo"}
    ]
    episode_title = "Titre de l'épisode"
    json_path = builder.build_episode(episode_title, chapters)
    assert os.path.exists(json_path)
    # Load and check structure
    import json
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert all("audio_path" in ch for ch in data)
    # Check that episode.mp3 also exists
    assert (tmp_path / "episode.mp3").exists()