# -*- coding: utf-8 -*-
import time
from copy import deepcopy

import scrapy


class ZhiweiSpider(scrapy.Spider):
    name = 'zhiwei'
    allowed_domains = ['zhipin.com']
    start_urls = ['https://www.zhipin.com/c101280100/y_4-h_101280100/?query=python&ka=sel-salary-4']

    def parse(self, response):
        # 页面上所有的职位信息的div
        divs = response.xpath('//*[@id="main"]/div/div[2]/ul/li/div')

        for div in divs:
            item = {}
            item['name'] = div.xpath('./div[1]/h3/a/div/text()').extract_first()
            item['detail_url'] = 'https://www.zhipin.com'+div.xpath('./div[1]/h3/a/@href').extract_first()
            item['salary'] = div.xpath('./div[1]/h3/a/span/text()').extract_first()
            item['company'] = div.xpath('./div[2]/div/h3/a/text()').extract_first()

            time.sleep(1)
            # 获取详情页的信息
            yield scrapy.Request(item['detail_url'], callback=self.parse_detail, meta={'item': item})

        # 获取下一页的url
        next_url = 'https://www.zhipin.com' + response.xpath('//a[@class="next"]/@href').extract_first()
        print(next_url)
        # time.sleep(2)
        yield scrapy.Request(next_url, self.parse)

    def parse_detail(self, response):
        item = response.meta['item']

        # 获取详情页的信息
        # sec = response.xpath('//div[@class="detail-content"]/div[3]/div/text()').extract()
        sec = response.xpath('//div[@class="detail-content"]//h3[text()="职位描述"]/following-sibling::div/text()').extract()
        job_sec = ''
        for i in sec:
            job_sec = job_sec + i.strip()

        item['job_sec'] = job_sec
        # item['adress'] = response.xpath('//*[@id="main"]/div[3]/div/div[2]/div[3]/div[6]/div/div[1]/text()').extract_first()
        item['adress'] = response.xpath('//div[@class="detail-content"]//h3[text()="工作地址"]/following-sibling::div[1]/div[1]/text()').extract_first()
        print(item)
        yield item