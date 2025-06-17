import scrapy
from komkom_scraper.items import OpportunityItem
import re

class WekomkomSpider(scrapy.Spider):
    name = 'wekomkom_spider'
    allowed_domains = ['wekomkom.com']
    start_urls = ['https://wekomkom.com/accompagnement']

    def parse(self, response):
        # Find all opportunity cards by link text "Voir l'offre"
        links = response.xpath('//a[contains(text(),"Voir l\'offre")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_opportunity)
        # Pagination: minimal, follow <a rel="next"> or button[aria-label="Next"]
        next_page = response.xpath('//a[@rel="next"]/@href | //button[@aria-label="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_opportunity(self, response):
        def get_title():
            # Try h1, then og:title meta
            t = response.css('h1::text').get()
            if t:
                return t.strip()
            ogt = response.css('meta[property="og:title"]::attr(content)').get()
            return ogt.strip() if ogt else None

        def get_description():
            # Try div.description, then article, fallback to body
            htmls = response.css('div.description').getall()
            if htmls:
                return ''.join(htmls).strip()
            htmls = response.css('article').getall()
            if htmls:
                return ''.join(htmls).strip()
            htmls = response.css('body').getall()
            return ''.join(htmls).strip() if htmls else None

        def get_deadline():
            # Look for "Date limite" with a date
            # 1. Text containing "Date limite" and a date
            match = re.search(r"Date limite[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})", response.text, re.IGNORECASE)
            if match:
                return match.group(1)
            # 2. Text like "X jours pour postuler" means relative, so deadline=None
            if re.search(r"\d+\s+jours\s+pour\s+postuler", response.text, re.IGNORECASE):
                return None
            return None

        def get_publication_date():
            pub = response.css('meta[property="article:published_time"]::attr(content)').get()
            if pub:
                return pub.strip()
            pub2 = response.css('meta[name="date"]::attr(content)').get()
            return pub2.strip() if pub2 else None

        def get_opportunity_type(description):
            desc_text = (description or "").lower()
            if any(kw in desc_text for kw in ['financement', 'subvention', 'prêt']):
                return 'Financement'
            if any(kw in desc_text for kw in ['formation', 'coaching']):
                return 'Formation'
            return 'Accompagnement'

        def get_eligibility():
            # Find <h2> containing "Eligibilité", get first following sibling
            headers = response.xpath("//h2[contains(translate(text(),'ELIGIBILITÉ', 'eligibilité'), 'eligibilité')]")
            if headers:
                sibling = headers[0].xpath('following-sibling::*[1]')
                return sibling.get() if sibling else None
            return None

        title = get_title()
        description = get_description()
        deadline = get_deadline()
        publication_date = get_publication_date()
        opportunity_type = get_opportunity_type(description)
        eligibility = get_eligibility()

        yield OpportunityItem(
            title=title,
            description=description,
            deadline=deadline,
            publication_date=publication_date,
            opportunity_type=opportunity_type,
            eligibility=eligibility,
            link=response.url,
            source='WEKOMKOM',
        )