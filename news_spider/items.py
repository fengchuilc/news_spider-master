# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class NewsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    type = Field()
    source = Field()
    newsId = Field()
    title = Field()
    contents = Field()
    url = Field()
    comments = Field()
    time = Field()
    body=Field()
