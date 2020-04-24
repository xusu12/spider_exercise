# -*- coding: utf-8 -*-
import json
import time

import scrapy


class PlaySpider(scrapy.Spider):
    name = 'play'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/apps/collection/topselling_free?hl=zh-CN']

    def parse(self, response):
        divs = response.xpath('//*[@id="body-content"]/div/div/div[1]/div/div/div/div[2]/div')

        for div in divs:
            item = {}
            item['name'] = div.xpath('.//div[@class="details"]/a[@class="title"]/text()').extract_first()
            print(item)
            time.sleep(0.3)

        data = {
            # "start": 120,
            # "num": 60,
            # "numChildren": 0,
            # "cctcss": "square-cover",
            # "cllayout": "NORMAL",
            # "ipf": 1,
            # "xhr": 1,
            # "hl": "zh-CN"
        }

        headers = {
            "cache-control": "no-cache",
            # "content-length": 6000,
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "origin": "https://play.google.com",
            "pragma": "no-cache",
            "referer": "https://play.google.com/store/apps/collection/topselling_free?hl=zh-CN",
            "x-client-data": "CK+1yQEIhbbJAQiitskBCMS2yQEIqZ3KAQjYncoBCNqdygEIqKPKAQiCpMoB"
        }

        url = 'https://play.google.com/store/apps/collection/topselling_free?hl=zh-CN&authuser=0'


        yield scrapy.Request(url, method="POST", headers=headers, body=json.dumps(data), callback=self.parse,
                             dont_filter=True)

    def parse_apps(self, response):
        print(response.text)
        # with open('apps.html', 'w', encoding='utf8') as f:
        #     f.write(response.text)
