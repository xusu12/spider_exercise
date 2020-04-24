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
    sql_times = get_init_updae_tm(kwQ)
    if sql_times:
        sql = "select kw from public.amazon_keyword_monitor where state = 1 and crawler_tm >= %s" % (
        sql_times)
        url_tuple_list = kwQ.retrieve_asin(sql)
        fail_sum = kwQ.RedisQ.zcard(url_type + 'fail')
        print('已下载关键字数 %s' % (len(url_tuple_list)))
        print('(去重)已下载关键字数 %s' % (len(set(url_tuple_list))))
        print('重试关键字数 %d' % (fail_sum))
        # print('keyword_retry: ', url_tuple_list)


# 商品统计
def goods_retry(urlQ):
    url_type = 'goods'
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and info_tm > 0 and info_tm_crawler >= %s" % (sql_times)
        url_tuple_list = urlQ.retrieve_asin(sql)
        sql1 = "select asin from public.amazon_product_data where asin_state=-1 and crawler_state=2 and sync_tm >= %s" % (sql_times)
        url_tuple_list1 = urlQ.retrieve_asin(sql1)
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        print('已下载商品数 %s' % (len(url_tuple_list)))
        print('(去重)已下载商品数 %s' % (len(set(url_tuple_list))))
        print('下载失败商品数 %s' % (len(url_tuple_list1)))
        print('(去重)下载失败商品数 %s' % (len(set(url_tuple_list1))))
        print('重试商品数 %d' % (fail_sum))


# 评论统计
def reviews_retry(urlQ):
    url_type = 'reviews'
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and comment_tm > 0 and comment_tm_crawler >= %s" % (sql_times)
        url_tuple_list = urlQ.retrieve_asin(sql)
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        print('已下载评论数 %s' % (len(url_tuple_list)))
        print('(去重)已下载评论数 %s' % (len(set(url_tuple_list))))
        print('重试评论数 %d' % (fail_sum))


# 跟卖统计
def tosell_retry(urlQ):
    url_type = 'tosell'
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        # sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and tosell_tm > 0 and tosell_tm_crawler >= %s" % (sql_times)
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 \
        and asin in (select asin from public.amazon_product_data_tosell where getinfo_tm > %s);" % (sql_times * 1000)
        url_tuple_list = urlQ.retrieve_asin(sql)
        sql1 = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 and \
        asin in (select asin from public.amazon_product_data where getinfo_tm > %s and asin_state = 0);" % (sql_times * 1000)
        url_tuple_list1 = urlQ.retrieve_asin(sql1)
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        print('已下载跟卖数 %s' % (len(url_tuple_list)))
        print('(去重)已下载跟卖数 %s' % (len(set(url_tuple_list))))
        print('已下架产品数 %s' % (len(set(url_tuple_list1))))
        print('重试跟卖数 %d' % (fail_sum))


# 库存统计
def qty_retry(urlQ):
    url_type = 'inventory'
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        sql = "select count(asin) from public.amazon_product_data where quantity = -1 and asin_state = 3 and getinfo_tm >= %s" % (sql_times * 1000)
        sql1 = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and info_tm > 0 and info_tm_crawler >= %s" % (sql_times)
        url_tuple_list1 = urlQ.retrieve_asin(sql)
        notQtyNum = url_tuple_list1[0][0]
        print('库存失败数 %s' % (notQtyNum))
        url_tuple_list2 = urlQ.retrieve_asin(sql1)
        qtySum = len(set(url_tuple_list2))
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        print('库存总数 %s' % (qtySum))
        # 库存成功数 = url_tuple_list2[0][0] - url_tuple_list1[0][0]
        print('库存成功数 %s' % (qtySum - notQtyNum))
        print('重试库存数 %d' % (fail_sum))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    goods_retry(urlQ)
    keyword_retry(urlQ)
    tosell_retry(urlQ)
    reviews_retry(urlQ)
    qty_retry(urlQ)
