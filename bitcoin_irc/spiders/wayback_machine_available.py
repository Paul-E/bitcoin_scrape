# -*- coding: utf-8 -*-
import datetime
import json

from sys import intern
from re import search

import scrapy
import pdb

from bitcoin_irc.items import WaybackData


PATTERN = "(http://bitcoinstats.com/irc/bitcoin-dev/logs/(20[0-9]+)/[01][0-9]/[0-3][0-9])"
WAYBACK_API_URL = "http://web.archive.org/cdx/search/cdx?url="
BASE_URL = WAYBACK_API_URL + "http://bitcoinstats.com/irc/bitcoin-dev/logs/{}/{:02d}/{:02d}&output=json&fl=timestamp,original,mimetype,statuscode"

GOOD_MIME = set(["application/http;msgtype=response", "text/html"])

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
        
        

class WaybackURLs(scrapy.Spider):
    name = "waybackurls"
    allowed_domains = ["http://archive.org"]
    start_urls = start_url_generator()
    seen_mime = set(GOOD_MIME)

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        if len(json_response) == 0:
            return

        bitcoin_url = intern(search(PATTERN, response.url).group(1))
        for result in json_response[1:]:
            if result[2] not in GOOD_MIME or result[3] != "200":
                if result[2] not in self.seen_mime:
                    self.seen_mime.add(result[2])
                    pdb.set_trace()
                continue
            timestamp = datetime.datetime.strptime(result[0],
                                                   "%Y%m%d%H%M%S")            
            item = WaybackData()
            item["timestamp"] = timestamp
            item["bitcoinirc_url"] = bitcoin_url
            item["archived_bitcoinirc_url"] = intern(result[1])
            yield item
        
