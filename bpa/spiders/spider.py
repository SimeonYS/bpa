import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbpaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbpaSpider(scrapy.Spider):
	name = 'bpa'
	start_urls = ['http://www.bpa.cu/home/news?page=1']

	def parse(self, response):
		articles = response.xpath('//div[@class="row pl-3"]')
		for article in articles:
			date = article.xpath('.//div[@class="row"]/div[2]//text()').get()
			post_links = article.xpath('.//div[@class="col-md-2 offset-md-4 offset-sm-0 pl-0"]//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="col-md-8 pull-left"]/h3/text()').get()
		content = response.xpath('//div[@class="row"]//text()[not (ancestor::h3 or ancestor::div[@class="d-flex justify-content-between text-muted"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbpaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
