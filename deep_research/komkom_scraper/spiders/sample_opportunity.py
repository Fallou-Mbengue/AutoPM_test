import scrapy
from komkom_scraper.items import OpportunityItem

class SampleOpportunitySpider(scrapy.Spider):
    name = "sample_opportunity"
    allowed_domains = ["example.com"]
    start_urls = [
        "https://example.com/opportunities.json"
    ]

    def parse(self, response):
        data = response.json()
        for entry in data.get("opportunities", []):
            yield OpportunityItem(
                title=entry.get("title"),
                description=entry.get("description"),
                deadline=entry.get("deadline"),
                link=entry.get("link"),
                opportunity_type=entry.get("opportunity_type"),
                sector=entry.get("sector"),
                amount=entry.get("amount"),
                eligibility=entry.get("eligibility"),
                source=response.url
            )