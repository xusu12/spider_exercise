# -*- coding: utf-8 -*-
import scrapy
import json


class YouzuspiderSpider(scrapy.Spider):
    name = 'YouzuSpider'
    allowed_domains = ['178all.com', 'dev.178all.com']
    start_urls = ['http://www.178all.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Language': 'zh - CN, zh;q = 0.9',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://dev.178all.com/Packagedata'

    }

    # def start_requests(self):
    #     url = 'http://www.178all.com/gamecenter'  # AJAX
    #     return [scrapy.FormRequest(url=url, headers=self.headers, callback=self.parse_before_login)]
    #
    # def parse_before_login(self, response):
    #     print("---------------填写登录表单-----------------")
    #
    #     formdata = {
    #         'username': 'hejianmei@139.com',
    #         'password': '20161130'
    #     }
    #     print("登录中...........................................")
    #     return scrapy.FormRequest.from_response(response, formdata=formdata, headers=self.headers, callback=self.parse)

    # def parse(self, response):
    def start_requests(self):
        # print('登录成功！')
        #
        # Cookie = response.request.headers.getlist('Cookie')
        # print(Cookie)

        url = 'http://dev.178all.com/Packagedata/Update'
        dataform = {
            'gid': '196377355',
            'showType': '1',
            'star': '开始日期',
            'end': '结束日期',
            'cpsid[]': ['196377355_50_1480558197', '196377355_50_1494217282', '196377355_50_1494229508',
                      '196377355_50_1500624428']
            # 'cpsid[]': '196377355_50_1480558197'
            # 'cpsid[]': '196377355_50_1494217282',
            # 'cpsid[]': '196377355_50_1494229508',
            # 'cpsid[]': '196377355_50_1500624428'
        }
        print(dataform)
        cookie = {
            # "PASS-TOKEN": "e7c14293d7b4e3df5aa9e4935ac770bc",
            # "checkedNum":196377355,
            "PHPSESSID":"vnfr4tneleldl1h992743hn2v7"

        }

        yield scrapy.FormRequest(url=url,
                                 headers=self.headers,
                                 formdata=dataform,
                                 cookies=cookie,
                                 callback=self.parse_after_login,
                                 dont_filter=True)

    def parse_after_login(self, response):
        print("统计数据表单填写...............................................")
        content = response.body.decode('utf-8')
        from pprint import pprint
        # pprint(content)
        data = "{"+content.split('"data":')[1]
        pprint(data)
        pprint(dict(data))
        content= ''.join(content)
        print("content: 打印保存数据", content)
        result = json.loads(content)  # str格式转为dict格式
        print("result: ", result)

        yield result
