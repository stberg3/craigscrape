import scrapy
from functools import reduce
from re import search

class CraigSpider(scrapy.Spider):
    name = "craig"

    start_urls = [
        "https://minneapolis.craigslist.org/search/sya",
        # "https://minneapolis.craigslist.org/search/syp",
    ]

    def parse_contact(self, response):
        name, phone, email = None
        name  = response.xpath(\
                '//li/h1[text()="contact name:"]/../p/text()').extract_first()

        phone = response.xpath('//p[@class="reply-tel-number"]/text()'\
                            ).re(r'(?:\(\d{3}\)\s)\d{3}-\d{4}')[0]

        email = response.xpath('//a[@class="mailapp"]/text()').extract_first()

        response.meta['name'] = name
        response.meta['phone'] = phone
        response.meta['email'] = email

        yield response.meta

    def get_contact_url(self, url, response):
        url_base = search(r'([^\.]+\.\w+\.\w+)', url).group(1)
        url_tail = response.xpath('//a[@id="replylink"]/@href').extract_first()
        return url_base+url_tail

    def parse(self, response):
        # follow links to listing pages
        for href in response.xpath('//p[@class="result-info"]/a/@href'\
                                    ).extract():
            next_page = response.urljoin(href)
            yield scrapy.Request(next_page, self.parse_listing)

        # follow pagination links
        href = response.xpath('//span[@class="buttons"]/a[last()]/@href'\
                              ).extract_first()
        if href is not None:
            next_page = response.urljoin(\
                response.xpath(\
                    '//span[@class="buttons"]/a[last()]/@href').extract_first())
            yield scrapy.Request(next_page, self.parse)

    def parse_listing(self, response):
        lat, long = response.xpath('//p[@class="mapaddress"]/small/a/@href'\
                                    ).re(r'@([^,]+),([^,]+)')


        meta = {
            'title': response.xpath('//span[@id="titletextonly"]/text()'\
                                    ).extract_first(),
            'images': response.xpath('//div[@id="thumbs"]/a/@href').extract(),
            'lat': lat,
            'long': long,
            'text': reduce(lambda x,y: x+y, \
                           response.xpath('//section[@id="postingbody"]/text()'\
                           ).extract()),
            'date': response.xpath('//p[@id="display-date"]/time/@datetime'\
                                    ).extract_first(),
            'url': response.url,
        }

        contact_url = self.get_contact_url(response.url, response)
        yield scrapy.Request(contact_url, self.parse_contact, meta=meta)
