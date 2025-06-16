import scrapy

class KomkomScraperItem(scrapy.Item):
    # define the fields for your item here
    title = scrapy.Field()
    link = scrapy.Field()
    # Add other fields as needed