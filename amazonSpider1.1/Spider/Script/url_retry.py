#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import re
import os
import time
import pickle
from threading import Thread
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue, return_PST



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
def add_url_to_queue(theQueue, url_tuple_list, url_type='', sql_times=None):
    used = 'useInterval'
    aday = return_PST().strftime('%Y%m%d')
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
        # 记录监控时间
        monitor_tm = urlTuple[3]
        md5value = kw_asin + url_type
        md5key = theQueue.get_md5_key(md5value)
        usedMd5key = theQueue.get_md5_key(md5value + used)
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
    filter_list = lambda lst: [x[0] for x in lst if type(x) is tuple and len(x) > 0]
    asin_set_list = []
    if url_type == 'keyword':
        sql1 = "select kw from public.amazon_druid_keyword_data where tm > %(tm)s and aday=%(aday)s group by kw;"
        # print(sql1)
        data = dict(tm=sql_times * 1000, aday=aday)
        asin_set_list = filter_list(urlQ.retrieve_asin(sql1, data))
        if len(asin_set_list) > 10:
            print(asin_set_list[:10])
        print('len asin_set_list', len(asin_set_list))
    if url_type == 'goods':
        sql1 = "select asin from public.amazon_druid_product_data where tm > %s and aday='%s';" % (sql_times * 1000,  return_PST().strftime('%Y%m%d'))
        #print(sql1)
        asin_set_list = filter_list(urlQ.retrieve_asin(sql1))
        if len(asin_set_list) > 10:
            print(asin_set_list[:10])
        print('len asin_set_list', len(asin_set_list))
    for url_dict in url_dict_list:
        url_tuple_bytes = pickle.dumps(url_dict)
        # print(monitor_tm, 1, md5value)
        result = add_to_queue(theQueue, url_tuple_bytes, url_type)
        # print(monitor_tm, 2, md5value)
        if result:
            # print(monitor_tm, result, md5value)
            theQueue.add_asinAndKw_to_set(url_dict.get('md5'))
        #urlQ.srem_successAsinSet_from_set(md5key)
        if url_type == 'goods':
            # 如果 asin 不是已下架
            if sql_times:
                if urlQ.is_downloaded(url_dict.get('md5')):
                    if url_dict.get('asin') not in asin_set_list:
                        print('实际上没有下载的asin', url_dict.get('asin'))
                        urlQ.srem_successAsinSet_from_set(url_dict.get('md5'))
        if url_type == 'keyword':
            # 如果 asin 不是已下架
            if sql_times:
                if urlQ.is_downloaded(url_dict.get('md5')):
                    if url_dict.get('kw') not in asin_set_list:
                        print('实际上没有下载的kw', url_dict.get('kw'))
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
    empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(kwQ)
    # sql_times = 0
    if sql_times:
        sql = "select kw, cid, aid, monitor_tm from public.amazon_keyword_monitor where state = 1 and crawler_tm < %s order by crawler_tm limit 8000;" % (sql_times)
        print(sql)
        print('\nkw　重试进程　%s\n' % (sql_times))
        url_tuple_list = kwQ.retrieve_keyword(sql)
        print('需要重试的关键字数 %s' % (len(url_tuple_list)))
        # print('keyword_retry: ', url_tuple_list)
        if len(url_tuple_list) > 0:
            add_url_to_queue(kwQ, url_tuple_list, url_type=url_type, sql_times=sql_times)


