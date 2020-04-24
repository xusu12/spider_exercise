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

from Crawler.BaseCrawler import BaseCrawler
from Crawler.keywordParser import KwParser
from conf.setting import BASE_TYPE
from conf.setting import KEYWORD_T_NUM
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import KeyWordQueue
from utils.util import IpQueue
from utils.util import DataQueue
from utils.util import UrlQueue
from utils.util import CookQueue
from Crawler.DataOutput import DataOutput
from utils.decorator import timer


class KwCrawler(BaseCrawler, Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Thread.__init__(self)
        self.url_type = 'keyword'

    # 根据要翻的页数, 抓取翻页链接(暂时没用这种方式)
    def get_page_url(self, html_code, page, keyword, Next=False):
        '''page 为指定要抓的页面'''
        url = KwParser.get_search_page_url(html_code, page, Next=Next)
        # 第二页url
        if '’' in keyword:
            keyword = "'".join(keyword.split('’'))

        qid = int(time.time())
        if not url:
            url = 'http://www.amazon.com/s/ref=sr_pg_2?rh=i%%3Aaps%%2Ck%%3A%s&page=2&keywords=%s&ie=UTF8&qid=%s' % (
                keyword, keyword, qid)
        # if url:
        #     qid = int(time.time())
        #     url = re.sub('qid=\d+', 'qid=%s' % (qid), url)
        #     url1 = re.sub('sr_pg_\d+\?', 'sr_pg_2?', url)
        #     url2 = re.sub('page=\d+\&', 'page=2&', url1)
        #     result = url2
        # else:
        #     url = 'http://www.amazon.com/s/ref=sr_pg_2?rh=i%%3Aaps%%2Ck%%3A%s&page=2&keywords=%s&ie=UTF8&qid=%s"' % (keyword, keyword, qid)
        #     result = url
        result = url

        return result

    # 获取翻页url
    def get_page_url_list(self, url, pageNum):
        page_url_list = []
        page_url_list.append(url)
        print(len(page_url_list), 'page_url_list: ', page_url_list)
        if pageNum >= 3:
            for i in range(3, pageNum + 1):
                page_url = self.make_page_url(url, i)
                if page_url:
                    page_url_list.append(page_url)
        print(len(page_url_list), 'page_url_list: ', page_url_list)
        return page_url_list

    # 获取要翻页的页码
    def get_page_num(self, resultSum, search_num):
        page_num = 0
        print('resultSum', resultSum)
        if search_num > 55:
            if type(resultSum) is int:
                page_num = ceil(55 / resultSum)
                print('page_num', page_num)
        else:
            page_num = ceil(search_num / resultSum)
        return page_num

    def make_page_url(self, url, page):
        time.sleep(1)
        qid = int(time.time())
        url = re.sub('qid=\d+', 'qid=%s' % (qid), url)
        print('make_page_url.url: ', url, qid)
        url1 = re.sub('sr_pg_\d+\?', 'sr_pg_%s?' % (page), url)
        url2 = re.sub('page=\d+\&', 'page=%s&' % (page), url1)
        return url2

    # 下载关键词页面
    def get_page_html(self, page_url, ua, ip, cookie, referer):
        page_html, cookies, page_is_error = self.get_html(page_url, ua, ip, cookie, referer)
        self.url_list.append(page_url)
        self.html_list.append(page_html)
        self.is_error_list.append(page_is_error)
        if cookies:
            self.cookies = cookies

    # 翻页下载逻辑
    def get_keyword_html_lsit(self, url, ua, ip, cookie, referer, kw=''):
        self.html_list = []
        self.url_list = []
        self.is_error_list = []
        self.cookies = None
        self.not_found = False
        print('get_keyword_html_list.url: ', url)
        html_code, cookiesObj, is_error = self.get_html(url, ua, ip, cookie, referer)
        if KwParser.has_not_found_keyword(html_code):
            self.html_list.append(html_code)
            self.url_list.append(url)
            self.cookies = cookiesObj
            self.is_error_list.append(is_error)
            resultList = KwParser.get_results_tag(html_code)
            search_num = KwParser()._get_search_num(html_code)
            print('get_keyword_html_lsit.search_num: ', search_num)
            resultSum = len(resultList)
            if resultSum > 0:
                page_url_list = []
                print(kw, 'keyword one page resultSum: ', resultSum)
                page_num = self.get_page_num(resultSum, search_num)
                print('page_num: ', page_num)
                # 大于1才需要翻页
                if page_num > 1:
                    page_url2 = self.get_page_url(html_code, 2, kw)
                    print('page_url2', page_url2)
                    page_url_list = self.get_page_url_list(page_url2, page_num)

                print(len(page_url_list), 'keyword page url list: ', page_url_list)
                # tList = []
                # tStart = 0
                # 遍历下载关键字
                if len(page_url_list) > 0:
                    i = 0
                    referer = url
                    # for page_url in page_url_list[1:len(page_url_list)]:
                    for page_url in page_url_list:
                        i += 1
                        print('keyword page%s: [%s]' % (i, page_url))
                        print('keyword referer %s: [%s]' % (i, referer))
                        self.get_page_html(page_url, ua, ip, None, referer)
                        referer = page_url
        else:
            self.not_found = True
        print('html_list_len', len(self.html_list), self.url_list, self.is_error_list)
        return self.html_list, self.url_list, self.cookies, self.is_error_list

    # 解析源码
    def kw_parser(self, html_list, kw, cid, ip='', url=''):
        '''只写了商品、评论、跟卖, 其余模块根据需要覆写此方法'''
        result = ()
        is_error = False
        try:
            kwData_dict = KwParser().kw_parser(html_list, kw, cid)
            result = (kwData_dict,)
        except Exception as e:
            self.debug_log.error('[%s]parser_keyword 解析 [%s] 时 [%s]' % (ip, url, e))
            is_error = True
        return result, is_error

    # 下载逻辑
    @timer
    def download(self, ip, asin_or_kw, url_dict):
        time_now = lambda: time.time()
        url_type = self.url_type
        kw = asin_or_kw
        cid = url_dict.get('cid') or 0
        print(ip, kw, cid, url_dict)
        # time.sleep(30)
        kw_url =  self.make_search_url(kw, cid)
        url = kw_url
        print('\nkeyword_url_tuple: ', kw_url)
        self.debug_log.debug(
            'url_type: %s, asin: %s, monitor_type: %s, url %s: ' % (url_type, kw, cid, url))
        if url:
            self.debug_log.debug('[ip %s] 工作中... [%s]' % (ip, url))
            startTime = return_PST().strftime("%Y-%m-%d %H:%M:%S")
            time1 = time_now()
            referer = 'https://www.amazon.com'
            self.debug_log.debug('keyword referer: %s' % (referer))
            ua = self.get_ua()
            self.debug_log.debug('keyword ua: %s' % (ua))
            # value_str = ip + ua
            # self.debug_log.debug('keyword value_str: %s' % (value_str))
            url_md5key = url_dict.get('md5') or ''
            if not url_md5key:
                url_md5key = self.get_md5_key(kw + url_type)
            # cookMd5key = self.get_md5_key(value_str)
            cookMd5key = None
            cookie = self.get_cookie(cookMd5key)
            self.debug_log.debug('keyword cookie: %s' % (cookie))
            # 下载url
            html_list, url_list, cookiesObj, is_error_lsit = \
                self.get_keyword_html_lsit(url, ua, ip, cookie, referer, kw=kw)
            old_dnum = url_dict.get('dnum') or 0
            durl = url_dict.get('durl') or []
            url_dict['durl'] = list(set(durl + url_list))
            url_dict['dnum'] = old_dnum + 1
            # 如果判定为没有关键词, 结束程序
            if self.not_found:
                DataOutput.record_not_found_keyword(kw)
                self.dataQ.record_keyword_not_fund_times()
                msgInt = 0
                proxyInfo = 'the keyword not found'
                self.record_log(kw, time1, msgInt, url_type, startTime, ip, proxyInfo)
                return self.debug_log.war('%s关键字不存在' % (kw))
            i = -1
            keyword_html_list = []
            if len(html_list) > 0:
                for html in html_list:
                    i += 1
                    is_error = is_error_lsit[i]
                    url = url_list[i]
                    if is_error:
                        msgInt = 6
                        proxyInfo = 'get Html error'
                        self.record_log(kw, time1, msgInt, url_type, startTime, ip, proxyInfo)

                    else:
                        analyze = self.analyze_html(html, cookie, cookiesObj, ip, kw, url_dict, cookMd5key, time1, startTime, html_type=url_type)
                        if analyze and analyze != 404:
                            keyword_html_list.append(html)
                if len(html_list) == len(keyword_html_list):
                    result, is_error = self.kw_parser(keyword_html_list, kw, cid, ip=ip, url=url)
                    if is_error:
                        msgInt = 3
                        proxyInfo = 'get data error'
                        self.record_log(kw, time1, msgInt, url_type, startTime, ip, proxyInfo)
                    else:
                        if not result:
                            self.the_url_is_discard(kw, url_dict, url_type, url_md5key)
                            msgInt = 2
                            proxyInfo = 'get data defeated'
                            self.record_log(kw, time1, msgInt, url_type, startTime, ip, proxyInfo)
                        else:
                            self.save_success_asin_keyword(kw, url_type=url_type)
                            msgInt = 1
                            proxyInfo = 'get data success'
                            self.record_log(kw, time1, msgInt, url_type, startTime, ip, proxyInfo)
                            keyword_datas = result[0]
                            data_bytes = pickle.dumps(keyword_datas)
                            self.dataQ.add_keyword_to_queue(data_bytes)
                            self.dataQ.record_data_ok_times()
                            self.dataQ.record_keyword_ok_times()
                else:
                    self.the_url_is_discard(kw, url_dict, url_type, url_md5key)
            else:
                self.the_url_is_discard(kw, url_dict, url_type, url_md5key)

            time.sleep(1)
        else:
            print(url_type, '没有url')
            self.add_url_to_set(url_dict, url_type, retry_type=True)
            time.sleep(1)


# worker调用
def keyword_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log, i):
    debug_log.debug('\nkeyword_start%s 启动成功' % (i))
    t_num = KEYWORD_T_NUM
    if BASE_TYPE == 'develop':
        t_num = 1
    while True:
        urllen1 = kwQ.return_keyword_len()
        urllen2 = kwQ._get_queue_len('monitorKeyword')
        urllen = urllen1 + urllen2
        if urllen < 1:
            sys.exit()
        crawlers = [KwCrawler(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log) for i in range(t_num)]
        for craw in crawlers:
            craw.start()
        for craw in crawlers:
            craw.join()


if __name__ == '__main__':
    log_name = sys.argv[0].split('/')[-1].split('.')[0]
    debug_log = Logger(log_name=log_name)
    info_log = Logger(log_level='info', log_name=log_name)
    myRedis = GetRedis().return_redis(debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    ipQ = IpQueue(myRedis, debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    cookiesQ = CookQueue(myRedis, debug_log)
    keyword_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log, 1)    # keyword_start()
