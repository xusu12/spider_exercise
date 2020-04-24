import sys
import requests
import json
from Crawler.BaseCrawler import BaseCrawler
from utils.util import Logger, UaPond, GetRedis, UrlQueue
from conf.setting import GET_ASIN_DATA_API
from Crawler.goodsParser import GoodsParser
from Crawler.Downloader import get_html_useRequest
from functools import wraps

# 以当前文件的名称作为日志文件的名称　sys.argv[0]是获取当前模块的名字
log_name = sys.argv[0].split('/')[-1].split('.')[0]
debug_log = Logger(log_name=log_name)


# 通过查询数据库获取品牌信息
def get_brand_from_db(debug_log):
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    # TODO  传入一条ｓｑｌ语句
    brand = urlQ.retrieve_asin('')
    return brand


# 就通过api接口获取品牌信息
def get_brand_from_api(asin):
    api_url = GET_ASIN_DATA_API.format(asin)
    data = requests.get(api_url, verify=False)
    data_dict = json.loads(data.text)
    brand = data_dict['data']['brand']
    return brand


# 通过商品解析类中的方法获取商品的品牌信息
def get_brand_from_parser(asin, debug_log):
    # 根据asin获取url
    urls = BaseCrawler.make_url(asin)
    url = urls[0]
    refer = urls[1]
    # 获取ua
    ua = UaPond.get_new_ua()
    cookies = ''
    ip = ''
    ipQ = ''
    # 调用下载器方法获取页面数据
    html_data, cookie, is_error = get_html_useRequest(url, ua, ip, cookies, debug_log, refer, ipQ, url_type='goods',
                                                      asin=asin)
    # 调用商品解析的方法获取页面的品牌信息
    brand = GoodsParser(html_data)._get_brand()
    return brand


def get_brand(asin):
    # 1. 通过查询数据库获取品牌信息
    # TODO 查询数据库
    # brand = get_brand_from_db(debug_log)
    brand = ''

    # 2. 如果数据库中未能获取品牌信息　就通过api接口获取品牌信息
    if not brand:
        brand = get_brand_from_api(asin)

        # 3. 如果通过API未能获取品牌信息 就通过商品解析类中的方法获取商品的品牌信息
        if not brand:
            brand = get_brand_from_parser(asin, debug_log)
    return brand


def brand_patch(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        # 运行被装饰方法　　获取返回数据
        data_dict = func(*args, **kwargs)

        # 如果数据为空　直接返回
        if not data_dict:
            return data_dict

        # 返回数据的字典
        result_dict = {}
        data_list = []

        # result_dict拆包
        for key, value in data_dict.items():
            kw = key
            keyword_data_dict = value[0]
            keyword_druid_data_list = value[1]
            # 遍历获取列表中的每一条数据　判断brand是否为空　如果是　就重新获取brand数据写入列表
            for data in keyword_druid_data_list:
                if not data['brand']:
                    data['brand'] = get_brand(data['asin'])
                # 将更新后的每条数据添加进新的列表
                data_list.append(data)
            result_dict[kw] = (keyword_data_dict, data_list)
        return result_dict

    return wrap
