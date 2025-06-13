import scrapy

class OpportunityItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    deadline = scrapy.Field()
    link = scrapy.Field()
    opportunity_type = scrapy.Field()
    sector = scrapy.Field()
    amount = scrapy.Field()
    eligibility = scrapy.Field()
    source = scrapy.Field()