# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BitcoinIrcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    time = scrapy.Field()
    chan = scrapy.Field()
    username = scrapy.Field()
    text = scrapy.Field()

class WaybackData(scrapy.Item):
    bitcoinirc_url = scrapy.Field()
    archived_bitcoinirc_url = scrapy.Field()
    timestamp = scrapy.Field()
