#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
# from os import cpu_count
import re
import time
import pickle
from math import ceil
from threading import Thread
from datetime import timedelta

from Crawler.BaseCrawler import BaseCrawler
from Crawler.reviewsParser import ReviewsParser
from Crawler.DataOutput import DataOutput
from utils.util import return_PST
from conf.setting import BASE_TYPE
from conf.setting import REVIEWS_T_NUM

from utils.util import Logger
from utils.util import GetRedis
from utils.util import IpQueue
from utils.util import DataQueue
from utils.util import UrlQueue
from utils.util import CookQueue
from utils.util import KeyWordQueue
from utils.decorator import timer


class ReviewsCrawler(BaseCrawler, Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Thread.__init__(self)
        self.url_type = 'reviews'

    # 根据asin与页数生成翻页url
    def make_page_url(self, asin, page):
        url = ReviewsParser.make_reviews_page_url(asin, page)
        return url

    # 获取翻页url
    def get_page_urls(self, asin, reviewsSum, frist=0):
        page_url_lsit = []
        pageNum = 0

        # 如果是第一次
        if frist == 1:
            pageNum = 10
            thePageNum = reviewsSum / 10
            if thePageNum < 9:
                pageNum = ceil(thePageNum)

        # 如果不是第一次
        if frist == 0:
            pageNum = 10
            thePageNum = reviewsSum / 10
            if thePageNum < 9:
                pageNum = ceil(thePageNum)

        url_type = 'reviews'
        if pageNum >= 2:
            for i in range(2, pageNum + 1):
                url = self.make_page_url(asin, i)
                page_url_lsit.append(url)
        return page_url_lsit

    def get_page_html(self, page_url, ua, ip, cookie, referer):
        page_html, cookies, page_is_error = self.get_html(page_url, ua, ip, cookie, referer)
        self.url_list.append(page_url)
        self.html_list.append(page_html)
        self.is_error_list.append(page_is_error)
        if cookies:
            self.cookies = cookies

    # 判断是否不需要翻页
    def is_not_turn_the_page(self, first, html, page_num=0, asin=''):
        '''
        判断规则, 如果不第一次下载, 单页内出现前一天的评论, 则判断为不需要翻页了.
        如果是第一次下载, 单页内出现三个月以前的评论, 也判断不再需要翻页.
        '''
        reviews_date_list = ReviewsParser.get_reviews_date_list(html)
        datetime = return_PST()
        min_reviews_date = min(reviews_date_list) if len(reviews_date_list) > 0 else int(datetime.strftime('%Y%m%d'))
        oldDate = datetime - timedelta(days=90)
        yesterdate = datetime - timedelta(days=1)
        yesterday = yesterdate.strftime('%Y%m%d')
        theYesterDete = int(yesterday)
        theMon = oldDate.strftime('%Y%m%d')
        three_mon_date = int(theMon)
        print('\n%s: min_reviews_date: %s\ntheYesterDete: %s\nthree_mon_date: %s\n' % (asin, min_reviews_date, theYesterDete, three_mon_date))
        # 如果不是第一次下载
        if not first:
            if min_reviews_date < theYesterDete:
                print('%s < %s' % (min_reviews_date, theYesterDete))
                print('非第一次下载, 当前是%s的第%s页评论, 不再需要继续翻页' % (asin, page_num))
                return True
            else:
                print('是第一次下载, 当前是%s的第%s页评论, 还需要继续翻页' % (asin, page_num))
                return False
        else:
            if min_reviews_date < three_mon_date:
                print('%s < %s' % (min_reviews_date, three_mon_date))
                print('非第一次下载, 当前是%s的第%s页评论, 不再需要继续翻页' % (asin, page_num))
                return True
            else:
                print('非第一次下载, 当前是%s的第%s页评论, 还需要继续翻页' % (asin, page_num))
                return False

    def looking_something(self, html_code):
        not_found_patterns = [
            re.compile('The Web address you entered is not a functioning', re.S),
            re.compile('Looking for something', re.S),
        ]
        not_found = ReviewsParser.get_new_data(pattern_list=not_found_patterns, html_code=html_code)
        if len(not_found) > 0:
            return True
        return False

    def get_reviews_url_asin(self, goods_html):
        result = ''
        xpath_list = [
            '//*[text()="Customer Reviews"]/../..//a[contains(text(), "customer reviews")]/@href',
        ]
        result_list = ReviewsParser.get_new_data(xpath_list=xpath_list, html_code=goods_html)
        if len(result_list) > 0:
            pattern_list = [
                re.compile('product-reviews/([A-Za-z0-9]{10,10})/ref'),
            ]
            result_list1 = ReviewsParser.get_new_data(pattern_list=pattern_list, html_code=result_list[0])
            if len(result_list1) > 0:
                result = result_list1[0]
        print('get_reviews_url.result: ', result)
        return result

    # 翻页下载评论
    def get_reviews_html_list(self, asin, url, ua, ip, cookie, referer):
        self.html_list = []
        self.url_list = []
        self.is_error_list = []
        self.cookies = None
        print(url, ua)
        # url = 'https://www.amazon.com/product-reviews/B000TZ8TEU/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent'
        html, cookiesObj, is_error = self.get_html(url, ua, ip, cookie, referer)
        reviewsUrl = ''
        url_asin = asin
        if self.looking_something(html) or not html:
            goodsUrl_tuple = self.make_url(asin, url_type='goods')
            goodsUrl, goodsReferer = goodsUrl_tuple[0], goodsUrl_tuple[1]
            print('get_reviews_html_list.goodsUrl: ', goodsUrl)
            goods_html, cookiesObj, is_error = self.get_html(goodsUrl, ua, ip, cookie, goodsReferer, url_type=self.url_type, asin=asin)
            url_asin = self.get_reviews_url_asin(goods_html)
            reviewsUrl = self.make_url(url_asin, url_type=self.url_type)[0]
            # print(reviewsUrl, goodsUrl)
            if not reviewsUrl:
                DataOutput.record_not_found_reviews(asin)
                self.is_error_list.append(404)
                return self.html_list, self.url_list, self.cookies, self.is_error_list

        if reviewsUrl:
            print('%s get_reviews_html_list.reviewsUrl: ' % (asin), reviewsUrl)
            goodsUrl_tuple = self.make_url(url_asin, url_type='goods')
            goodsUrl = goodsUrl_tuple[0]
            html, cookiesObj, is_error = self.get_html(reviewsUrl, ua, ip, cookie, goodsUrl, url_type=self.url_type, asin=asin)

        if ReviewsParser.is_page_not_found(html) :
            DataOutput.record_not_found_reviews(asin)
            self.is_error_list.append(404)
            return self.html_list, self.url_list, self.cookies, self.is_error_list

        if cookiesObj and not cookie:
            cookie = cookiesObj
        self.url_list.append(url)
        self.html_list.append(html)
        self.is_error_list.append(is_error)
        md5value = asin + 'reviewsFirst'
        md5key = self.get_md5_key(md5value)
        first = dataQ.is_first_download(md5key)
        # 先获取评论总数
        reviewsSum = ReviewsParser.get_review_count(html)
        print('reviewsSum: ', reviewsSum, asin)
        if reviewsSum > 10:
            # 如果不需要翻页, 则直接return, 减少没必要的网络请求
            if self.is_not_turn_the_page(first, html, page_num=1, asin=asin):
                return self.html_list, self.url_list, cookie, self.is_error_list
            # 如果是第一次下载评论 review:  ['174']
            if first:
                is_frist = 1
            else:
                is_frist = 0

            # 获取翻页url
            page_url_list = self.get_page_urls(url_asin, reviewsSum, frist=is_frist)

            tList = []
            tStart = 0
            # 遍历下载评论(多线程)
            if page_url_list:
                i = 1
                j = 1
                referer = url
                for page_url in page_url_list:
                    i += 1
                    j += 1
                    print('reviews page%s: [%s]' % (i, page_url))
                    print('referer %s: [%s]' % (i, referer))
                    self.get_page_html(page_url, ua, ip, None, referer)
                    referer = page_url
                    for html in self.html_list:
                        if self.is_not_turn_the_page(first, html, page_num=j, asin=asin):
                            return self.html_list, self.url_list, cookie, self.is_error_list

        return self.html_list, self.url_list, self.cookies, self.is_error_list

    @timer
    def download(self, ip, asin_or_kw, url_dict):
        time_now = lambda: time.time()
        url_type = self.url_type
        print('reviewsCrawler_download.url type: ', url_type)
        asin = asin_or_kw
        print('reviewsCrawler_download.asin', asin)
        monitor_type = url_dict.get('mtp') or 3
        url_md5key = url_dict.get('md5') or ''
        if not url_md5key:
            url_md5key = self.get_md5_key(asin + url_type)
        print('url_type: %s, asin: %s, monitor_type: %s: ' % (url_type, asin, monitor_type))
        urltitle = urlQ.get_urlTitle_from_string(asin)
        url = self.make_url(asin, url_type=url_type, urltitle=urltitle)[0]
        #url = 'https://www.amazon.com/product-reviews/%s/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1' % (asin)
        if url:
            self.debug_log.debug('[ip %s] 工作中... [%s]' % (ip, url))
            startTime = return_PST().strftime("%Y-%m-%d %H:%M:%S")
            time1 = time_now()
            ua = self.get_ua()
            self.debug_log.debug('reviews ua: %s' % (ua))
            # value_str = ip + ua
            # self.debug_log.debug('reviews value_str: %s' % (value_str))
            # cookMd5key = self.get_md5_key(value_str)
            cookMd5key = None
            cookie = self.get_cookie(cookMd5key)
            self.debug_log.debug('reviews cookie: %s' % (cookie))
            # sessionId = ''
            # if cookie:
            #     sessionId = cookie.get('session-id') or ''
            referer = self.make_url(asin, url_type='goods')[0]
            self.debug_log.debug('reviews referer: %s' % (referer))
            html_list, url_list, cookiesObj, is_error_lsit = self.get_reviews_html_list(asin, url, ua, ip, cookie, referer)
            i = -1
            is_not_found = None
            if len(is_error_lsit) > 0:
                is_not_found = is_error_lsit[0]
            if is_not_found != 404:
                reviews_data_list = []
                for html in html_list:
                    i += 1
                    is_error = is_error_lsit[i]
                    url = url_list[i]
                    if is_error:
                        self.the_url_is_discard(asin, url_dict, url_type, url_md5key)
                        msgInt = 6
                        proxyInfo = 'get Html error'
                        self.record_log(asin, time1, msgInt, url_type, startTime, ip, proxyInfo)

                    else:
                        analyze = self.analyze_html(html, cookie, cookiesObj, ip, asin, url_dict,
                                                    cookMd5key, time1, startTime, html_type=url_type)
                        if analyze and analyze != 404:
                            result, is_error = self.parser(html, html_type=url_type, asin=asin, ip=ip,
                                                           monitor_type=monitor_type)
                            if is_error:
                                self.the_url_is_discard(asin, url_dict, url_type, url_md5key)
                                msgInt = 3
                                proxyInfo = 'get data error'
                                self.record_log(asin, time1, msgInt, url_type, startTime, ip, proxyInfo)
                            else:
                                if not result:
                                    self.the_url_is_discard(asin, url_dict, url_type, url_md5key)
                                    msgInt = 2
                                    proxyInfo = 'get data defeated'
                                    self.record_log(asin, time1, msgInt, url_type, startTime, ip, proxyInfo)
                                else:
                                    msgInt = 1
                                    proxyInfo = 'get data success'
                                    self.record_log(asin, time1, msgInt, url_type, startTime, ip, proxyInfo)
                                    reviews_data_list.append(result[0])
                                    self.dataQ.record_data_ok_times()
                                    self.dataQ.record_reviews_ok_times()
                if reviews_data_list:
                    data_list = []
                    for data in reviews_data_list:
                        for item in data:
                            data_list += data[item]
                    print('reviews data_list', asin, len(data_list), data_list)
                    reviews_datas = {asin: data_list}
                    self.save_success_asin_keyword(asin, url_type=url_type)
                    data_bytes = pickle.dumps(reviews_datas)
                    self.dataQ.add_reviews_to_queue(data_bytes)
                else:
                    self.the_url_is_discard(asin, url_dict, url_type, url_md5key)
                    time.sleep(1)

        else:
            print(url_type, '没有url')
            self.the_url_is_discard(asin, url_dict, url_type, url_md5key)
            time.sleep(1)


def reviews_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log, i):
    debug_log.debug('\nreviews_start%s 启动成功' % (i))
    t_num = REVIEWS_T_NUM
    if BASE_TYPE == 'develop':
        t_num = 1
    while True:
        urllen1 = urlQ.retrieve_reviewsUrl_len()
        urllen2 = urlQ._get_queue_len('monitorReviews')
        urllen = urllen1 + urllen2
        if urllen < 1:
            sys.exit()
        crawlers = [ReviewsCrawler(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log) for i in range(t_num)]
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
    reviews_start(urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log, 1)
