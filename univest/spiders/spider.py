import scrapy

from scrapy.loader import ItemLoader

from ..items import UnivestItem
from itemloaders.processors import TakeFirst


class UnivestSpider(scrapy.Spider):
	name = 'univest'
	start_urls = ['https://www.univest.net/newsroom']

	def parse(self, response):
		post_links = response.xpath('//div[contains(@class,"article")]/div[@class="row"]')
		for post in post_links[1:]:
			url = post.xpath('.//a/@href').get()
			date = post.xpath('.//span[@class="big"]/text()').get()[1:]
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h3//text()[normalize-space()] | //h2[@class="module-details_title"]//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()] | //*[contains(concat( " ", @class, " " ), concat( " ", "padder-v-xxl", " " ))]//text()[normalize-space() and not(ancestor::h3)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=UnivestItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
