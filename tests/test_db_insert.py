import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from deep_research.db.models import Base, Opportunity
from deep_research.komkom_scraper.pipelines import PostgresPipeline

@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite for test
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_postgres_pipeline_insert(monkeypatch, db_session):
    pipeline = PostgresPipeline()
    # Patch get_session and get_engine
    monkeypatch.setattr("deep_research.komkom_scraper.pipelines.get_session", lambda: lambda: db_session)
    monkeypatch.setattr("deep_research.komkom_scraper.pipelines.get_engine", lambda: db_session.get_bind())
    pipeline.open_spider(None)

    item = {
        "title": "Grant X",
        "description": "Funding for X",
        "deadline": "2023-12-31",
        "link": "https://example.com/a",
        "opportunity_type": "Grant",
        "sector": "Science",
        "amount": "$1000",
        "eligibility": "Researchers",
        "source": "https://example.com",
        "fingerprint": "abc123"
    }
    # Should not raise
    pipeline.process_item(item, None)
    # Check in DB
    result = db_session.query(Opportunity).filter_by(fingerprint="abc123").first()
    assert result is not None
    assert result.title == "Grant X"

def test_postgres_pipeline_duplicate(monkeypatch, db_session):
    pipeline = PostgresPipeline()
    monkeypatch.setattr("deep_research.komkom_scraper.pipelines.get_session", lambda: lambda: db_session)
    monkeypatch.setattr("deep_research.komkom_scraper.pipelines.get_engine", lambda: db_session.get_bind())
    pipeline.open_spider(None)

    item = {
        "title": "Grant X",
        "description": "Funding for X",
        "deadline": "2023-12-31",
        "link": "https://example.com/a",
        "opportunity_type": "Grant",
        "sector": "Science",
        "amount": "$1000",
        "eligibility": "Researchers",
        "source": "https://example.com",
        "fingerprint": "abc123"
    }
    pipeline.process_item(item, None)
    with pytest.raises(Exception):
        pipeline.process_item(item, None)