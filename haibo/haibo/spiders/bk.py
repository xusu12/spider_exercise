# -*- coding: utf-8 -*-
import json

import scrapy


class BkSpider(scrapy.Spider):
    name = 'bk'
    allowed_domains = ['studyboos.xyz']
    start_urls = ['http://studyboos.xyz/Study/']

    def parse(self, response):
        url = 'http://studyboos.xyz/Study/userStudy/searchSolr.do'

        data = {
            'pageNo': 1,
            'pageSize': 13
        }

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "http://studyboos.xyz/Study/"

        }

        yield scrapy.Request(url,
                             method="POST",
                             headers=headers,
                             body=json.dumps(data),
                             # json = data,
                             callback=self.parse_li,
                             dont_filter=True)

    def parse_li(self, response):
        data = json.loads(response.text)

        for row in data['rows']:

            print(row['title'])