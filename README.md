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

#### Local End-to-End Testing (No AWS S3)

To test locally without using real S3, you can use the `LOCAL_STATIC_DIR` environment variable.

- **How it works:**  
  When `LOCAL_STATIC_DIR` is set, episode audio and other uploaded files are copied into this directory instead of being uploaded to S3.  
  The FastAPI app will automatically serve this directory at `/static`, so returned URLs will look like `http://127.0.0.1:8000/static/{key}`.

- **Setup example:**
  ```sh
  export LOCAL_STATIC_DIR=./local_static
  mkdir -p ./local_static
  uvicorn api.main:app --reload
  ```

- **Notes:**
  - Make sure `LOCAL_STATIC_DIR` exists and is writable.
  - The S3 upload code is bypassed; production is not affected when `LOCAL_STATIC_DIR` is unset.
  - Access generated episodes and files via URLs like `http://127.0.0.1:8000/static/{key}`.

- **To revert to S3/CDN uploads:**  
  Unset the `LOCAL_STATIC_DIR` variable (`unset LOCAL_STATIC_DIR` or close your shell).

---

### Test the full local pipeline

You can run a full local end-to-end test (DB setup, spider, episode builder) using the provided script:

```sh
bash scripts/run_local_e2e.sh
```

This will:
- Ensure environment variables for DB and static directory are set (or will set defaults)
- Create tables in the database
- Run the opportunity spider (if `scrapy` is installed)
- Build a demo episode for user 1 (lang=fr) using the latest scraped opportunities
- Show the resulting MP3 path

**For full local testing, in one terminal:**
```sh
bash scripts/run_local_e2e.sh
```

**And in another terminal, start the API and frontend:**
```sh
uvicorn api.main:app --reload
npm start
```

# Deployment

## FastAPI Backend Dockerization

A `Dockerfile` is available at the project root for containerizing the FastAPI backend.  
**Build and run:**
```sh
docker build -t my-fastapi-app .
docker run -p 8000:8000 my-fastapi-app
```

## AWS ECR Deployment

A sample deployment script for AWS ECR is provided at `deploy/ecr_push.sh`.  
Edit the placeholders with your AWS account, region, and repository information.

## Frontend Static Deployment

The frontend supports static deployment via Netlify.  
A `netlify.toml` is provided in the `frontend/` directory:

- **Build command:** `npm run build`
- **Publish directory:** `build`