#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
sys.path.append("../../")
import os
import re
import pickle
import time
from datetime import datetime
# from threading import Thread

from Crawler.BaseCrawler import BaseCrawler
from utils.util import return_PST
from conf.setting import REPORT_DIR
from utils.util import Logger
from utils.util import GetRedis
from utils.util import UrlQueue
from utils.util import KeyWordQueue
# from utils.util import IpQueue
# from utils.util import DataQueue
# from utils.util import CookQueue
from Crawler.DataOutput import GetDbObj


#　重置爬取状态
def init_crawler_state():
    time_now = int(time.time() * 1000)
    dbObj = GetDbObj().get_db_obj()
    cur = dbObj.cursor()
    update_sql = 'update public.amazon_product_data set crawler_state=0 where getinfo_tm < %s;' % (time_now)
    cur.execute(update_sql)
    row1 = cur.rowcount
    print('%s %s %s行更新成功' % (1, update_sql, row1))
    update_sql = 'update public.amazon_product_data_tosell set crawler_state=0 where getinfo_tm < %s;' % (time_now)
    cur.execute(update_sql)
    row2 = cur.rowcount
    print('%s %s %s行更新成功' % (2, update_sql, row2))
    update_sql = 'update public.amazon_keyword_data set crawler_state=0 where getinfo_tm < %s;' % (time_now)
    cur.execute(update_sql)
    row3 = cur.rowcount
    print('%s %s %s行更新成功' % (3, update_sql, row3))
    dbObj.commit()
    cur.close()
    dbObj.close()


# 获取最大监控时间
def get_monitor_tm(theQueue, tm_key=''):
    key_type = tm_key
    # max_tm_bytes = False
    max_tm_bytes = theQueue._get_value_from_string(tm_key, key_type)
    if max_tm_bytes:
        max_tm_str = str(max_tm_bytes, encoding='utf-8')
        if re.match('^1[0-9]{9}$', max_tm_str):
            print(max_tm_str, type(max_tm_str))
            return int(max_tm_str)
    if os.path.exists('%s.tm' % tm_key):
        with open('%s.tm' % tm_key, 'r', encoding='utf-8') as f:
            tm = f.readline()
            if re.match('^1[0-9]{9}$', tm):
                return int(tm)
    return 0


# 将新增url, 加入队列
def add_url_to_queue(theQueue, url_tuple_list, tm_key, url_type=''):
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
    monitor_tm_list = []
    # print(url_tuple_list)
    urlNum = 0
    url_data_dict = {}
    print('\n\nurl_tuple_list', len(url_tuple_list))
    # time.sleep(10)
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
    url_dict_list = sorted(url_data_list, key=lambda x: x.get('mtm', int(time.time())))
    print('\n\nurl_dict_list', len(url_dict_list))
    # time.sleep(10)
    for url_dict in url_dict_list:
        url_tuple_bytes = pickle.dumps(url_dict)
        # print(monitor_tm, 1, md5value)
        result = add_to_queue(theQueue, url_tuple_bytes, url_type)
        # print(monitor_tm, 2, md5value)
        if result:
            # print(monitor_tm, result, md5value)
            theQueue.add_asinAndKw_to_set(url_dict.get('md5'))
            urlNum += 1

    key_type = tm_key
    print('%s %s min_tm: %s - max_tm: %s\n' % (url_type, tm_key, min(monitor_tm_list), max(monitor_tm_list)))
    if len(monitor_tm_list) > 0:
        sql_times = get_monitor_tm(theQueue, tm_key)
        tm_value = max(monitor_tm_list)
        # print('tm_value', tm_value, tm_key)
        if tm_value > 0 and tm_value > sql_times:
            # 记录监控时间
            theQueue._set_key_value_to_string(tm_key, tm_value, key_type, overtime=86400)
    return urlNum


def kw_init(kwQ):
    url_type = 'keyword'
    tm_key = 'keywordMaxTm'
    sql = "select kw, cid, aid, monitor_tm from public.amazon_keyword_monitor where state = 1 order by crawler_tm limit 5000;"
    print(sql)
    url_tuple_list = kwQ.retrieve_keyword(sql)
    print('kw_init: ', len(url_tuple_list))
    urlNum = 0
    if len(url_tuple_list) > 0:
       urlNum = add_url_to_queue(kwQ, url_tuple_list, tm_key, url_type)
    return urlNum


