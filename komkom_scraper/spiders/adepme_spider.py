import scrapy
from komkom_scraper.items import KomkomScraperItem

class AdepmeSpider(scrapy.Spider):
    name = "adepme_spider"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com"]

    def parse(self, response):
        # Example item, replace with your scraping logic
        item = KomkomScraperItem()
        item['title'] = response.xpath('//title/text()').get()
        item['link'] = response.url
        yield item