# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class CsmSpider(scrapy.Spider):
    name = 'csm'
    allowed_domains = ['61.146.213.163:8011']
    start_urls = [
        'http://61.146.213.163:8011/User_ItemList.aspx?lid=f96ea453-7c8f-488c-beb4-a696849bba06&page={}'.format(num) for num in range(1, 142)]

    def parse(self, response):

        item = {}

        alis = response.xpath('//td/a[@target="_blank"]/@href')

        for a in alis:
            item['项目url'] = 'http://61.146.213.163:8011/' + a

            yield scrapy.Request(url=item['项目url'], callback=self.parse_content, meta={'item': deepcopy(item)})

    def parse_content(self, response, meta):

        item = meta['item']
        if not response.text == "<script>alert('找不到该记录！');window.history.go(-1);</script>":
            # item = meta['item']

            item["证明书号"] = response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[1]/a/@title').extract_first() if response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[1]/a/@title') else " "
            item["座落"] = response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[2]/text()').extract_first() if response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[2]/text()') else " "
            item["项目名称"] = response.xpath('//*[@id="kfsmctd"]/a/text()').extract_first() if response.xpath(
                '//*[@id="kfsmctd"]/a/text()') else " "
            item["楼房信息"] = response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[2]/text()').extract_first() if response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[2]/text()') else " "
            item["楼盘分类"] = 'http://61.146.213.163:8011/' + response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[4]/a/@href').extract_first() if response.xpath(
                '//*[@id="selltable1"]/tbody/tr[2]/td[4]/a/@href') else " "
            item["楼盘url"] = item['项目url']
            item["合同样本信息"] = " " if response.xpath(
                '//*[@id="preselltable2"]/tbody/tr/td/text()').extract_first() == "此开发商没有预售楼盘项目或该预售项目暂未通过审核" else response.xpath(
                '//*[@id="preselltable2"]/tbody/tr/td/text()').extract_first()

            yield item

        item["状态"] = "找不到该记录！"

        yield
