# Episode Builder

## Usage

The Episode Builder constructs audio episodes from a list of opportunities/news items, generating both MP3 and HLS audio, optionally overlaying background music, and uploading the episode to S3/CDN.

### Example

```python
from episode_builder.builder import build_episode

result = build_episode(
    user_id=123,
    lang="en",
    opportunity_list=[{"id": 1, "title": "Sample news"}],
    work_dir="/tmp/episode_build",
    title="Today's News",
    date="2024-01-01",
    background_music_path="/path/to/music.mp3",  # Optional
    DummyTTS=DummyTTS,  # Provide your TTS implementation
)
print(result["mp3_url"])
print(result["hls_url"])
```

### Environment

- To use background music, set the `background_music_path` argument to a valid audio file path.
- Requires ffmpeg installed and available on PATH for HLS segmenting.

### Dependencies

Install requirements with:

```
pip install -r requirements.txt
```

- `ffmpeg-python` and `boto3` are required for export and upload functionality.
- Requires a database with the models defined in `db/models.py`.

### Testing

Tests are located in `tests/test_episode_builder.py` and use dummy TTS and S3 upload functions.