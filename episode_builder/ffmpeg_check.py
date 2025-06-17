"""
FFmpeg presence check for runtime safety.

If FFmpeg is not found on PATH, raises a clear error pointing to README instructions.
"""

from pydub.utils import which

import warnings

def ensure_ffmpeg():
    if which("ffmpeg") is None:
        warnings.warn(
            "FFmpeg not found on PATH. Some features may be unavailable. "
            "See README.md for installation instructions.",
            RuntimeWarning
        )
        return False
    return True