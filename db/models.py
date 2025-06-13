from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Episode(Base):
    __tablename__ = 'episodes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    language = Column(String(2), nullable=False)
    title = Column(String(256), nullable=False)
    date = Column(Date, nullable=False)
    audio_url = Column(String(1024), nullable=False)
    duration = Column(Integer, nullable=False)  # seconds
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("EpisodeItem", back_populates="episode")

class EpisodeItem(Base):
    __tablename__ = 'episode_items'
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'), nullable=False)
    opportunity_id = Column(Integer, nullable=False)
    start_time = Column(Integer, nullable=False)  # seconds
    position = Column(Integer, nullable=False)

    episode = relationship("Episode", back_populates="items")