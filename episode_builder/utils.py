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

def upload_to_s3(local_path, key):
    # Placeholder: in production, upload file to S3 and return public URL
    return f"https://cdn.example.com/{key}"