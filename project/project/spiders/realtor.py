# -*- coding: utf-8 -*-
import scrapy
from geopy.geocoders import Nominatim
from geopy.distance import great_circle

class RealtorSpider(scrapy.Spider):
    name = "realtor"
    station = (0,0)
    start_url = ''

    def start_requests(self):
        urls = [
            self.start_url,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        keepers = []
        page = response.url.split("/")[-2]
        filename = 'realtor-%s.html' % page
        details = response.css('a[href*=detail]::attr(href)').extract()
        unique_details = set()
        for d in details:
            unique_details.add(d)
            #print(d)

        geolocator = Nominatim()
        for d in unique_details:
            address_lst = d.split('/')[-1].split('_')[0:-1]
            street_addr = address_lst[0].replace('-', ' ')
            city, state, zipcode = address_lst[1:4]
            addr = '{} {}, {} {}'.format(street_addr, city, state, zipcode)
            #print(addr)

            location = geolocator.geocode(addr)
            if not location:
                print('ERROR: location lookup failed for ' + addr)
            else:
                dist = great_circle(
                    self.station,
                    (location.latitude, location.longitude))
                if dist.miles < 1.0:
                    keepers.append('realtor.com{}'.format(d))

        for link in keepers:
            print(link)
        self.log('Crawled file %s' % filename)


class ChathamSpider(RealtorSpider):
    name = "chatham"
    station = (40.7400965, -74.38508279999996)
    start_url = 'http://www.realtor.com/realestateandhomes-search/Chatham_NJ/type-single-family-home/price-na-750000'



