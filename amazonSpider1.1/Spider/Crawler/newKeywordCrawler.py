#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
import re
import time
import pickle
from math import ceil
from threading import Thread

from utils.util import Logger
from utils.util import GetRedis
from utils.util import KeyWordQueue
from utils.util import IpQueue
from utils.util import DataQueue
from utils.util import UrlQueue
from utils.util import CookQueue
from Crawler.keywordCrawler import KwCrawler


class NewKwCrawler(KwCrawler, Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Thread.__init__(self)

    # 从redis队列读取关键字以及搜索类型
    def get_keyword(self, retry=10):
        if retry < 1:
            return '', {}
        url_type = 'keyword'
        timeout = 10
        monitor_name = 'monitorKeyword'    # 'KeywordQueue'
        result = None
        kw_dict = ()
        overtime = 30
        if self.kwQ._get_queue_len(monitor_name) > 0:
            result1 = self.kwQ._get_member_from_queue(monitor_name, timeout)
            if not result1:
                return '', {}
            result = result1[1]
            if not result:
                return '', {}
            kw_dict = pickle.loads(result)
            if not kw_dict:
                return '', {}
            kw = kw_dict.get('kw') or ''
            if not kw:
                return '', {}
            r = re.compile('[\u4e00-\u9fa5]+')
            k = r.search(kw)
            if k:
                return self.get_keyword(retry=retry - 1)
            used = 'useInterval'
            md5key = self.get_md5_key(kw + url_type + used)
            is_used = self.kwQ._get_value_from_string(md5key, used)
            if not self.is_download(kw, url_type):
                if is_used and kw:
                    self.add_sleep_url(kw_dict, url_type=url_type, retry_type=True)
                    print('url休眠中 %s %s' % (kw, url_type))
                    time.sleep(0.1)
                    return self.get_keyword(retry=retry - 1)
                # 如果没下载
                # 设置一个时间间隔
                self.kwQ._set_key_value_to_string(md5key, used, used, overtime=overtime)
                return kw, kw_dict
            else:
                time.sleep(0.1)
                return self.get_keyword(retry=retry - 1)

        else:
            return '', {}

    def run(self):
        asin_or_kw, url_dict = self.get_keyword()
        asin_kw_verify = url_dict.get('kw') or ''
        if asin_or_kw and asin_or_kw == asin_kw_verify:
            self.crawler(asin_or_kw, url_dict)


def keyword_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log, i=0):
    debug_log.debug('\nkeyword_start%s 启动成功' % (i))
    monitor_name = 'monitorKeyword'  # 'KeywordQueue'
    while True:
        urllen = urlQ._get_queue_len(monitor_name)
        print('当前NewUrl队列长度: %s' % (urllen))
        if urllen < 1:
            time.sleep(10)
            break
        spiderNum = ceil(urllen / 10)
        if spiderNum > 10:
            spiderNum = 10 
        print('需要开启的线程数: ', spiderNum)
        spider_list = [NewKwCrawler(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log) for i in range(spiderNum)]
        i = 0
        for spider in spider_list:
            i += 1
            spider.start()
        for spider in spider_list:
            spider.join()


if __name__ == '__main__':
    debug_log = Logger()
    info_log = Logger('info')
    myRedis = GetRedis().return_redis(debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    ipQ = IpQueue(myRedis, debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    cookiesQ = CookQueue(myRedis, debug_log)
    keyword_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log)
