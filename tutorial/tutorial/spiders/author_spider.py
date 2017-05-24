import scrapy


author_set = set()
class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['http://quotes.toscrape.com/']


    def parse(self, response):
        # follow links to author pages
        for href in response.css('.author + a::attr(href)').extract():
            # print(href,"==",type(href))
            next_page = response.urljoin(href)
            yield scrapy.Request(next_page, self.parse_author)

        # follow pagination links
        for href in response.css('li.next a::attr(href)').extract():
            next_page = response.urljoin(href)
            yield scrapy.Request(next_page, self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        name = extract_with_css('h3.author-title::text')
        if name in author_set:
            pass
        else:
            author_set.add(name)

        yield {
            'name': name,
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }
