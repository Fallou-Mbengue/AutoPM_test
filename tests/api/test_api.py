import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, Episode, EpisodeItem
from api.main import app, get_db

# --- Use in-memory sqlite for tests ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed data: one episode for user 1
    ep = Episode(
        user_id=1,
        language="en",
        title="Latest News",
        date="2024-05-01",
        audio_url="https://example.com/audio.mp3",
        duration=360,
    )
    db.add(ep)
    db.commit()
    db.refresh(ep)
    # Add chapters/items
    items = [
        EpisodeItem(
            episode_id=ep.id,
            opportunity_id=101,
            start_time=0,
            position=1,
        ),
        EpisodeItem(
            episode_id=ep.id,
            opportunity_id=102,
            start_time=180,
            position=2,
        ),
    ]
    db.add_all(items)
    db.commit()
    yield db
    db.close()

# Override dependency for testing
app.dependency_overrides[get_db] = lambda: next(iter([pytest.lazy_fixture('db_session')]))

client = TestClient(app)

def test_get_latest_episode(monkeypatch, db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    resp = client.get("/api/v1/users/1/latest-komkom-news")
    assert resp.status_code == 200
    data = resp.json()
    assert "episode_id" in data
    assert "title" in data
    assert "podcast_url" in data
    assert "chapters_url" in data
    assert "publication_date" in data
    # Test 404
    resp = client.get("/api/v1/users/999/latest-komkom-news")
    assert resp.status_code == 404

def test_get_episode_audio(monkeypatch, db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    # Get seeded episode's ID
    ep = db_session.query(Episode).first()
    resp = client.get(f"/api/v1/episodes/{ep.id}/audio.mp3", allow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == ep.audio_url
    # Test 404
    resp = client.get("/api/v1/episodes/999/audio.mp3")
    assert resp.status_code == 404

def test_get_episode_chapters(monkeypatch, db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    ep = db_session.query(Episode).first()
    resp = client.get(f"/api/v1/episodes/{ep.id}/chapters.json")
    assert resp.status_code == 200
    chapters = resp.json()
    assert isinstance(chapters, list)
    assert len(chapters) == 2
    for chapter in chapters:
        assert "opportunity_id" in chapter
        assert "start_time" in chapter
        assert "position" in chapter
    # Test 404
    resp = client.get("/api/v1/episodes/999/chapters.json")
    assert resp.status_code == 404