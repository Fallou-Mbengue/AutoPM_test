from pydub import AudioSegment

def concatenate_audios(audio_segments):
    """Concatenate a list of AudioSegment objects into one."""
    if not audio_segments:
        raise ValueError("No audio segments to concatenate.")
    out = audio_segments[0]
    for segment in audio_segments[1:]:
        out += segment
    return out

def export_silence(duration_ms=1000):
    """Create a silent AudioSegment of given duration."""
    return AudioSegment.silent(duration=duration_ms)