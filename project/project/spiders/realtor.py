# -*- coding: utf-8 -*-
import scrapy

class RealtorSpider(scrapy.Spider):
    name = "realtor"

    def start_requests(self):
        urls = [
            'http://www.realtor.com/realestateandhomes-search/Chatham_NJ/type-single-family-home/price-na-750000',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'realtor-%s.html' % page
        details = response.css('a[href*=detail]::attr(href)').extract()
        for d in details:
            print(d)
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        self.log('Crawled file %s' % filename)
