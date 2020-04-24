#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
sys.path.append("../../")
import os
import pickle
import re
import time
from threading import Thread
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue


# 获取最大监控时间
def get_monitor_tm(theQueue, tm_key=''):
    key_type = tm_key
    # max_tm_bytes = False
    max_tm_bytes = theQueue._get_value_from_string(tm_key, key_type)
    if max_tm_bytes:
        max_tm_str = str(max_tm_bytes, encoding='utf-8')
        if re.match('^1[0-9]{9}$',max_tm_str):
            print(max_tm_str, type(max_tm_str))
            return int(max_tm_str)
    if os.path.exists('%s.tm' % tm_key):
        with open('%s.tm' % tm_key, 'r', encoding='utf-8') as f:
            tm = f.readline()
            if re.match('^1[0-9]{9}$', tm):
                return int(tm)
    return int(time.time()) - 600


# 将新增url, 加入队列
def add_url_to_queue(theQueue, url_tuple_list, tm_key, url_type=''):
    used = 'useInterval'

    def add_to_queue(theQueue, url_tuple_bytes, url_type=''):
        qType = 'monitor'
        result = False
        if url_type == 'goods':
            result = theQueue.add_goods_url_to_queue(url_tuple_bytes, qType)
        if url_type == 'reviews':
            result = theQueue.add_reviews_url_to_queue(url_tuple_bytes, qType)
        if url_type == 'tosell':
            result = theQueue.add_tosell_url_to_queue(url_tuple_bytes, qType)
        if url_type == 'keyword':
            result = theQueue.add_keyword_to_queue(url_tuple_bytes, qType)
        return result
    monitor_tm_list = []
    # print(url_tuple_list)
    url_data_dict = {}
    for urlTuple in url_tuple_list:
        # print(urlTuple)
        kw_asin = urlTuple[0]
        cid_monitorType = urlTuple[1]
        aid = urlTuple[2]
        # 记录监控时间
        monitor_tm = urlTuple[3]
        # print(monitor_tm, type(monitor_tm))
        if monitor_tm and type(monitor_tm) is int:
            monitor_tm_list.append(monitor_tm)

        md5value = kw_asin + url_type
        md5key = theQueue.get_md5_key(md5value)
        usedMd5key = theQueue.get_md5_key(md5value + used)
        if not theQueue.is_exists_asinAndKwSet(md5key):
            url_dict = dict(
                aid=aid,
                mtm=monitor_tm,
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
    url_dict_list = sorted(url_data_list, key=lambda x:x.get('mtm', int(time.time())))
    for url_dict in url_dict_list:
        url_tuple_bytes = pickle.dumps(url_dict)
        # print(monitor_tm, 1, md5value)
        result = add_to_queue(theQueue, url_tuple_bytes, url_type)
        # print(monitor_tm, 2, md5value)
        if result:
            # print(monitor_tm, result, md5value)
            theQueue.add_asinAndKw_to_set(url_dict.get('md5'))
            set_name = 'NewUrl'
            theQueue._add_member_to_set(set_name, url_dict.get('md5'))

    key_type = tm_key
    print('%s %s min_tm: %s - max_tm: %s\n' % (url_type, tm_key, min(monitor_tm_list), max(monitor_tm_list)))
    if len(monitor_tm_list) > 0:
        sql_times = get_monitor_tm(theQueue, tm_key)
        tm_value = max(monitor_tm_list)
        # print('tm_value', tm_value, tm_key)
        if tm_value > 0 and tm_value > sql_times:
            # 记录监控时间
            theQueue._set_key_value_to_string(tm_key, tm_value, key_type, overtime=86400)
            with open('%s.tm' % (tm_key), 'w', encoding='utf-8') as f:
                f.write(str(tm_value))
                print(str(tm_value), '%s.tm' % (tm_key))


# 监控关键字
def kw_monitor(kwQ):
    url_type = 'keyword'
    tm_key = 'keywordMaxTm'
    sql_times = get_monitor_tm(kwQ, tm_key)
    sql = "select kw, cid, aid, monitor_tm from public.amazon_keyword_monitor where state > 0 and monitor_tm > %s order by monitor_tm" % (sql_times)
    print(sql)
    print('\nkw　实时监控进程　%s\n' % (sql_times))
    url_tuple_list = kwQ.retrieve_keyword(sql)
    print('monitoring_kw_Now: ', len(url_tuple_list))
    if len(url_tuple_list) > 0:
        add_url_to_queue(kwQ, url_tuple_list, tm_key, url_type)


# 监控商品
def goods_monitor(urlQ):
    url_type = 'goods'
    tm_key = 'goodsMaxTm'
    sql_times = get_monitor_tm(urlQ, tm_key)
    sql = "select asin, monitor_type, aid, info_tm from public.amazon_product_monitor where state > 0 and monitor_type > 0 and info_tm > %s order by info_tm" % (sql_times)
    print(sql)
    print('\ngoods　实时监控进程　%s\n' % (sql_times))
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('monitoring_goods_Now: ', len(url_tuple_list))
    if len(url_tuple_list) > 0:
        add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)


# 监控评论
def reviews_monitor(urlQ):
    url_type = 'reviews'
    tm_key = 'reviewsMaxTm'
    sql_times = get_monitor_tm(urlQ, tm_key)
    sql = "select asin, monitor_type, aid, comment_tm from public.amazon_product_monitor where state > 0 and comment_tm > %s and monitor_type >= 3 and monitor_type != 5 order by comment_tm" % (sql_times)
    print(sql)
    print('\nreviews　实时监控进程　%s\n' % (sql_times))
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('monitoring_reviews_Now: ', len(url_tuple_list))
    if len(url_tuple_list) > 0:
        add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)


# 监控跟卖
def tosell_monitor(urlQ):
    url_type = 'tosell'
    tm_key = 'tosellMaxTm'
    sql_times = get_monitor_tm(urlQ, tm_key)
    sql = "select asin, monitor_type, aid, tosell_tm from public.amazon_product_monitor where state > 0 and tosell_tm > %s and monitor_type >= 5 order by tosell_tm" % (sql_times)
    print(sql)
    print('\ntosell　实时监控进程　%s\n' % (sql_times))
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('monitoring_tosell_Now: ', len(url_tuple_list))
    if len(url_tuple_list) > 0:
        add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)


if __name__ == '__main__':
    '''定时器, 每1分钟启动1次'''
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    t1 = Thread(target=kw_monitor, args=(kwQ,))
    t2 = Thread(target=goods_monitor, args=(urlQ,))
    t3 = Thread(target=reviews_monitor, args=(urlQ,))
    t4 = Thread(target=tosell_monitor, args=(urlQ,))
    tList = [
        t1,
        t2,
        t3,
        t4,
    ]
    for t in tList:
        t.start()
