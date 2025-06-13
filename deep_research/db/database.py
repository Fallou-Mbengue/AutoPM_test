import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_db_url():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    db = os.getenv("DB_NAME", "komkom_db")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

_engine = None
_Session = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_db_url()
        _engine = create_engine(db_url)
    return _engine

def get_session():
    global _Session
    if _Session is None:
        engine = get_engine()
        _Session = sessionmaker(bind=engine)
    return _Session