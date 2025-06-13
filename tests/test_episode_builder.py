import os
import tempfile
from episode_builder import builder
import pytest

class DummyTTS:
    def synthesize(self, text):
        # Generates 1 second of silence as fake audio
        from pydub import AudioSegment
        return AudioSegment.silent(duration=1000)

def test_build_episode(monkeypatch):
    # Monkeypatch upload_to_s3 to return the local path
    monkeypatch.setattr(
        "episode_builder.utils.upload_to_s3",
        lambda local_path, key: local_path,
    )

    user_id = 1
    lang = "en"
    opportunity_list = [{"id": 101, "title": "Test News"}]
    title = "Test Episode"
    date = "2024-01-01"
    with tempfile.TemporaryDirectory() as work_dir:
        result = builder.build_episode(
            user_id=user_id,
            lang=lang,
            opportunity_list=opportunity_list,
            work_dir=work_dir,
            title=title,
            date=date,
            background_music_path=None,
            DummyTTS=DummyTTS,
        )
        assert os.path.exists(result["mp3_url"])
        assert os.path.exists(result["hls_url"])
        assert result["duration"] > 0