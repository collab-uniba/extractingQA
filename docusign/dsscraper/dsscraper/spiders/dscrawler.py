# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

import unidecode
import logging
from dsscraper.items import DsscraperItem


class DscrawlerSpider(CrawlSpider):
	logger = logging.getLogger(__name__)

	name = 'dscrawler'
	allowed_domains = ['community.docusign.com']
	start_urls = ['http://community.docusign.com/t5/DocuSign-API-Integration-NET-READ-ONLY/bd-p/Electronic_Signature_API', 
		'http://community.docusign.com/t5/DocuSign-API-Integration-Java-READ-ONLY/bd-p/Java', 
		'http://community.docusign.com/t5/DocuSign-API-Integration-PHP-READ-ONLY/bd-p/php_api', 
		'http://community.docusign.com/t5/DocuSign-API-Integration-Ruby-Salesforce-and-Other-READ-ONLY/bd-p/dev_other',
		'http://community.docusign.com/t5/Misc-Dev-Archive-READ-ONLY/bd-p/Ask_A_Development_Question_Board']

	rules = (
		Rule(LinkExtractor(deny=r'/\?q=change_me_/'), follow=False),
        	Rule(LinkExtractor(allow=r'/t5/DocuSign-API-Integration-NET-READ-ONLY/bd-p/'), callback='parse_page', follow=True),
		Rule(LinkExtractor(allow=r'/t5/DocuSign-API-Integration-Java-READ-ONLY/bd-p/'), callback='parse_page', follow=True),
		Rule(LinkExtractor(allow=r'/t5/DocuSign-API-Integration-PHP-READ-ONLY/bd-p/'), callback='parse_page', follow=True),
		Rule(LinkExtractor(allow=r'/t5/DocuSign-API-Integration-Ruby-Salesforce-and-Other-READ-ONLY/bd-p/'), callback='parse_page', follow=True),
	        Rule(LinkExtractor(allow=r'/t5/Misc-Dev-Archive-READ-ONLY/bd-p/'), callback='parse_page', follow=True),
	)

	#parsed_pages = set()
	uid = 0 # static item counter, ++1 as a new discussion is crawled


	def parse_page(self, response):
		self.logger.debug('Hit page %s', response.url)
		#DscrawlerSpider.parsed_pages.add(response.url)
                discussions = response.xpath('//h2[@class="lia-message-subject"]/a')
		# FIXME this is not matching anything
		# first get the body, then the single questions with href attribute

                for discussion in discussions:
                        url = response.urljoin( discussion.xpath(
                                'attribute::href').extract()[0] )
			yield scrapy.Request(url, callback=self.parse_discussion)

	def parse_discussion(self, response):
		self.logger.debug('Hit discussion %s', response.url)
		DscrawlerSpider.uid += 1		

		item = DsscraperItem()
		item['uid'] = DscrawlerSpider.uid

		# //*[@id="link_4"]
                item['title'] = "".join ( response.xpath(
                	'//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/h1/text()').extract() )

                item['url'] = response.url

		date = unidecode.unidecode( response.xpath(
			'//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[1]/text()').extract()[0].strip() )
		time = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[2]/text()').extract()[0] 
		item['date_time'] = date + ' ' + time

		text = response.xpath('//*[@id="messagebodydisplay"]/div/p/text()').extract()
		for row in text:
			row = unidecode.unidecode(row)
		item['text'] = "\n".join(text)

		resolve = response.xpath('//*[@id="messagebodydisplay"]/div/div/p/text()').extract()[0].strip()
		if 'Solved!' in resolve:
			item['resolve'] = True
		else:
			item['resolve'] = False

		views = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div[2]/span[2]/text()').extract()[0]
		item['views'] = views[1:-7].replace(',', '') ## removes comma, leading "(" and trailing " Views)"

		answers = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div[2]/span[1]/a/text()').extract()[0].strip()
		item['answers'] = answers

		try:
			tags = response.xpath('//*[@id="link_13"]/text()').extract()[0].strip()
			if 'Me too' in tags:
				item['tags'] = ''
			else:
				item['tags'] = tags
		except IndexError as e:
			#print "Index out of range ({0})".format(e)   # <=>  ignore, no tags				
			item['tags'] = '' 
			pass # don't give up on building the item, though
		except:
			print "Unexpected error:", sys.exc_info()[0]  # this is unexpected
                       	item['tags'] = '' 
			pass

		yield item
		parse_answers(self, response, answers)


	# TODO add kudos count as upvotes
	def parse_answers(self, response, answers):
		self.logger.debug('Parsing %s answers', answers)

		for i in range(0, answers):
			item = DsscraperItem()

			item['uid'] = DscrawlerSpider.uid # same as the discussion thread the answer belongs to

			answer = response.xpath('//*[@id="lineardisplaymessageviewwrapper_{0}"]'.format(i))
			item['url'] = response.url
			item['title'] = "".join( answer.xpath(
				'//*[@id="messageview_2"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/h1/text()').extract )

			text = response.xpath('//*[@id="messagebodydisplay_2"]/div/p/text()').extract()
			for row in text:
				row = unidecode.unidecode(row)
			item['text']
			
	                date = unidecode.unidecode( response.xpath(
        	                '//*[@id="messageview_2"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[1]/text()').extract()[0].strip() )
                	time = response.xpath('//*[@id="messageview_2"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[2]/text()').extract()[0]
	                item['date_time'] = date + ' ' + time

	                resolve = response.xpath('//*[@id="messageview_2"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/span[1]/boolean()')
                	item['resolve'] = resolve 

			item['answers'] = 'N/A'
			item['tags'] = 'N/A'
			
	                views = response.xpath('/text()').extract()[0]
	                item['views'] = views[1:-7].replace(',', '') ## removes comma, leading "(" and trailing " Views)"
		
			yield item

