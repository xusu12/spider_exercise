#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import time
import requests
from threading import Thread
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue, return_PST


pst_now = lambda: return_PST().strftime('%Y-%m-%d %H:%M:%S')
date_now = lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
debug_log = Logger()
myRedis = GetRedis().return_redis(debug_log)
urlQ = UrlQueue(myRedis, debug_log)

send_api = 'https://sys.selmetrics.com/pyapi/send'
tm_format = 'PT: %s\nGMT+8: %s\n'


def send_email_api(url_in, json_in):
    return requests.post(url_in, json=json_in, verify=False)


def look_set_len(myRedis, sName, set_type=''):
    r = myRedis
    the_set = r.smembers(sName)
    the_len = len(the_set)
    print('\n%s len: %s\n' % (set_type, the_len))
    return the_len


def look_queue_len(myRedis, Qname, url_type=''):
    r = myRedis
    url_len = r.llen(Qname)
    print('\n%s len: %s\n' % (url_type, url_len))
    return url_len


def send_func(msg_list, war_msg, title_format, to_addr, from_addrs_name=''):
    if len(msg_list) > 0:
        pt_time = pst_now()
        btm = date_now()
        msg_list.insert(0, war_msg)
        msg_list.append(tm_format % (btm, pt_time))
        msg_string = '\n'.join(msg_list)
        print(msg_string)
        # send_email(to_addr, None, title_format % (pt_time), msg_string)
        send_dict = dict(ta=to_addr, ts=title_format % (pt_time), ms=msg_string)
        if from_addrs_name:
            send_dict['fn'] = from_addrs_name
        resp = send_email_api(send_api, send_dict)
        print(resp.text)


def proxy_warning():
    '''最后写'''
    pass
    # 出现proxy error告警
    # 出现timeout 告警
    # 普通日志失败过多告警.


def new_task_warning(to_addr):
    '''第三写'''
    # 新任务超时告警(在规定的时间内, 没有入库).
    # 当前时间12小时内加入检测, 且没有当前时间24小时内的数据, 则告警.
    sql1 = 'select kw, monitor_tm, crawler_tm from public.amazon_keyword_monitor \
where state = 1 and monitor_tm > extract(epoch from now()) - 3 * 3600 \
and monitor_tm < extract(epoch from now()) - 60 * 30 \
and crawler_tm = 0 and kw not in \
(select kw from public.amazon_keyword_data where getinfo_tm > (extract(epoch from now()) - 24 * 3600) * 1000);'
    kw_list = urlQ.retrieve_asin(sql1)
    print(sql1)
    if len(kw_list) < 100:
        print(kw_list)
    msg_list = []
    msg_format = '%s 模块 %s 条新数据没有更新'
    war_msg = 'Warning: 新数据未爬取!'
    title_format = 'New task Warning! PT: %s'
    if len(kw_list) > 0:
        msg_list.append(msg_format % ('keyword', len(kw_list)))
    if 0 < len(kw_list) < 10:
        msg_list.append(str(kw_list))
        to_addr = 'HSXinqun@aliyun.com,BruceX@selmuch.com'
    return send_func(msg_list, war_msg, title_format, to_addr)


    # 新任务加入过多告警(有可能会完不成任务)
    # 新任务队列过长告警(说明异常, 或者有可能陷入死循环)


