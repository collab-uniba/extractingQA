# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

class DsscraperPipeline(object):
	logger = logging.getLogger(__name__)

	def process_item(self, item, spider):
		self.cleanse_unicode(item)
	        return item

	def cleanse_unicode(self, item):
		self.logger.debug("Cleansing %s", item)
		return item
