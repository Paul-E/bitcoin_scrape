# -*- coding: utf-8 -*-
import datetime

from sys import intern
from re import search, sub
from pickle import load
import scrapy
import pdb

from bitcoin_irc.items import WaybackArchive

REPLACE = b'<a name="l[0-9.]+">\n(<a href="#l[0-9.]+">[0-9]{2}:[0-9]{2}</a>)\n</a>'
EXPRESSION = "([a-z\-]+)/logs/(20[0-9]+)/([0-9]{2})/([0-9]{2})"
ARCHIVE_TIME = "([0-9]{14})"
BASE_URL = "http://bitcoinstats.com/irc/bitcoin-dev/logs/{}/{:02d}/{:02d}"


with open("available_all.pickle", "rb") as pickle_file:
    available = load(pickle_file)
for entry in available:
    entry["wayback_url"] = entry["wayback_url"].replace("http", "https", 1)
start_urls = [entry["wayback_url"] for entry in available]

class WaybackData(scrapy.Spider):
    name = "waybackdata"
    allowed_domains = ["http://archive.org"]
    start_urls = start_urls

    def parse(self, response):
        if response.status == 200:
            # Replace the nested <a> tags
            new_body = sub(REPLACE, lambda x: x.group(1), response.body)
            response = response.replace(body = new_body)        
        url_params = search(EXPRESSION, response.url)
        chan = intern(url_params.group(1))
        ar_time_match = search(ARCHIVE_TIME, response.request.url)
        archive_time = datetime.datetime.strptime(ar_time_match.group(1),
                                                  "%Y%m%d%H%M%S")
        for row in response.xpath('//div[@class="container"]//tr'):
            elements = row.xpath("td")
            time_string = elements[0].xpath("a/@href").extract()[0].replace("#l", "")
            pytime = datetime.datetime.fromtimestamp(float(time_string))
            try:
                username = intern(elements[1].xpath("text()").extract()[0])
            except IndexError:
                username = ""
            extracted_text = elements[2].xpath(".//text()").extract()
            if len(extracted_text) > 0:
                text = extracted_text[0]
            else:
                text = ""
                
            item = WaybackArchive()
            item["time"] = pytime
            item["chan"] = chan
            item["username"] = username
            item["text"] = text
            item["archive_time"] = archive_time
            yield item
