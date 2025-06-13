from pydub.effects import normalize

def normalize_audio(audio_segment, target_dbfs=-18):
    normalized = normalize(audio_segment)
    change_in_dBFS = target_dbfs - normalized.dBFS
    return normalized.apply_gain(change_in_dBFS)

def overlay_background(base_audio, bg_audio, bg_volume=-25):
    # Adjust background music volume
    bg_audio = bg_audio - abs(bg_volume)
    # Loop bg_audio to match base_audio length
    loops = int(len(base_audio) / len(bg_audio)) + 1
    bg_audio = bg_audio * loops
    bg_audio = bg_audio[:len(base_audio)]
    # Overlay
    return base_audio.overlay(bg_audio)

import os
import shutil

def upload_to_s3(local_path, key):
    """
    Uploads a file to S3 (production) or to a local static directory for local testing.

    If the environment variable LOCAL_STATIC_DIR is set, copies the file to that directory
    and returns a local static URL (for FastAPI local static serving).
    Otherwise, uses the original S3 placeholder logic.
    """
    local_static_dir = os.getenv("LOCAL_STATIC_DIR")
    if local_static_dir:
        # Ensure target subdirectory exists
        target_path = os.path.join(local_static_dir, key)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(local_path, target_path)
        # Return a URL pointing to the FastAPI static mount (assume localhost:8000)
        return f"http://127.0.0.1:8000/static/{key}"
    # Placeholder: in production, upload file to S3 and return public URL
    return f"https://cdn.example.com/{key}"