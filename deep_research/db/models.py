from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = 'opportunities'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    deadline = Column(Date)
    publication_date = Column(Date)
    opportunity_type = Column(String)
    eligibility = Column(Text)
    link = Column(String)
    source = Column(String), UniqueConstraint

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    description = Column(Text)
    deadline = Column(Date)
    link = Column(String(1024))
    opportunity_type = Column(String(128))
    sector = Column(String(128))
    amount = Column(String(128))
    eligibility = Column(String(256))
    source = Column(String(256))
    fingerprint = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint('fingerprint', name='_opportunity_fingerprint_uc'),
    )