# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class DsscraperItem(Item):

	uid = Field()
	type = Field()
	title = Field()
	text = Field()
	date_time = Field()
	tags = Field()
	views = Field()
	answers = Field()
	resolve = Field()
	upvotes = Field()
	url = Field()
