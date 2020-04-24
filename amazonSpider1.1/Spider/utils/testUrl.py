#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import pickle

from utils.util import Logger, GetRedis, UrlQueue

# 根据监控类型分发asin
def is_monitor_type(urlQ, asin, monitor_type, aid):
    # 监控类型（1产品， 2评论， 4跟卖， 数据库存1, 3, 5, 7）
    print('Worker is_monitor_type init')
    url_tuple = (asin, monitor_type, aid)
    url_betys = pickle.dumps(url_tuple)
    if monitor_type == 1 or monitor_type == 3 or monitor_type == 5 or monitor_type == 7:
        print('goods', url_betys)
        result = urlQ.jump_queue_to_goods(url_betys)
        if not result:
            result = urlQ.add_goods_url_to_queue(url_betys)

    if monitor_type == 3 or monitor_type == 7 or monitor_type == 6:
        print('reviews', url_betys)
        result = urlQ.jump_queue_to_reviews(url_betys)
        if not result:
            result = urlQ.add_reviews_url_to_queue(url_betys)

    if monitor_type == 5 or monitor_type == 7 or monitor_type == 6:
        print('tosell', url_betys)
        result = urlQ.jump_queue_to_tosell(url_betys)
        if not result:
            result = urlQ.add_tosell_url_to_queue(url_betys)

def func(urlQ, sql):
    print(sql)
    asins = urlQ.retrieve_asin(sql)
    print('monitoring_kw_Now: ', asins)
    if asins:
        print('monitoring_kw_Now 到这里了吗')
        for item in asins:
            # asin= item[0]
            # print(type(asin), asin)
            # asin, monitor_type, aid = item[0], item[1], item[2]
            # print(type(asin), asin, type(monitor_type), monitor_type, type(aid), aid)
            if type(item[0]) is str and type(item[1]) is int:
                asin, monitor_type, aid = item[0], item[1], item[2]
                is_monitor_type(urlQ, asin, monitor_type, aid)

if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    sql = "select asin, monitor_type, aid from public.amazon_product_monitor where monitor_type > 0 and aid='3';"
    # sql = "select info_tm, comment_tm, tosell_tm from public.amazon_product_monitor where monitor_type > 0;"
    # sql = "select monitor_tm from public.amazon_keyword_monitor where state > 0;"
    func(urlQ, sql)
    # asin = 'B013TSICNQ'
    # asin = 'B06XX7VW8Z'
    # asin = 'B01AMY4VX0'
    # asin = 'B077SDFQP8'
    # monitor_type = 1
    # aid = '3'
    # is_monitor_type(urlQ, asin, monitor_type, aid)