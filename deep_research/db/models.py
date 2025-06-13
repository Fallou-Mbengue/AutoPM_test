from sqlalchemy import Column, Integer, String, Date, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import synonym

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = 'opportunities'

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    description = Column(Text)
    deadline = Column(Date)
    publication_date = Column(Date)
    url = Column(String(1024), index=True)
    opportunity_type = Column(String(128))
    sector = Column(String(128))
    amount = Column(String(128))
    eligibility = Column(String(256))
    source = Column(String(256))
    fingerprint = Column(String(64), nullable=False, unique=True)

    link = synonym('url')

    __table_args__ = (
        UniqueConstraint('source', 'url', name='uq_opportunity_source_url'),
        UniqueConstraint('fingerprint', name='_opportunity_fingerprint_uc'),
    )