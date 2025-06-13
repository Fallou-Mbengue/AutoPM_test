# AutoPM_test
Test auto pm cosine 

## Text-to-Speech (TTS) Integration

This project supports TTS for French and Wolof using Google gTTS and [Coqui TTS](https://github.com/coqui-ai/TTS) (XTTS v2 multilingual model).

### Requirements

- Python 3.8+
- [TTS (Coqui)](https://github.com/coqui-ai/TTS) with XTTS v2:  
  Install dependencies from `requirements.txt`:
  ```
  pip install -r requirements.txt
  ```
  This will install `TTS[all]` and `torch`.

### Wolof Model

By default, the system uses the open-source multilingual model `tts_models/multilingual/xtts_v2` for Wolof voice synthesis.  
To use a custom or community Wolof model (e.g., `galsenai/xtts_v2_wolof`), set the environment variable before running:

```bash
export WOLOF_MODEL="galsenai/xtts_v2_wolof"
```

### Usage

- For French (`lang='fr'`), Google gTTS is used.
- For Wolof (`lang='wo'`), Coqui TTS is used if available and properly installed. If not, the system falls back to French TTS with a warning. 
