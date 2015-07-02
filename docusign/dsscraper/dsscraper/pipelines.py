# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import unidecode
from six import string_types

class DsscraperPipeline(object):
	logger = logging.getLogger(__name__)

	def process_item(self, item, spider):
		self.cleanse_unicode(item)
	        return item

	def cleanse_unicode(self, item):
		if isinstance(item, string_types) or isinstance(item, unicode):
			self.logger.debug("Cleansing unicode %s", item)
			unidecode.unidecode(item)
			uniString = unicode(item, "UTF-8")
			uniString = uniString.replace(u"\u00a0", "")
			item = uniString
		
		# TODO: still don't know how to deal with HTML content
		return item