def goods_init(urlQ):
    url_type = 'goods'
    tm_key = 'goodsMaxTm'
    sql = "select asin, monitor_type, aid, info_tm from public.amazon_product_monitor where state = 1 and monitor_type > 0 order by info_tm_crawler limit 10000;"
    print(sql)
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('goods_init: ', len(url_tuple_list))
    urlNum = 0
    if len(url_tuple_list) > 0:
        urlNum = add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)
    return urlNum


def reviews_init(urlQ):
    url_type = 'reviews'
    tm_key = 'reviewsMaxTm'
    sql = "select asin, monitor_type, aid, comment_tm from public.amazon_product_monitor where state = 1 and monitor_type >= 3 and monitor_type != 5 order by comment_tm_crawler limit 5000;"
    print(sql)
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('reviews_init: ', len(url_tuple_list))
    urlNum = 0
    if len(url_tuple_list) > 0:
        urlNum = add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)
    return urlNum


def tosell_init(urlQ):
    url_type = 'tosell'
    tm_key = 'tosellMaxTm'
    sql = "select asin, monitor_type, aid, tosell_tm from public.amazon_product_monitor where state = 1 and monitor_type >= 5 order by tosell_tm_crawler limit 5000;"
    print(sql)
    url_tuple_list = urlQ.retrieve_asin(sql)
    print('tosell_init: ', len(url_tuple_list))
    urlNum = 0
    if len(url_tuple_list) > 0:
        urlNum = add_url_to_queue(urlQ, url_tuple_list, tm_key, url_type)
    return urlNum


# 初始化所有url
def all_url_init(urlQ, kwQ):
    kwNum = kw_init(kwQ)
    goodsNum = goods_init(urlQ)
    reviewsNum = reviews_init(urlQ)
    tosellNum = tosell_init(urlQ)
    urlNum = goodsNum + reviewsNum + tosellNum + kwNum
    urlQ.update_mission_attempts(urlNum)
    pstNow = return_PST()
    startTime = pstNow.strftime("%Y-%m-%d %H:%M:%S")
    dateNow = pstNow.strftime("%Y_%m_%d")
    statFile = os.path.join(REPORT_DIR, 'statistics_%s.csv' % (dateNow))
    msg = '\n[,%s,] [,初始化报告,], 任务总数, %s, 成功加入商品队列, %s, ' % (startTime, urlNum, goodsNum)
    msg1 = '成功加入评论队列, %s, ' % (reviewsNum)
    msg2 = '成功加入跟卖队列, %s,' % (tosellNum)
    msg3 = '成功加入关键字队列, %s, 任务开始！' % (kwNum)
    msgs = msg + msg1 + msg2 + msg3
    with open(statFile, 'a') as f:
        f.write(msgs)


#清空新url集合
def empty_new_url_set(urlQ):
    set_name = 'NewUrl'
    while True:
        url = urlQ._pop_member_from_set(set_name)
        if not url:
            break
        print('%s 已从NewUrl集合删除' % (url))

# 清空已添加集合
def empty_asinAndKw(urlQ):
    while True:
        asinAndKw = urlQ.pop_asinAndKw_from_set()
        if not asinAndKw:
            break
        print('asinAndKw [%s] 删除成功' % asinAndKw)


# 清空任务队列
def empty_url_queue(myRedis, Qname):
    r = myRedis
    i = 0
    while True:
        i += 1
        url = r.rpop(Qname)
        if not url:
            break
    print('\n已删除url %s\n' % (i))


# 清空已成功集合
def empty_succeessUrl(urlQ):
    while True:
        succeessUrl = urlQ.pop_successAsinKwSet()
        if not succeessUrl:
            break
        print('succeessUrl [%s] 删除成功' % succeessUrl)


# 清空下载失败集合
def empty_defeatedUrl(urlQ):
    while True:
        defeatedUrl = urlQ.pop_defeated_urlSet()
        if not defeatedUrl:
            break
        print('defeatedUrl [%s] 删除成功' % defeatedUrl)


