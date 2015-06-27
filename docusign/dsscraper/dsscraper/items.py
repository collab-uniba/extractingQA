# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class DsscraperItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
	uid = Field()
	title = Field()
	text = Field()
	url = Field()
	date_time = Field()
	tags = Field()
	views = Field()
	answers = Field()
	resolve = Field()
