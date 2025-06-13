import scrapy

class OpportunityItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    deadline = scrapy.Field()
    publication_date = scrapy.Field()
    opportunity_type = scrapy.Field()
    eligibility = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()