# 商品重试
def goods_retry(urlQ):
    url_type = 'goods'
    Qname = 'goodsUrlQueue'
    empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(urlQ)
    # sql_times = 0
    if sql_times:
        # 未下载重试
        sql = "select asin, monitor_type, aid, info_tm from public.amazon_product_monitor where state = 1 \
and monitor_type > 0 and info_tm_crawler < %s and asin not in (select asin from public.amazon_druid_product_data where aday='%s') order by info_tm_crawler limit 8000;" % (sql_times, return_PST().strftime('%Y%m%d'))

        # 库存下载失败重试
        #sql1 = "select asin, monitor_type, aid, info_tm from public.amazon_product_monitor where asin in (select asin from amazon_product_data where asin in (select asin from amazon_product_monitor where state=1 and monitor_type > 0) and asin not in (select asin from amazon_druid_product_data where aday='%s')) order by info_tm_crawler limit 8000;" % (return_PST().strftime("%Y%m%d"))
        #print(sql)
        print('\ngoods　重试进程　%s\n' % (sql_times))
        url_tuple_list = urlQ.retrieve_asin(sql)
        #url_tuple_list2 = urlQ.retrieve_asin(sql1)
        #url_list_tuple = set(url_tuple_list + url_tuple_list2)
        url_list_tuple = url_tuple_list
        print('需要重试的商品数 %s' % (len(url_list_tuple)))
        # print('monitoring_goods_Now: ', url_tuple_list)
        if len(url_list_tuple) > 0:
            add_url_to_queue(urlQ, url_list_tuple, url_type=url_type, sql_times=sql_times)


# 评论重试
def reviews_retry(urlQ):
    url_type = 'reviews'
    Qname = 'reviewsUrlQueue'
    empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(urlQ)
    # sql_times = 0
    if sql_times:
        sql = "select asin, monitor_type, aid, comment_tm from public.amazon_product_monitor where state = 1 and comment_tm_crawler < %s and monitor_type >= 3 and monitor_type != 5 order by comment_tm_crawler desc limit 8000;" % (sql_times)
        print(sql)
        print('\nreviews　重试进程　%s\n' % (sql_times))
        url_tuple_list = urlQ.retrieve_asin(sql)
        print('需要重试的评论数 %s' % (len(url_tuple_list)))
        # print('monitoring_reviews_Now: ', url_tuple_list)
        if len(url_tuple_list) > 0:
            add_url_to_queue(urlQ, url_tuple_list, url_type)


# 跟卖重试
def tosell_retry(urlQ):
    url_type = 'tosell'
    Qname = 'tosellUrlQueue'
    empty_url_queue(urlQ.RedisQ, Qname)
    sql_times = get_init_updae_tm(urlQ)
    # sql_times = 0
    if sql_times:
        # sql = "select asin, monitor_type, aid, tosell_tm from public.amazon_product_monitor where state = 1 and tosell_tm_crawler < %s and monitor_type >= 5 order by tosell_tm_crawler limit 8000;" % (sql_times)
        sql = "select asin, monitor_type, aid, tosell_tm from public.amazon_product_monitor where state = 1 and tosell_tm_crawler < %s and monitor_type >= 5 \
and asin not in (select asin from public.amazon_product_data_tosell where getinfo_tm > %s) and \
asin not in (select asin from public.amazon_product_data where getinfo_tm > %s and asin_state = 0) order by tosell_tm_crawler limit 8000;" % (sql_times, sql_times * 1000, sql_times * 1000)
        print(sql)
        print('\ntosell　重试进程　%s\n' % (sql_times))
        url_tuple_list = urlQ.retrieve_asin(sql)
        print('需要重试的跟卖数 %s' % (len(url_tuple_list)))
        # print('monitoring_tosell_Now: ', url_tuple_list)
        if len(url_tuple_list) > 0:
            add_url_to_queue(urlQ, url_tuple_list, url_type)


if __name__ == '__main__':
    '''定时器, 每天16-23点的第3分钟执行'''
    '''定时器, 每天0-14点的第3分钟执行'''
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    t1 = Thread(target=keyword_retry, args=(kwQ,))
    t2 = Thread(target=goods_retry, args=(urlQ,))
    t3 = Thread(target=reviews_retry, args=(urlQ,))
    t4 = Thread(target=tosell_retry, args=(urlQ,))
    tList = [
        t1,
        t2,
        t3,
        t4,
    ]
    for t in tList:
        t.start()
