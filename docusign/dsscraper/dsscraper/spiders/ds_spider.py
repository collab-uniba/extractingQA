from scrapy import Spider
from scrapy.selector import Selector
from scrapy.shell import inspect_response

from operator import itemgetter

from dsscraper.items import DsscraperItem


class StackSpider(Spider):
	name = "dsscraper"
	allowed_domains = ["community.docusign.com"]
	start_urls = [
		"http://community.docusign.com/t5/forums/searchpage/tab/message/page/1?advanced=true&filter=acceptedSolutions%2Clabels%2CsolvedThreads&include_forums=true&location=category%3ADevZone2&search_page_size=50&search_type=thread&solution=true&solved=true&sort_by=-solutionDate",
	]

	def parse(self, response):
		discussions = Selector(response).xpath('//h2[@class="lia-message-subject"]/a')
		baseURL = "http://community.docusign.com"

		for discussion in discussions:
			item = DsscraperItem()
			item['title'] = discussion.xpath(
                		'child::text()').extract()
	            	item['url'] = discussion.xpath(
        	        	'attribute::href').extract()
			item['url'] = baseURL + itemgetter(0)(item['url'])
	            	yield item


	def parse_details(self, response):
		item = response.meta.get('item', None)
		if item:
			# populate more `item` fields
			return item
		else:
			inspect_response(response, self)
