import scrapy


# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class GoogleSpider(CrawlSpider):
    name = "plays"
    allowed_domains = ["play.google.com"]
    start_urls = [
        # 'http://play.google.com/',
        'https://play.google.com/store/apps/details?id=com.viber.voip'
    ]
    rules = [
        Rule(LinkExtractor(allow=("https://play\.google\.com/store/apps/details",)), callback='parse_app', follow=False),
    ]  # CrawlSpider 会根据 rules 规则爬取页面并调用函数进行处理

    def parse_app(self, response):
        # 在这里只获取页面的 URL 以及下载数量
        item = {}
        item['url'] = response.url
        item['num'] = response.xpath("//div[@itemprop='numDownloads']").xpath("text()").extract()
        print(item)
