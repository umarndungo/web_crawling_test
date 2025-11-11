# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    availability = scrapy.Field()
    reviews = scrapy.Field()
    image_url = scrapy.Field()
    rating = scrapy.Field()
    crawl_timestamp = scrapy.Field()
    status = scrapy.Field()
