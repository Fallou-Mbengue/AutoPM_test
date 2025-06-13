"""
FastAPI app for KomKom News API.

Run locally:
    uvicorn api.main:app --reload

Requirements:
    pip install -r requirements.txt
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import boto3

from db.models import Episode, EpisodeItem
from deep_research.db.database import get_session

# --- CORS Middleware (open; TODO: restrict origins) ---
app = FastAPI(
    title="KomKom News API",
    version="1.0.0",
    description="API for personalized KomKom news podcast episodes.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency: SQLAlchemy session ---
def get_db():
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error (SQLAlchemy)"},
    )

# --- Response Models ---
class LatestEpisodeResponse(BaseModel):
    episode_id: int
    title: str
    podcast_url: str
    chapters_url: str
    publication_date: str  # ISO

class ChapterItem(BaseModel):
    opportunity_id: int
    start_time: int
    position: int

# --- Endpoint: GET /api/v1/users/{user_id}/latest-komkom-news ---
@app.get("/api/v1/users/{user_id}/latest-komkom-news", response_model=LatestEpisodeResponse, tags=["Episodes"])
def get_latest_episode(user_id: int, db: Session = Depends(get_db)):
    ep = (
        db.query(Episode)
        .filter(Episode.user_id == user_id)
        .order_by(Episode.date.desc(), Episode.created_at.desc())
        .first()
    )
    if not ep:
        raise HTTPException(status_code=404, detail="No episode found for this user.")
    chapters_url = f"/api/v1/episodes/{ep.id}/chapters.json"
    # TODO: if S3 presign available, use it.
    return LatestEpisodeResponse(
        episode_id=ep.id,
        title=ep.title,
        podcast_url=ep.audio_url,
        chapters_url=chapters_url,
        publication_date=ep.date.isoformat(),
    )

# --- Endpoint: GET /api/v1/episodes/{episode_id}/audio.mp3 ---
@app.get("/api/v1/episodes/{episode_id}/audio.mp3", tags=["Episodes"])
def get_episode_audio(episode_id: int, db: Session = Depends(get_db)):
    ep = db.query(Episode).filter(Episode.id == episode_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found.")
    # Check for PRESIGN_S3 env
    presign = os.getenv("PRESIGN_S3", "0") == "1"
    if presign and ep.audio_url.startswith("s3://"):
        # S3 presign logic
        s3_url = ep.audio_url
        # s3://bucket/key
        try:
            _, bucket, *key_parts = s3_url.split("/")
            key = "/".join(key_parts)
            client = boto3.client("s3")
            presigned_url = client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=3600,
            )
            return RedirectResponse(url=presigned_url, status_code=307)
        except Exception:
            raise HTTPException(status_code=500, detail="Could not generate presigned S3 URL.")
    return RedirectResponse(url=ep.audio_url, status_code=307)

# --- Endpoint: GET /api/v1/episodes/{episode_id}/chapters.json ---
@app.get("/api/v1/episodes/{episode_id}/chapters.json", response_model=List[ChapterItem], tags=["Episodes"])
def get_episode_chapters(episode_id: int, db: Session = Depends(get_db)):
    ep = db.query(Episode).filter(Episode.id == episode_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found.")
    items = (
        db.query(EpisodeItem)
        .filter(EpisodeItem.episode_id == episode_id)
        .order_by(EpisodeItem.position.asc())
        .all()
    )
    return [
        ChapterItem(
            opportunity_id=item.opportunity_id,
            start_time=item.start_time,
            position=item.position,
        )
        for item in items
    ]

# --- Placeholder: Authentication Header (TODO) ---
# For future endpoints, check for Authorization header, e.g.:
# auth = request.headers.get("Authorization")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)