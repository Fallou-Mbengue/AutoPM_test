"""
FFmpeg presence check for runtime safety.

If FFmpeg is not found on PATH, raises a clear error pointing to README instructions.
"""

from pydub.utils import which

def ensure_ffmpeg():
    if which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg not found on PATH. Please install it to use the episode builder. "
            "See README.md for instructions (brew/apt/choco/download)."
        )

# Run check at import so any script importing builder.py gets the check for free
ensure_ffmpeg()