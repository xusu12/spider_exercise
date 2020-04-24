# -*- coding: utf-8 -*-
import json
import re
import js2py
import scrapy
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# import PyV8


class TpSpider(scrapy.Spider):
    name = 'tp'
    allowed_domains = ['toutiao.com']
    start_urls = ['https://www.toutiao.com/']

    def parse(self, response):
        # 创建Options对象
        options = Options()

        # set_headless: 设置无界面
        options.set_headless()

        # 设置成无界面模式
        driver = webdriver.Chrome()

        # 获取页面信息
        driver.get('https://www.toutiao.com/ch/news_image/')

        # 解析页面上的js代码  生成需要的参数
        ascp = driver.execute_script('return ascp.getHoney()')
        a_s = ascp['as']
        c_p = ascp['cp']
        s = driver.execute_script('return TAC.sign(0)')

        url = 'https://www.toutiao.com/api/pc/feed/?max_behot_time=0&as={}&cp={}&_signature={}'.format(a_s, c_p, s)

        print(url)
        time.sleep(100)
        yield scrapy.Request(url, callback=self.parse_li)

    def parse_li(self, response):
        print(response.text)
    #     item = {}
    #     text = json.loads(response.text)
    #     titles = re.findall(r"'title': '(.+?)'", str(text))
    #     ids = re.findall(r"'item_id': '(.+?)'", str(text))
    #     urls = []
    #     index = 0
    #     for i in ids:
    #         item = {}
    #         title = titles[index]
    #         item['title'] = title
    #         url = 'https://www.toutiao.com/'+'a'+i
    #         item['url'] = url
    #         print(item)
    #         index += 1
