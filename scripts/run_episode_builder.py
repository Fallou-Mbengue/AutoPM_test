import os
import sys
import json
from episode_builder.builder import build_episode
from deep_research.db import database
from deep_research.db.models import Opportunity
from tts_generator.generator import TTSGenerator

# Fallback DummyTTS if TTSGenerator fails or for speed
class DummyTTS:
    def __init__(self, lang="fr"):
        self.lang = lang
    def synthesize(self, text, out_path, **kwargs):
        # Generate 1s of silence as a dummy mp3
        import wave
        import contextlib
        import struct
        with contextlib.closing(wave.open(out_path, 'w')) as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(22050)
            f.writeframes(b'\x00\x00' * 22050)
        return out_path

def get_last_opportunities(session, limit=3):
    return session.query(Opportunity).order_by(Opportunity.id.desc()).limit(limit).all()

def opportunity_to_dict(op):
    return {"id": op.id, "title": getattr(op, "title", "No title")}

def main():
    user_id = 1
    lang = "fr"
    title = "Opportunités récentes"
    date = None  # Let builder set current date if needed
    work_dir = os.environ.get("LOCAL_STATIC_DIR", "./local_static")
    os.makedirs(work_dir, exist_ok=True)

    # DB session
    session = database.get_session()

    # Fetch last 3 opportunities
    ops = get_last_opportunities(session, limit=3)
    if not ops:
        print(json.dumps({"error": "No opportunities found in database."}))
        sys.exit(1)

    opportunity_list = [opportunity_to_dict(op) for op in ops]

    # Try TTSGenerator, fallback to DummyTTS
    try:
        tts = TTSGenerator(lang=lang)
        # Optionally test with a dummy call to make sure it works
        # tts.synthesize("test", "/tmp/test.mp3")
    except Exception:
        tts = DummyTTS(lang=lang)

    # Build episode
    result = build_episode(
        user_id=user_id,
        lang=lang,
        opportunity_list=opportunity_list,
        work_dir=work_dir,
        title=title,
        date=date,
        DummyTTS=tts,
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()