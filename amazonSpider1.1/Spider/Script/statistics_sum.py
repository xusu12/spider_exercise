#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import re
import os
import time

from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue


# 获得更新时间戳
def get_init_updae_tm(theQueue):
    tm_key = 'initUpdateTm'
    key_type = 'updateTime'
    tm_value = theQueue._get_value_from_string(tm_key, key_type)
    if tm_value:
        result1 = str(tm_value, encoding='utf-8')
        if re.match('^1[0-9]{9}$', result1):
            return int(result1)
    with open('%s.tm' % tm_key, 'r', encoding='utf-8') as f:
        tm = f.readline()
        if re.match('^1[0-9]{9}$', tm):
            return int(tm)


# 关键字统计
def keyword_retry(kwQ):
    url_type = 'keyword'
    sql = "select kw from public.amazon_keyword_monitor where state = 1 and monitor_tm > 0;"
    url_tuple_list = kwQ.retrieve_asin(sql)
    print('关键字数 %s' % (len(url_tuple_list)))
    print('(去重)关键字数 %s' % (len(set(url_tuple_list))))
    # print('keyword_retry: ', url_tuple_list)


# 商品统计
def goods_retry(urlQ):
    url_type = 'goods'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and info_tm > 0 ;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('商品数 %s' % (len(url_tuple_list)))
    print('(去重)商品数 %s' % (len(set(url_tuple_list))))


# 评论统计
def reviews_retry(urlQ):
    url_type = 'reviews'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 3 and monitor_type != 5 and comment_tm > 0 ;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('评论数 %s' % (len(url_tuple_list)))
    print('(去重)评论数 %s' % (len(set(url_tuple_list))))


# 跟卖统计
def tosell_retry(urlQ):
    url_type = 'tosell'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 ;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('跟卖数 %s' % (len(url_tuple_list)))
    print('(去重)跟卖数 %s' % (len(set(url_tuple_list))))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    goods_retry(urlQ)
    keyword_retry(urlQ)
    tosell_retry(urlQ)
    reviews_retry(urlQ)
    #qty_retry(urlQ)
