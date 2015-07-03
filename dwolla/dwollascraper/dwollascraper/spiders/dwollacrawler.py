# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from dwollascraper.items import DwollascraperItem


class DwollacrawlerSpider(CrawlSpider):
    name = 'dwollacrawler'
    allowed_domains = ['discuss.dwolla.com']
    start_urls = ['http://www.discuss.dwolla.com/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = DwollascraperItem()
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
