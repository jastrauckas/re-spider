# -*- coding: utf-8 -*-
from __future__ import print_function

import scrapy
import smtplib
import datetime
import os
import util
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from email.mime.text import MIMEText
from email.header import Header
from multiprocessing import Lock


stations = {
    'chatham': (40.7400965, -74.38508279999996),
    'short hills': (40.725201, -74.322998),
    'millburn': (40.725711, -74.303682),
    'maplewood': (40.731303, -74.275522),
}

# create output directory and lock for output file
output_lock = Lock()

output_filename = util.get_output_filename()
if not os.path.exists(os.path.dirname(output_filename)):
    try:
        os.makedirs(os.path.dirname(output_filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

yesterday_listings = set(util.get_yesterday_results())
print('YESTERDAY: ' + str(yesterday_listings))

password = ''
with open('pwd.txt') as pwd_file:
    password = pwd_file.readlines()[0]

def sendEmail(links):
    txt=''
    for link in links:
        txt += (link + '\n')

    print('Email body:')
    print(txt)

    msg = MIMEText(txt, 'plain', 'utf-8')
    msg['Subject'] = Header('New Listings', 'utf-8')
    msg['From'] = 'wall_e_bot@yahoo.com'
    msg['To'] = 'jastrauckas@gmail.com'

    username = str('wall_e_bot@yahoo.com')

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

    # maps town name to a list of URLS
    result_map = {}

    def start_requests(self):
        urls = [
            'http://www.realtor.com/realestateandhomes-search/Chatham_NJ/type-single-family-home/price-na-750000',
            'http://www.realtor.com/realestateandhomes-search/Millburn_NJ/type-single-family-home/price-na-750000',
            'http://www.realtor.com/realestateandhomes-search/Maplewood_NJ/type-single-family-home/price-na-750000'
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
                for name,coords in stations.items():
                    dist = great_circle(
                        coords,
                        (location.latitude, location.longitude))
                    if dist.miles < 1.0:
                        listing = 'realtor.com{}'.format(d)
                        if listing not in yesterday_listings:
                            keepers.append(listing)

        print('MATCHES:')
        for link in keepers:
            print(link)

        output_lock.acquire()
        with open(output_filename, 'a') as output_file:
            for link in keepers:
                print(link, file=output_file)
        output_lock.release()

        print('Sending email...')
        sendEmail(keepers)
        self.log('Crawled file %s' % filename)
