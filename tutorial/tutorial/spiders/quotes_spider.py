import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]


    def parse(self, response):
        quotes = response.xpath('//div[@class="quote"]')

        for quote in quotes:
            yield {
                "text": quote.xpath('./span[@class="text"]/text()').extract_first(),
            }
