# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# import scrapy


# class OlxScraperItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     listing_id = scrapy.Field()
#     title = scrapy.Field()
#     price = scrapy.Field()
#     location = scrapy.Field()
#     url = scrapy.Field()

#     pass
# olx_scraper/items.py
import scrapy
class OlxItem(scrapy.Item):
    details = scrapy.Field()
    price = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()

pass