# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from unidecode import unidecode
import logging
from dsscraper.items import DsscraperItem


class DscrawlerSpider(CrawlSpider):
	logger = logging.getLogger(__name__)

	name = 'dscrawler'
	allowed_domains = ['community.docusign.com']
	start_urls = ['http://community.docusign.com/t5/DocuSign-API-Integration-NET-READ-ONLY/bd-p/Electronic_Signature_API'] 
		#'http://community.docusign.com/t5/DocuSign-API-Integration-Java-READ-ONLY/bd-p/Java', 
		#'http://community.docusign.com/t5/DocuSign-API-Integration-PHP-READ-ONLY/bd-p/php_api', 
		#'http://community.docusign.com/t5/DocuSign-API-Integration-Ruby-Salesforce-and-Other-READ-ONLY/bd-p/dev_other',
		#'http://community.docusign.com/t5/Misc-Dev-Archive-READ-ONLY/bd-p/Ask_A_Development_Question_Board']

	rules = (
		Rule( LinkExtractor( deny=('q=change_me_', 'nospellcheck=true', 'searchpage', 'viewprofilepage', 'kudosleaderboardpage', 'userloginpage', 'userregistrationpage', 'DocuSignIdeas', 'enableautocomplete', ), allow=(r'(Electronic_Signature_API(\/page\/\d+)?)$',) ), callback='parse_page', follow=True ),
	)

	uid = 0 # static item counter, +1 as a new discussion is crawled


	# parse a subforum page
	def parse_page(self, response):
		self.logger.debug('Hit page %s', response.url)
		discussions = response.xpath('//*[@id="messageList"]/div/table/tbody/tr/td/div/div/div/h2/span/a')

               	for discussion in discussions:
                       	url = response.urljoin( discussion.xpath(
                                'attribute::href').extract()[0] )
			yield scrapy.Request(url, callback=self.parse_discussion)


	# scrape a question, answers are associated by id 
	def parse_discussion(self, response):
		self.logger.debug('Parsing question %s', response.url)
		DscrawlerSpider.uid += 1		

		item = DsscraperItem()
		item['type'] = 'question'
		item['uid'] = DscrawlerSpider.uid

		# //*[@id="link_4"]
                item['title'] = "".join ( response.xpath(
                	'//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/h1/text()').extract() )

                item['url'] = response.url

		date = response.xpath(
			'//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[1]/text()').extract()[0].strip()
		date = unidecode(date)
		time = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[2]/text()').extract()[0] 
		item['date_time'] = date.replace("-", "/") + ' ' + time

		text = response.xpath('//*[@id="messagebodydisplay"]/div/p').extract()
		item['text'] = unidecode("\n".join(text))

		resolve = response.xpath('//*[@id="messagebodydisplay"]/div/div/p/text()').extract() 
		if resolve and 'Solved!' in resolve[0].strip():
			item['resolve'] = True
		else:
			item['resolve'] = False

		views = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div[2]/span[2]/text()').extract()[0]
		item['views'] = int( views[1:-7].replace(',', '') ) ## removes comma, leading "(" and trailing " Views)"

		# kudos are upvotes
		upvotes =  response.xpath('//*[@class="MessageKudosCount lia-component-kudos-widget-message-kudos-count"]/text()').extract() 
		if not upvotes:
			upvotes = response.xpath('//*[@id="kudosButtonV2"]/div/div[1]/span/span[@class="MessageKudosCount lia-component-kudos-widget-message-kudos-count"]/text()').extract()
		item['upvotes'] = int(upvotes[0].strip())

		answers = response.xpath('//*[@id="messageview"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div[2]/span[1]/text()[2]').extract()[0].strip()
		item['answers'] = int(answers[3:]) - 1 # the no of answers is the no of messages in the discussion minus the question itself

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

		# sostituire in response.url '/td-p/' con '/m-p/', altrimenti l'url risulta gia' visitato e la request fallisce
		new_url = response.url
		new_url = new_url.replace("/td-p/", "/m-p/", 1)
		yield scrapy.Request(new_url, callback=self.parse_answers, meta={'question': item})


        # scrape answers
	def parse_answers(self, response):
		question = response.meta['question']
                uid = question['uid']
                answers = question['answers']
 
                # a thread is made of a question and its following answers, to be appended here
	        thread = [question]
 
                self.logger.debug('Parsing %s answers', answers)
		for i in range(0, answers):
                	item = DsscraperItem()
                        item['type'] = 'answer'
                        item['uid'] = uid # same as the discussion thread the answer belongs to

                        answer = response.xpath('//*[@id="lineardisplaymessageviewwrapper_{0}"]'.format(i))
                        item['url'] = response.url
                        item['title'] = "".join( answer.xpath(
                        	'//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/h1/text()'.format(i)).extract() )

                        text = response.xpath('//*[@id="messagebodydisplay_{0}"]/div/p'.format(i)).extract()
                        item['text'] = unidecode("\n".join(text))

                        date = response.xpath(
                                '//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[1]/text()'.format(i)).extract()[0].strip()
			date = unidecode(date)
                        time = response.xpath('//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/p/span/span[2]/text()'.format(i)).extract()[0]
                        item['date_time'] = date.replace("-", "/") + ' ' + time

                        resolve = response.xpath('//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div/span[@class="solution"]'.format(i))
                        if resolve:
		                item['resolve'] = True
                        else:
                                item['resolve'] = False

                        item['answers'] = 'N/A'
                        item['tags'] = 'N/A'

                        # kudos are upvotes
                        upvotes = response.xpath('//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[3]/div/div/div/div/div/div/div/a/span/text()'.format(i)).extract()
			if not upvotes:
				upvotes = response.xpath('//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[3]/div/div/div/div/div/div/div/span/span/text()'.format(i)).extract()
                        item['upvotes'] = int(upvotes[0].strip())

                        views = response.xpath('//*[@id="messageview_{0}"]/div/div/div/div[3]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div[2]/span[2]/text()'.format(i)).extract()[0]
                        item['views'] = int( views[1:-7].replace(',', '') ) ## removes comma, leading "(" and trailing " Views)"

                        thread.append(item)

		return thread