def get_the_time():
        # 日期格式
        date_str = '%Y%m%d'
        # 时间格式
        time_str = '%Y%m%d%H%M%S'
        # 当天的日期对象
        the_day = datetime.now()
        # 当天日期字符串
        date_str = the_day.strftime(date_str)
        # 当天15点整字符串
        the_day_str = '%s150000' % (date_str)
        # 当天15点的时间对象
        time_day = time.strptime(the_day_str, time_str)
        print(1, time_day, type(time_day))
        # 当天15点时间戳
        the_time = time.mktime(time_day)
        print(the_time, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(the_time)))
        return the_time


def init_updae_tm(theQueue):
    tm_key = 'initUpdateTm'
    tm_value = int(get_the_time())
    key_type = 'updateTime'
    theQueue._set_key_value_to_string(tm_key, tm_value, key_type, overtime=86400)
    with open('%s.tm' % (tm_key), 'w', encoding='utf-8') as f:
        f.write(str(tm_value))
        print(str(tm_value), '%s.tm' % (tm_key))


# 设置完工状态
def set_worker_state(myRedis):
    r = myRedis
    r.set('urlInit', 'true', 72000)


# 获取完工状态
def get_worker_state(myRedis):
    r = myRedis
    result = False
    state = r.get('urlInit')
    print(state)
    if state:
        if state == 'true' or state == b'true':
            result = True
    return result


def url_init():
    '''服务启动时调用一次, 定时器每天凌晨0点1分调用'''
    pstNow = return_PST()
    pstHour = pstNow.hour
    debug_log = Logger()
    # info_log = Logger('info')
    if pstHour == 0:
        myRedis = GetRedis().return_redis(debug_log)
        if get_worker_state(myRedis):
            pass
            #return debug_log.war('init_url: %s 其它机器已经初始化过了' % (pstNow.strftime('%Y-%m-%d %H:%M:%S')))
        # 重置爬取状态
        init_crawler_state()
        kwQ = KeyWordQueue(myRedis, debug_log)
        urlQ = UrlQueue(myRedis, debug_log)
        # ipQ = IpQueue(myRedis, debug_log)
        # dataQ = DataQueue(myRedis, debug_log)
        # cookiesQ = CookQueue(myRedis, debug_log)

        # 设置初始化时间戳(用来判断数据是否已爬取)
        init_updae_tm(urlQ)

        # 清空新url集合
        empty_new_url_set(urlQ)

        # 将任务总数重设为0
        urlQ.set_mission_attempts(0)

        # 清空重试统计队列
        myRedis.zremrangebylex('%s%s' % ('goods', 'fail'), '-', '+')
        myRedis.zremrangebylex('%s%s' % ('tosell', 'fail'), '-', '+')
        myRedis.zremrangebylex('%s%s' % ('reviews', 'fail'), '-', '+')
        myRedis.zremrangebylex('%s%s' % ('keyword', 'fail'), '-', '+')

        # 清空商品队列
        Qname = 'goodsUrlQueue'
        empty_url_queue(myRedis, Qname)
        # 清空评论队列
        Qname = 'reviewsUrlQueue'
        empty_url_queue(myRedis, Qname)
        # 清空跟卖队列
        Qname = 'tosellUrlQueue'
        empty_url_queue(myRedis, Qname)
        # 清空关键词队列
        Qname = 'KeywordQueue'
        empty_url_queue(myRedis, Qname)

        # 清空已添加集合
        empty_asinAndKw(urlQ)
        # 清空已成功集合
        empty_succeessUrl(urlQ)
        # 清空下载失败集合
        empty_defeatedUrl(urlQ)

        # 将结束报告状态, 设置为False
        key = 'isStatistics'
        key_type = 'statistics'
        value = pickle.dumps(False)
        urlQ._set_key_value_to_string(key, value, key_type, overtime=86400)

        # 初始化所有url
        all_url_init(urlQ, kwQ)

        # 设置完工状态
        set_worker_state(myRedis)
        # 清空url的验证码与失败统计次数
        myRedis.zremrangebylex('urlDefeatedTimes', '-', '+')
        myRedis.zremrangebylex('urlRobotCheckTimes', '-', '+')
        debug_log.war('init_url: %s 初始化完成' % (pstNow.strftime('%Y-%m-%d %H:%M:%S')))
    else:
        debug_log.war('init_url: 当前太平洋时间: %s, 不是凌晨0点' % (pstNow.strftime('%Y-%m-%d %H:%M:%S')))


if __name__ == '__main__':
    url_init()
    # init_crawler_state()
    # get_the_time()
