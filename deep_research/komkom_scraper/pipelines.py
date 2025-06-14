import re
import hashlib
from datetime import datetime
import scrapy
from sqlalchemy.exc import IntegrityError
from deep_research.db.database import get_session, get_engine
from deep_research.db.models import Opportunity
from deep_research.komkom_scraper.items import OpportunityItem

from bs4 import BeautifulSoup  # Added missing import

class NormalizationPipeline:
    def process_item(self, item, spider):
        # Only process OpportunityItem
        if isinstance(item, OpportunityItem):
            # Parse and normalize deadline
            if "deadline" in item and item["deadline"]:
                item["deadline"] = self.parse_date(item["deadline"])
            else:
                item["deadline"] = None
            # Parse and normalize publication_date
            if "publication_date" in item and item["publication_date"]:
                item["publication_date"] = self.parse_date(item["publication_date"])
            else:
                item["publication_date"] = None
            # Clean description and eligibility fields
            if "description" in item and item["description"]:
                item["description"] = self.clean_text(item["description"])
            if "eligibility" in item and item["eligibility"]:
                item["eligibility"] = self.clean_text(item["eligibility"])
            # Ensure sector and amount are present (set to None if missing)
            item["sector"] = item.get("sector", None)
            item["amount"] = item.get("amount", None)
            # Compute and attach fingerprint for deduplication
            item["fingerprint"] = self.fingerprint_item(item)
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
        # If timestamp-like input
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
            sector=item.get('sector', None),
            amount=item.get('amount', None),
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