# -*- coding: utf-8 -*-
import datetime

from sys import intern
from re import search, sub
import scrapy
import pdb

from bitcoin_irc.items import BitcoinIrcItem

# REPLACE = '<a name="l[0-9.]+">'
REPLACE = b'<a name="l[0-9.]+">\n(<a href="#l[0-9.]+">[0-9]{2}:[0-9]{2}</a>)\n</a>'
EXPRESSION = "([a-z\-]+)/logs/(20[0-9]+)/([0-9]{2})/([0-9]{2})"
BASE_URL = "http://bitcoinstats.com/irc/bitcoin-dev/logs/{}/{:02d}/{:02d}"

def start_url_generator():
    start_year = 2010
    start_month = 10
    start_day = 1
    current_date = datetime.date(start_year, start_month, start_day)
    end = datetime.datetime.now().date()
    delta = datetime.timedelta(days = 1)
    while current_date <= end:
        yield BASE_URL.format(current_date.year,
                              current_date.month,
                              current_date.day)
        current_date += delta
        
        


class BitcoinstatsSpider(scrapy.Spider):
    name = "bitcoinstats"
    allowed_domains = ["http://bitcoinstats.com"]
    # start_urls = (
    #     # 'http://www.http://bitcoinstats.com/',
    #     "http://bitcoinstats.com/irc/bitcoin-dev/logs/2016/04/05",
    # )
    start_urls = start_url_generator()

    def parse(self, response):
        if response.status == 200:
            # Replace the nested <a> tags
            new_body = sub(REPLACE, lambda x: x.group(1), response.body)
            response = response.replace(body = new_body)
        url_params = search(EXPRESSION, response.url)
        chan = intern(url_params.group(1))
        year = int(url_params.group(2))
        month = int(url_params.group(3))
        day = int(url_params.group(4))
        for row in response.xpath("//tr"):
            elements = row.xpath("td")
            time_string = elements[0].xpath("a/@href").extract()[0].replace("#l", ")"
            pytime = datetime.datetime.fromtimestamp(float(time_string))
            username = intern(elements[1].xpath("text()").extract()[0])
            extracted_text = elements[2].xpath(".//text()").extract()
            if len(extracted_text) > 0:
                text = extracted_text[0]
            else:
                text = ""
                
            item = BitcoinIrcItem()
            item["time"] = pytime
            item["chan"] = chan
            item["username"] = username
            item["text"] = text
            yield item
