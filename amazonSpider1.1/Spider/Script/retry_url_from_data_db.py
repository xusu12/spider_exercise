#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import re
import os
import time
import pickle
from threading import Thread
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue


def empty_url_queue(myRedis, Qname):
    r = myRedis
    i = 0
    while True:
        i += 1
        url = r.rpop(Qname)
        if not url:
            break
    print('\n已删除url %s\n' % (i))


# 将新增url, 加入队列
def add_url_to_queue(theQueue, url_tuple_list, url_type=''):
    used = 'useInterval'
    def add_to_queue(theQueue, url_tuple_bytes, url_type=''):
        result = False
        if url_type == 'goods':
            result = theQueue.add_goods_url_to_queue(url_tuple_bytes)
        if url_type == 'reviews':
            result = theQueue.add_reviews_url_to_queue(url_tuple_bytes)
        if url_type == 'tosell':
            result = theQueue.add_tosell_url_to_queue(url_tuple_bytes)
        if url_type == 'keyword':
            result = theQueue.add_keyword_to_queue(url_tuple_bytes)
        return result
    # print(url_tuple_list)
    url_data_dict = {}
    for urlTuple in url_tuple_list:
        # print(urlTuple)
        kw_asin = urlTuple[0]
        cid_monitorType = urlTuple[1]
        aid = urlTuple[2]
        md5value = kw_asin + url_type
        md5key = theQueue.get_md5_key(md5value)
        usedMd5key = theQueue.get_md5_key(md5value + used)
        url_dict = dict(
            aid=aid,
            md5=md5key,
            umd5=usedMd5key,
            utp=url_type,
        )
        if url_type == 'keyword':
            url_dict['kw'] = kw_asin
            url_dict['cid'] = cid_monitorType
        else:
            url_dict['asin'] = kw_asin
            url_dict['mtp'] = cid_monitorType
        if not url_data_dict.get(kw_asin):
            url_data_dict[kw_asin] = url_dict
    url_data_list = []
    for url in url_data_dict:
        url_data_list.append(url_data_dict[url])
    url_dict_list = sorted(url_data_list, key=lambda x: x.get('mtm', int(time.time())))
    for url_dict in url_dict_list:
        url_tuple_bytes = pickle.dumps(url_dict)
        # print(monitor_tm, 1, md5value)
        result = add_to_queue(theQueue, url_tuple_bytes, url_type)
        # print(monitor_tm, 2, md5value)
        if result:
            # print(monitor_tm, result, md5value)
            theQueue.add_asinAndKw_to_set(url_dict.get('md5'))
        urlQ.srem_successAsinSet_from_set(url_dict.get('md5'))


# 获得更新时间戳
def get_init_updae_tm(theQueue):
    tm_key = 'initUpdateTm'
    key_type = 'updateTime'
    tm_value = theQueue._get_value_from_string(tm_key, key_type)
    if tm_value:
        result1 = str(tm_value, encoding='utf-8')
        if re.match('^1[0-9]{9}$', result1):
            return int(result1)
    if os.path.exists('%s.tm' % tm_key):
        with open('%s.tm' % tm_key, 'r', encoding='utf-8') as f:
            tm = f.readline()
            if re.match('^1[0-9]{9}$', tm):
                return int(tm)


# 关键字重试
def keyword_retry(kwQ):
    url_type = 'keyword'
    Qname = 'KeywordQueue'
    # empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(kwQ)
    # sql_times = 0
    if sql_times:
        sql1 = "select kw from public.amazon_keyword_data where getinfo_tm < %s and kw in (select kw from public.amazon_keyword_monitor where state = 1) order by getinfo_tm;" % (sql_times * 1000)
        print(sql1)
        print('\nkw　重试进程　%s\n' % (sql_times))
        url_list = kwQ.retrieve_keyword(sql1)
        print('需要重试的关键字数 %s' % (len(url_list)))
        url_tuple_list = []
        if len(url_list) > 0:
            for url in url_list:
                kw = url[0]
                cid = 0
                aid = 0
                url_tuple = (kw, cid, aid)
                url_tuple_list.append(url_tuple)
            add_url_to_queue(kwQ, url_tuple_list, url_type)


# 商品重试
def goods_retry(urlQ):
    url_type = 'goods'
    Qname = 'goodsUrlQueue'
    # empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(urlQ)
    # sql_times = 0
    if sql_times:
        # 未下载重试
        sql1 = "select asin from public.amazon_product_data where getinfo_tm < %s and asin in (select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0) order by getinfo_tm;" % (sql_times * 1000)
        print(sql1)
        print('\ngoods　重试进程　%s\n' % (sql_times))
        url_list = urlQ.retrieve_asin(sql1)
        print('需要重试的商品数 %s' % (len(url_list)))
        url_tuple_list = []
        if len(url_list) > 0:
            for url in url_list:
                asin = url[0]
                monitor_type = 1
                aid = 0
                url_tuple = (asin, monitor_type, aid)
                url_tuple_list.append(url_tuple)
            add_url_to_queue(urlQ, url_tuple_list, url_type)


# 跟卖重试
def tosell_retry(urlQ):
    url_type = 'tosell'
    Qname = 'tosellUrlQueue'
    # empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(urlQ)
    # sql_times = 0
    if sql_times:
        sql1 = "select asin from public.amazon_product_data_tosell where getinfo_tm < %s and asin in (select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5) order by getinfo_tm;" % (sql_times * 1000)
        print(sql1)
        print('\ntosell　重试进程　%s\n' % (sql_times))
        url_list = urlQ.retrieve_asin(sql1)
        print('需要重试的跟卖数 %s' % (len(url_list)))
        # print('monitoring_tosell_Now: ', url_list)
        url_tuple_list = []
        if len(url_list) > 0:
            for url in url_list:
                asin = url[0]
                monitor_type = 5
                aid = 0
                url_tuple = (asin, monitor_type, aid)
                url_tuple_list.append(url_tuple)
            add_url_to_queue(urlQ, url_tuple_list, url_type)


if __name__ == '__main__':
    '读数据表, 把没有下载的历史数据进行重试, 每天1-14点第2分钟执行'
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    t1 = Thread(target=keyword_retry, args=(kwQ,))
    t2 = Thread(target=goods_retry, args=(urlQ,))
    # t3 = Thread(target=reviews_retry, args=(urlQ,))
    t4 = Thread(target=tosell_retry, args=(urlQ,))
    tList = [
        t1,
        t2,
        # t3,
        t4,
    ]
    for t in tList:
        t.start()
