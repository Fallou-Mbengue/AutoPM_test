import hashlib
import re
from datetime import datetime

from deep_research.db import database, models

class NormalizationPipeline:
    @staticmethod
    def clean_text(text):
        if not text:
            return None
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def parse_date(date_str):
        if not date_str:
            return None
        # Try various date formats, including long-form English dates
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%B %d, %Y",  # e.g. May 10, 2024
            "%d %B %Y",   # e.g. 10 May 2024
        ]
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except Exception:
                continue
        return None

    @staticmethod
    def fingerprint_item(item):
        # Use title+link or all fields as a fingerprint base
        base = (item.get('title') or "") + "|" + (item.get('link') or "")
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def process_item(self, item, spider):
        # Clean/normalize fields
        for field in ["title", "description", "eligibility"]:
            item[field] = self.clean_text(item.get(field))
        for date_field in ["deadline", "publication_date"]:
            item[date_field] = self.parse_date(item.get(date_field))
        # Set fingerprint
        item["fingerprint"] = self.fingerprint_item(item)
        return item

class PostgresPipeline:
    def open_spider(self, spider):
        self.Session = database.get_session()
        self.engine = database.get_engine()
        models.Base.metadata.create_all(self.engine)

    def process_item(self, item, spider):
        session = self.Session()
        try:
            fingerprint = item.get("fingerprint")
            # Check for duplicate
            exists = session.query(models.Opportunity).filter_by(fingerprint=fingerprint).first()
            if exists:
                raise Exception("Duplicate item detected (fingerprint)")
            opp = models.Opportunity(
                title=item.get("title"),
                description=item.get("description"),
                deadline=item.get("deadline"),
                publication_date=item.get("publication_date"),
                url=item.get("link"),
                opportunity_type=item.get("opportunity_type"),
                sector=item.get("sector"),
                amount=item.get("amount"),
                eligibility=item.get("eligibility"),
                source=item.get("source"),
                fingerprint=fingerprint,
            )
            session.add(opp)
            session.commit()
            return item
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()