def data_queue_warning(to_addr):
    # 数据队列过长警报(意味着数据没有存进去)
    uType = 'Data'
    gNme = 'goods' + uType
    gLen = look_queue_len(myRedis, gNme, url_type=gNme)
    bNme = 'bsr' + uType
    bLen = look_queue_len(myRedis, bNme, url_type=bNme)
    rNme = 'reviews' + uType
    rLen = look_queue_len(myRedis, rNme, url_type=rNme)
    tNme = 'tosell' + uType
    tLen = look_queue_len(myRedis, tNme, url_type=tNme)
    kNme = 'keyword' + uType
    kLen = look_queue_len(myRedis, kNme, url_type=kNme)
    msg_list = []
    msg_format = '%s 队列滞留 %s 条数据'
    war_msg = 'Warning: 数据入库可能有问题'
    title_format = 'Data Save Warning! PT: %s'
    if gLen >= 1000:
        msg_list.append(msg_format % ('    product data ', gLen))
    if bLen >= 1000:
        msg_list.append(msg_format % ('    bsr data ', bLen))
    if rLen >= 1000:
        msg_list.append(msg_format % ('    reviews data ', rLen))
    if tLen >= 1000:
        msg_list.append(msg_format % ('    tosell data ', tLen))
    if kLen >= 1000:
        msg_list.append(msg_format % ('    keyword data ', kLen))
    return send_func(msg_list, war_msg, title_format, to_addr)


def db_count_warning(to_addr='HSXinqun@aliyun.com'):
    # 数据表过大警报.(意味着性能下降)
    the_num = lambda lst: lst[0][0] if len(lst) == 1 and type(lst[0]) is tuple and len(lst[0]) == 1 else 0
    sql = "select count(*) from %s;"
    keyword_druid = 'public.amazon_druid_keyword_data'
    keyword_druid_count = the_num(urlQ.retrieve_asin(sql % keyword_druid))
    print(keyword_druid_count, type(keyword_druid_count))
    bsr_druid = 'public.amazon_druid_product_data_bsr'
    bsr_druid_count = the_num(urlQ.retrieve_asin(sql % bsr_druid))
    product_druid = 'public.amazon_druid_product_data'
    product_druid_count = the_num(urlQ.retrieve_asin(sql % product_druid))
    tosell_druid = 'public.amazon_product_data_tosell'
    tosell_druid_count = the_num(urlQ.retrieve_asin(sql % tosell_druid))
    reviews_druid = 'public.amazon_product_comment'
    reviews_druid_count = the_num(urlQ.retrieve_asin(sql % reviews_druid))
    msg_list = []
    msg_format = '%s count %s'
    if keyword_druid_count > 10000 * 800:
        msg_list.append(msg_format % (keyword_druid, keyword_druid_count))
    print(keyword_druid_count, type(keyword_druid_count))
    if bsr_druid_count > 10000 * 300:
        msg_list.append(msg_format % (bsr_druid, bsr_druid_count))
    print(bsr_druid_count, type(bsr_druid_count))
    if product_druid_count > 10000 * 300:
        msg_list.append(msg_format % (product_druid, product_druid_count))
    print(product_druid_count, type(product_druid_count))
    if tosell_druid_count > 10000 * 300:
        msg_list.append(msg_format % (tosell_druid, tosell_druid_count))
    print(tosell_druid_count, type(tosell_druid_count))
    if reviews_druid_count  > 10000 * 300:
        msg_list.append(msg_format % (reviews_druid, reviews_druid_count))
    print(reviews_druid_count, type(reviews_druid_count))
    war_msg = 'Warning: 数据表过大'
    title_format = '数据表过大 Warning! PT: %s'
    if len(msg_list) > 0:
        pt_time = pst_now()
        btm = date_now()
        msg_list.insert(0, war_msg)
        msg_list.append(tm_format % (pt_time, btm))
        msg_string = '\n'.join(msg_list)
        print(msg_string)
        resp = send_email_api(send_api, dict(ta=to_addr, ts=title_format % (pt_time), ms=msg_string))
        print(resp.json())


if __name__ == '__main__':
    to_addr = 'garyF@daisycorp.net,HSLiulei@aliyun.com,hongz@intechannel.com,HSXinqun@aliyun.com,BruceX@selmuch.com'
    t_list = [
        Thread(target=new_task_warning, args=(to_addr,)),
        Thread(target=data_queue_warning, args=(to_addr,)),
        Thread(target=db_count_warning),
    ]
    for t in t_list:
        t.start()
    for t in t_list:
        t.join()
