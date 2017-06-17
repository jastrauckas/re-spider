# -*- coding: utf-8 -*-
import scrapy
import smtplib
import datetime
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from email.mime.text import MIMEText
from email.header    import Header

def sendEmail(links):
    txt=''
    for link in links:
        txt += (link + '\n')

    msg = MIMEText(txt, 'plain', 'utf-8')
    msg['Subject'] = Header('New Listings', 'utf-8')
    msg['From'] = 'wall_e_bot@yahoo.com'
    msg['To'] = 'jastrauckas@gmail.com'

    username = str('wall_e_bot@yahoo.com')
    password = str('GOhXvopk6q')  

    try:
        server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()    
        print('Email sent')
    except Exception as e:
        print('Failed to send email: '+ str(e))


class RealtorSpider(scrapy.Spider):

    name = "realtor"
    station = (0,0)
    start_url = ''

    def start_requests(self):
        urls = [self.start_url]
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

        sendEmail(keepers)
        self.log('Crawled file %s' % filename)


class ChathamSpider(RealtorSpider):
    name = "chatham"
    station = (40.7400965, -74.38508279999996)
    start_url = 'http://www.realtor.com/realestateandhomes-search/Chatham_NJ/type-single-family-home/price-na-650000'

class SummitSpider(RealtorSpider):
    name = 'summit'
    station = (40.71673459999999, -74.35769349999998)
    start_url = 'http://www.realtor.com/realestateandhomes-search/Summit_NJ/type-single-family-home/price-na-650000'
