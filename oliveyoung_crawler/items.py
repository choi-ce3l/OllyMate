# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OliveyoungCrawlerItem(scrapy.Item):
    goodsNo = scrapy.Field()
    goodsName = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()
    pricerange = scrapy.Field()
    purchase_link = scrapy.Field()
    image_link = scrapy.Field()
    memberNo = scrapy.Field()
    skintype = scrapy.Field()
    skintone = scrapy.Field()
    skinconcern = scrapy.Field()
    review = scrapy.Field()
    rating = scrapy.Field()
    date = scrapy.Field()
    rank = scrapy.Field()
