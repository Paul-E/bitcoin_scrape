# -*- coding: utf-8 -*-
import datetime
import json

from sys import intern
from collections import defaultdict
from re import search, sub
from scrapy.http import Request

import scrapy
import pdb

from bitcoin_irc.items import WaybackURL


PATTERN = "(http://bitcoinstats.com/irc/bitcoin-dev/logs/(20[0-9]+)/[01][0-9]/[0-3][0-9])"
WAYBACK_API_URL = "http://archive.org/wayback/available?url="
BASE_URL = WAYBACK_API_URL + "http://bitcoinstats.com/irc/bitcoin-dev/logs/{}/{:02d}/{:02d}"
EARLIEST = datetime.datetime(2010, 10, 1)

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
    page_timestamps = defaultdict(dict)

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        snapshots = json_response["archived_snapshots"]
        # pdb.set_trace()
        if len(snapshots) == 0:
            return
        closest = snapshots["closest"]
        url = closest["url"]
        timestamp = datetime.datetime.strptime(closest["timestamp"],
                                               "%Y%m%d%H%M%S")
        bitcoin_url = search(PATTERN, response.url).group(1)
        if len(self.page_timestamps[bitcoin_url]) is 0:
            self.page_timestamps[bitcoin_url]["last_try"] = None
            self.page_timestamps[bitcoin_url]["last_success"] = None
        if timestamp != self.page_timestamps[bitcoin_url]["last_success"]:
            item = WaybackURL()
            item["timestamp"] = timestamp
            item["wayback_url"] = url
            item["bitcoinirc_url"] = bitcoin_url
            self.page_timestamps[bitcoin_url]["last_success"] = timestamp
            self.page_timestamps[bitcoin_url]["last_try"] = timestamp
            yield item
            
        url_timestamp = search("&timestamp=([0-9]+)", response.url)
        if url_timestamp:
            last_try = datetime.datetime.strptime(url_timestamp.group(1),
                                                  "%Y%m%d%H%M%S")
            self.page_timestamps[bitcoin_url]["last_try"] = last_try
            
        last_try = self.page_timestamps[bitcoin_url]["last_try"]
        if EARLIEST < last_try:
            next_time = last_try - datetime.timedelta(weeks = 1)
            time_param = "&timestamp=" + next_time.strftime("%Y%m%d%H%M%S")
            request_url = WAYBACK_API_URL + bitcoin_url + time_param
            pdb.set_trace()
            yield Request(request_url)
        
