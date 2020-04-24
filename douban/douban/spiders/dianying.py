# -*- coding: utf-8 -*-
import scrapy
from tasks import download_pic
# from douban import download_pic


class DianyingSpider(scrapy.Spider):
    name = 'dianying'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        print(response.url)
        # 提取a标签的列表
        lis = response.xpath('//*[@id="content"]/div/div[1]/ol/li')
        i = 0
        for li in lis:
            i+=1
            item = {}
            item['name'] = li.xpath('.//div[@class="info"]//a/span[1]').extract_first()
            item['pic'] = response.urljoin(li.xpath('.//div[@class="pic"]/a/img/@src').extract_first())
            print(item)


            # 调用celery异步任务的方法  下载图片
            download_pic.delay(item['pic'], './douban/img/pic{}.jpg'.format(i))
