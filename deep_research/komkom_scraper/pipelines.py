import re
import hashlib
from datetime import datetime
import scrapy
from sqlalchemy.exc import IntegrityError
from deep_research.db.database import get_session, get_engine
from deep_research.db.models import Opportunity
from deep_research.komkom_scraper.items import OpportunityItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

def parse_date(date_str):
    # Implement parsing logic for various date formats
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            continue
    return None

class NormalizationPipeline:
    def process_item(self, item, spider):
        if isinstance(item, OpportunityItem):
            if "deadline" in item and item["deadline"]:
                item["deadline"] = parse_date(item["deadline"])
            if "publication_date" in item and item["publication_date"]:
                item["publication_date"] = parse_date(item["publication_date"])
        return item

    @staticmethod
    def clean_text(text):
        if not text:
            return ""
        # Remove HTML tags and normalize whitespace
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @staticmethod
    def parse_date(date_str):
        if not date_str:
            return None
        # Try multiple formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except Exception:
                continue
        # If timestamp
        try:
            ts = float(date_str)
            return datetime.fromtimestamp(ts).date()
        except Exception:
            pass
        return None

    @staticmethod
    def fingerprint_item(item):
        # Use title + deadline + link for deduplication
        s = f"{item.get('title', '')}|{item.get('deadline', '')}|{item.get('link', '')}"
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

class PostgresPipeline:
    def open_spider(self, spider):
        self.session = get_session()()
        self.engine = get_engine()
        self.seen_fingerprints = set()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        fingerprint = item.get('fingerprint')
        if not fingerprint:
            return item
        # Check for duplicates in-memory (current batch)
        if fingerprint in self.seen_fingerprints:
            raise scrapy.exceptions.DropItem("Duplicate item found (in batch).")
        self.seen_fingerprints.add(fingerprint)
        # Check for duplicates in DB
        exists = self.session.query(Opportunity).filter_by(fingerprint=fingerprint).first()
        if exists:
            raise scrapy.exceptions.DropItem("Duplicate item found (in database).")
        db_obj = Opportunity(
            title=item.get('title'),
            description=item.get('description'),
            deadline=item.get('deadline'),
            link=item.get('link'),
            opportunity_type=item.get('opportunity_type'),
            sector=item.get('sector'),
            amount=item.get('amount'),
            eligibility=item.get('eligibility'),
            source=item.get('source'),
            fingerprint=fingerprint
        )
        self.session.add(db_obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise scrapy.exceptions.DropItem("Duplicate item found (unique constraint).")
        return item