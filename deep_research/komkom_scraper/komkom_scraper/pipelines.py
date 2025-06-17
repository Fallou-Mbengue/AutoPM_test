import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from deep_research.db import database, models

class NormalizationPipeline:
    @staticmethod
    def canonicalize_url(url: str) -> str | None:
        if not url:
            return url
        try:
            parts = urlparse(url)
            scheme = (parts.scheme or '').lower()
            netloc = parts.netloc
            if netloc:
                # Remove leading www.
                if netloc.lower().startswith('www.'):
                    netloc = netloc[4:]
                # Lower only host part, keep port as is
                # netloc could be user:pass@host:port
                # We'll split by '@' and ':'
                userinfo, _, hostport = netloc.rpartition('@')
                if hostport == '':
                    hostport = userinfo
                    userinfo = ''
                # Split host and (optional) port
                if ':' in hostport:
                    host, port = hostport.split(':', 1)
                    host = host.lower()
                    hostport = f"{host}:{port}"
                else:
                    hostport = hostport.lower()
                netloc = f"{userinfo + '@' if userinfo else ''}{hostport}"
            # Remove trailing slash on non-root path
            path = parts.path
            if path != '/' and path.endswith('/'):
                path = path.rstrip('/')
            # Compose URL back
            new_url = urlunparse((scheme, netloc, path, parts.params, parts.query, parts.fragment))
            return new_url
        except Exception:
            return url

    @staticmethod
    def clean_text(text):
        if not text:
            return text
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Collapse whitespace and remove leading/trailing
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def parse_date(date_str):
        if not date_str:
            return None
        # Try various date formats
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%B %d, %Y", "%d %B %Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except Exception:
                continue
        return None

    @staticmethod
    def fingerprint_item(item):
        # Use canonicalized link for fingerprint
        link = NormalizationPipeline.canonicalize_url(item.get('link') or "")
        base = (item.get('title') or "") + "|" + (link or "")
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def process_item(self, item, spider):
        # Clean/normalize fields
        for field in ["title", "description", "eligibility"]:
            item[field] = self.clean_text(item.get(field))
        # Canonicalize link before fingerprinting
        if "link" in item and item["link"]:
            item["link"] = self.canonicalize_url(item["link"])
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