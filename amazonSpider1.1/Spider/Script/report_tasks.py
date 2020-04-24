#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import re
import os
import time

from conf.setting import REPORT_DIR
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue, return_PST
from GiveAnAlarm.email_give_an_alarm import send_func


pst_now = lambda: return_PST()
from_addrs_name = '自动报告'


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
    return 0

#标记以及获取发送状态
def mark_sent(theQueue, the_key_value: tuple, mark_type='set', expires=3600 * 24):
    '''
    if mark_type='set', the_key_value=(key, value)
    if mark_type='get', the_key_value=(key, )
    '''
    if mark_type == 'set':
        return theQueue.RedisQ.set(the_key_value[0], the_key_value[1])
    if mark_type == 'get':
        return theQueue.RedisQ.get(the_key_value[0])


def statistics(urlQ, to_addr_in):
    the_date = return_PST()
    file_name = os.path.join(REPORT_DIR, 'statistics_info_%s.csv' % (the_date.strftime('%Y%m%d')))
    #  关键字总数 已入库数  入库失败的数量
    kw_sum, kw_num, kw_fail_sum = keyword_retry(urlQ)
    #  产品的总数  已经入库的数量  入库失败的数量  入库失败但是保存数据到数据库的商品的数量
    goods_sum, goods_num, goods_fail_sum, fail_goods = goods_retry(urlQ)
    # goods_sum, goods_num, goods_fail_sum= goods_retry(urlQ)
    # 没有库存, 价格, bsr, 标题, 品牌, 图片, 评轮, 评分 的产品数量
    not_qty_sum, not_price, not_bsr, not_title, not_brand, not_img, not_rc, not_rrg = qty_retry(urlQ)
    #  评论的总数 已经入库的数量  入库失败的数量
    reviews_sum, reviews_num, reviews_fail_sum = reviews_retry(urlQ)
    #  跟卖的总数 已经入库的数量  入库失败的数量
    tosell_sum, tosell_num, tosell_fail_sum = tosell_retry(urlQ)
    # 库存已入库数
    inventory_num = goods_num - not_qty_sum
    # 未完成入库的商品的数量
    goods_unfinished = goods_sum - goods_num
    # 未完成入库的关键字的数量
    kw_unfinished = kw_sum - kw_num
    # 未完成入库的跟卖的数量
    tosell_unfinished = tosell_sum - tosell_num
    # 未完成入库的评论的数量
    reviews_unfinished = reviews_sum - reviews_num
    # 库存入库完成度
    inventory_comlete_rate = inventory_num / goods_sum * 100
    # 商品入库完成度
    goods_complete_rate = goods_num / goods_sum * 100
    # 关键字入库完成度
    kw_complete_rate = kw_num / kw_sum * 100
    # 跟卖入库完成度
    tosell_complete_rate = tosell_num / tosell_sum * 100
    # 评论入库完成度
    reviews_complete_rate = reviews_num / reviews_sum * 100
    # 库存重试率
    inventory_retry_rate = not_qty_sum / goods_sum * 100
    # 商品重试率
    goods_retry_rate = goods_fail_sum / goods_sum * 100
    # 关键字重试率
    kw_retry_rate = kw_fail_sum / kw_sum * 100
    # 跟卖重试率
    tosell_retry_rate = tosell_fail_sum / tosell_sum * 100
    # 评论重试率
    reviews_retry_rate = reviews_fail_sum / reviews_sum * 100
    with open(file_name, 'a', encoding='utf-8') as f:

        f.write("\n , ,GTM+8,%s\n" % (time.strftime('%Y-%m-%d,%H:%M:%S', time.localtime(time.time()))))
        f.write("%s,%s,%s,%s,%s,%s\n" % (
            the_date.strftime('%Y-%m-%d,%H:%M:%S'), 'inventory|库存', 'product|产品',
            'keyword|关键字', 'tosell|跟卖', 'reviews|评论'
        ))
        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,总数', goods_sum, goods_sum, kw_sum, tosell_sum, reviews_sum)
                )
        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,已入库', inventory_num, goods_num, kw_num, tosell_num, reviews_num)
                )
        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,未完成', goods_sum - inventory_num, goods_unfinished,
                 kw_unfinished, tosell_unfinished, reviews_unfinished)
                )

        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,完成度', '%.2f%%' % inventory_comlete_rate,
                 '%.2f%%' % goods_complete_rate, '%.2f%%' % kw_complete_rate,
                 '%.2f%%' % tosell_complete_rate, '%.2f%%' % reviews_complete_rate)
                )
        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,需重试', not_qty_sum, goods_fail_sum, kw_fail_sum, tosell_fail_sum, reviews_fail_sum)
                )
        f.write("%s,%s,%s,%s,%s,%s\n" %
                (' ,重试率', '%.2f%%' % inventory_retry_rate,
                 '%.2f%%' % goods_retry_rate,
                 '%.2f%%' % kw_retry_rate,
                 '%.2f%%' % tosell_retry_rate,
                 '%.2f%%' % reviews_retry_rate)
                )

    # 发送邮件的参数
    # 发送邮件的数据格式
    msg_format = "%s模块：总共%s条数据， 已入库%s条数据， 未完成%s条数据， 完成度%.2f%%， 需重试%s， 重试率%.2f%%"
    # 没有库存, 价格, bsr, 标题, 品牌, 图片, 评论, 评分 的产品数量
    field_msg_format = "已入库产品总数 %s, 其中:\n " \
                       "没有inventory %s, 占比 %.2f%%\n" \
                       "没有price %s, 占比 %.2f%%\n" \
                       "没有bsr %s, 占比 %.2f%%\n" \
                       "没有title %s, 占比 %.2f%%\n" \
                       "没有brand %s, 占比 %.2f%%\n" \
                       "没有image %s, 占比 %.2f%%\n" \
                       "没有review count %s, 占比 %.2f%%\n" \
                       "没有review rating %s, 占比 %.2f%%\n"
    # 没有库存的比例
    not_qty_rate = not_qty_sum / goods_sum * 100
    # 没有价格的比例
    not_price_rate = not_price / goods_sum * 100
    # 没有bsr的比例
    not_bsr_rate = not_bsr / goods_sum * 100
    # 没有标题的比例
    not_title_rate = not_title / goods_sum * 100
    # 没有品牌的比例
    not_brand_rate = not_brand / goods_sum * 100
    # 没有图片的比例
    not_img_rate = not_img / goods_sum * 100
    # 没有评论的比例
    not_rc_rate = not_rc / goods_sum * 100
    # 没有评分的比例
    not_rrg_rate = not_rrg / goods_sum * 100
    print(field_msg_format % (
            goods_sum, not_qty_sum, not_qty_rate, not_price, not_price_rate, not_bsr, not_bsr_rate,
            not_title, not_title_rate, not_brand, not_brand_rate, not_img, not_img_rate,
            not_rc, not_rc_rate, not_rrg, not_rrg_rate
            ))

    # 要发送的信息
    msg_list = []
    # 发送的邮箱地址
    to_addr = to_addr_in
    to_addr1 = 'garyF@daisycorp.net,HSLiulei@aliyun.com,hongz@intechannel.com,'
    # to_addr1 = ''
    to_addr2 = ',dcpeter@aliyun.com,dcmargaret@aliyun.com'
    # to_addr2 = ''
    war_msg = '%s 模块 完成度%.2f%%'
    title_format = ' crawler report! PT: %s'

    # 判断产品入库的完成度  超过90%就发送邮件
    if goods_complete_rate >= 90:
        # 消息类型
        msg_type = 'product'
        # 做标记所需的键
        mark_key = msg_type + '90%' + the_date.strftime('%Y%m%d')
        if not mark_sent(urlQ, (mark_key,), mark_type='get'):
            # 专属的title_format
            the_title_format = msg_type + title_format
            msg_list.append(msg_format % (
            msg_type, goods_sum, goods_num, goods_unfinished, goods_complete_rate, goods_fail_sum,
            goods_retry_rate))
            msg_list.append(field_msg_format % (
            goods_sum, not_qty_sum, not_qty_rate, not_price, not_price_rate, not_bsr, not_bsr_rate,
            not_title, not_title_rate, not_brand, not_brand_rate, not_img, not_img_rate,
            not_rc, not_rc_rate, not_rrg, not_rrg_rate
            ))
            send_func(msg_list, war_msg % (msg_type, goods_complete_rate), the_title_format, to_addr1 + to_addr, from_addrs_name=from_addrs_name)
            # 标记发送状态, 以免重复发送
            mark_sent(urlQ, (mark_key, the_date.strftime('%Y%m%d %H:%M:%S')), mark_type='set')
        # 清空列表
        msg_list = []

    # 判断关键字入库的完成度  超过90%就发送邮件
    if kw_complete_rate >= 90:
        # 消息类型
        msg_type = 'keyword'
        # 做标记所需的键
        mark_key = msg_type + '90%' + the_date.strftime('%Y%m%d')
        if not mark_sent(urlQ, (mark_key,), mark_type='get'):
            # 专属的title_format
            the_title_format = msg_type + title_format
            msg_list.append(msg_format % (
            msg_type, kw_sum, kw_num, kw_unfinished, kw_complete_rate, kw_fail_sum, kw_retry_rate))
            send_func(msg_list, war_msg % (msg_type, kw_complete_rate), the_title_format, to_addr1 + to_addr, from_addrs_name=from_addrs_name)
            # 标记发送状态, 以免重复发送
            mark_sent(urlQ, (mark_key, the_date.strftime('%Y%m%d %H:%M:%S')), mark_type='set')
        # 清空列表
        msg_list = []
    # 判断跟卖入库的完成度  超过90%就发送邮件
    if tosell_complete_rate >= 90:
        # 消息类型
        msg_type = 'tosell'
        # 做标记所需的键
        mark_key = msg_type + '90%' + the_date.strftime('%Y%m%d')
        if not mark_sent(urlQ, (mark_key,), mark_type='get'):
            # 专属的title_format
            the_title_format = msg_type + title_format
            msg_list.append(msg_format % (
            msg_type, tosell_sum, tosell_num, tosell_unfinished, tosell_complete_rate, tosell_fail_sum,
            tosell_retry_rate))
            send_func(msg_list, war_msg % (msg_type, tosell_complete_rate), the_title_format, to_addr1 + to_addr, from_addrs_name=from_addrs_name)
            # 标记发送状态, 以免重复发送
            mark_sent(urlQ, (mark_key, the_date.strftime('%Y%m%d %H:%M:%S')), mark_type='set')
        # 清空列表
        msg_list = []
    # 判断评论入库的完成度  超过90%就发送邮件
    if reviews_complete_rate >= 90:
        # 消息类型
        msg_type = 'reviews'
        # 做标记所需的键
        mark_key = msg_type + '90%' + the_date.strftime('%Y%m%d')
        if not mark_sent(urlQ, (mark_key,), mark_type='get'):
            # 专属的title_format
            the_title_format = msg_type + title_format
            msg_list.append(msg_format % (
            msg_type, reviews_sum, reviews_num, reviews_unfinished, reviews_complete_rate, reviews_fail_sum,
            reviews_retry_rate))
            send_func(msg_list, war_msg % (msg_type, reviews_complete_rate), the_title_format, to_addr1 + to_addr, from_addrs_name=from_addrs_name)
            # 标记发送状态, 以免重复发送
            mark_sent(urlQ, (mark_key, the_date.strftime('%Y%m%d %H:%M:%S')), mark_type='set')
        # 清空列表
        msg_list = []

    # 每天太平洋时间17:00发送邮件
    # 获取当前时间太平洋时间
    if the_date.hour == 17:
        title_format = '爬虫统计报告 PT: %s'
        war_msg = '爬虫统计报告:'
        # 将每个类别的信息添加到队列
        msg_list.append(msg_format % (
            'product', goods_sum, goods_num, goods_unfinished, goods_complete_rate, goods_fail_sum,
            goods_retry_rate))
        msg_list.append(field_msg_format % (
            goods_sum, not_qty_sum, not_qty_rate, not_price, not_price_rate, not_bsr, not_bsr_rate,
            not_title, not_title_rate, not_brand, not_brand_rate, not_img, not_img_rate,
            not_rc, not_rc_rate, not_rrg, not_rrg_rate
        ))
        msg_list.append(msg_format % (
            'keyword', kw_sum, kw_num, kw_unfinished, kw_complete_rate, kw_fail_sum, kw_retry_rate))
        msg_list.append(msg_format % (
            'tosell', tosell_sum, tosell_num, tosell_unfinished, tosell_complete_rate, tosell_fail_sum,
            tosell_retry_rate))
        msg_list.append(msg_format % (
            'reviews', reviews_sum, reviews_num, reviews_unfinished, reviews_complete_rate, reviews_fail_sum,
            reviews_retry_rate))
        # 发送邮件
        send_func(msg_list, war_msg, title_format, to_addr1 + to_addr + to_addr2, from_addrs_name=from_addrs_name)


# 关键字统计
def keyword_retry(kwQ):
    url_type = 'keyword'
    sql = "select kw from public.amazon_keyword_monitor where state = 1 and monitor_tm > 0;"
    url_tuple_list = kwQ.retrieve_asin(sql)
    kw_sum = len(set(url_tuple_list))
    # print('关键字数 %s' % (len(url_tuple_list)))
    # print('(去重)关键字数 %s' % (len(set(url_tuple_list))))
    # print('keyword_retry: ', url_tuple_list)
    kw_num = -1
    fail_sum = -1
    sql_times = get_init_updae_tm(kwQ)
    if sql_times > 0:
        sql = "select kw from public.amazon_keyword_monitor where state = 1 and crawler_tm >= %s" % (
            sql_times)
        print(sql)  # url_tuple_list = urlQ.retrieve_asin(sql)
        url_tuple_list = kwQ.retrieve_asin(sql)
        kw_num = len(set(url_tuple_list))
        fail_sum = kwQ.RedisQ.zcard(url_type + 'fail')
        # print('已下载关键字数 %s' % (len(url_tuple_list)))
        # print('(去重)已下载关键字数 %s' % (len(set(url_tuple_list))))
        # print('重试关键字数 %d' % (fail_sum))
    return kw_sum, kw_num, fail_sum


# 商品统计
def goods_retry(urlQ):
    url_type = 'goods'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and info_tm > 0;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    goods_sum = len(set(url_tuple_list))
    # print('商品数 %s' % (len(url_tuple_list)))
    # print('(去重)商品数 %s' % (len(set(url_tuple_list))))
    goods_num = -1
    fail_sum = -1
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type > 0 and info_tm > 0 and info_tm_crawler >= %s" % (
            sql_times)
        url_tuple_list = urlQ.retrieve_asin(sql)
        sql1 = "select asin from public.amazon_product_data where asin_state=-1 and crawler_state=2 and getinfo_tm >= %s" % (
            sql_times)
        url_tuple_list1 = urlQ.retrieve_asin(sql1)
        goods_num = len(set(url_tuple_list))
        fail_goods = len(set(url_tuple_list1))
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        # print('已下载商品数 %s' % (len(url_tuple_list)))
        # print('(去重)已下载商品数 %s' % (len(set(url_tuple_list))))
        # print('下载失败商品数 %s' % (len(url_tuple_list1)))
        # print('(去重)下载失败商品数 %s' % (len(set(url_tuple_list1))))
        # print('重试商品数 %d' % (fail_sum))
    return goods_sum, goods_num, fail_sum, fail_goods
    # return goods_sum, goods_num, fail_sum


# 评论统计
def reviews_retry(urlQ):
    url_type = 'reviews'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 3 and monitor_type != 5 and comment_tm > 0 ;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    reviews_sum = len(set(url_tuple_list))
    # print('评论数 %s' % (len(url_tuple_list)))
    # print('(去重)评论数 %s' % (len(set(url_tuple_list))))
    reviews_num = -1
    fail_sum = -1
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 3 and monitor_type != 5 and comment_tm > 0 and comment_tm_crawler >= %s" % (
            sql_times)
        url_tuple_list = urlQ.retrieve_asin(sql)
        reviews_num = len(set(url_tuple_list))
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        # print('已下载评论数 %s' % (len(url_tuple_list)))
        # print('(去重)已下载评论数 %s' % (len(set(url_tuple_list))))
        # print('重试评论数 %d' % (fail_sum))
    return reviews_sum, reviews_num, fail_sum


# 跟卖统计
def tosell_retry(urlQ):
    url_type = 'tosell'
    sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 ;"
    url_tuple_list = urlQ.retrieve_asin(sql)
    tosell_sum = len(set(url_tuple_list))
    # print('跟卖数 %s' % (len(url_tuple_list)))
    # print('(去重)跟卖数 %s' % (len(set(url_tuple_list))))
    tosell_num = -1
    fail_sum = -1
    sql_times = get_init_updae_tm(urlQ)
    if sql_times:
        # sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 and tosell_tm_crawler >= %s;" % (sql_times)
        sql = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 \
and asin in (select asin from public.amazon_product_data_tosell where getinfo_tm > %s);" % (sql_times * 1000)
        url_tuple_list = urlQ.retrieve_asin(sql)
        sql1 = "select asin from public.amazon_product_monitor where state = 1 and monitor_type >= 5 and tosell_tm > 0 and \
        asin in (select asin from public.amazon_product_data where getinfo_tm > %s and asin_state = 0);" % (sql_times * 1000)
        url_tuple_list1 = urlQ.retrieve_asin(sql1)
        # print(sql)#url_tuple_list = urlQ.retrieve_asin(sql)
        tosell_num = len(set(url_tuple_list + url_tuple_list1))
        fail_sum = urlQ.RedisQ.zcard(url_type + 'fail') or 0
        # print('已下载跟卖数 %s' % (len(url_tuple_list)))
        # print('(去重)已下载跟卖数 %s' % (len(set(url_tuple_list))))
        # print('重试跟卖数 %d' % (fail_sum))
    return tosell_sum, tosell_num, fail_sum


# 库存统计
def qty_retry(urlQ):
    url_type = 'inventory'
    sql_times = get_init_updae_tm(urlQ)
    not_qty_sum = not_price = not_bsr = not_title = not_brand = not_img = not_rc = not_rrg = 0
    if sql_times:
        # 缺失少库存的产品数
        sql_qty = "select asin from public.amazon_product_data where quantity = -1 and asin_state = 3 and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        url_tuple_list1 = urlQ.retrieve_asin(sql_qty)
        not_qty_sum = len(url_tuple_list1)

        # 缺少价格的产品数
        sql_price = "select asin from public.amazon_product_data where asin_state=3 and price <=0 and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        price_tuple_list = urlQ.retrieve_asin(sql_price)
        not_price = len(price_tuple_list)

        # 缺少bsr的产品数
        sql_bsr = "select asin from public.amazon_product_data where asin_state!=0 and bsr <=0 and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        bsr_tuple_list = urlQ.retrieve_asin(sql_bsr)
        not_bsr = len(bsr_tuple_list)

        # 缺少标题的产品数
        sql_title = "select asin from public.amazon_product_data where asin_state!=0 and title = '' and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        title_tuple_list = urlQ.retrieve_asin(sql_title)
        not_title = len(title_tuple_list)

        # 缺少品牌的产品数
        sql_brand = "select asin from public.amazon_product_data where asin_state!=0 and brand = '' and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        brand_tuple_list = urlQ.retrieve_asin(sql_qty)
        not_brand = len(brand_tuple_list)

        # 缺少图片的产品数
        sql_img = "select asin from public.amazon_product_data where asin_state!=0 and image = '' and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        img_tuple_list = urlQ.retrieve_asin(sql_img)
        not_img = len(img_tuple_list)
        # 缺少评论 的产品数
        sql_rc = "select asin from public.amazon_product_data where asin_state!=0 and rc <= 0 and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        rc_tuple_list = urlQ.retrieve_asin(sql_rc)
        not_rc = len(rc_tuple_list)

        # 缺少评分的产品数
        sql_rrg = "select asin from public.amazon_product_data where asin_state!=0 and rrg <= 0 and getinfo_tm >= %s;" % (
                    sql_times * 1000)
        rrg_tuple_list = urlQ.retrieve_asin(sql_rrg)
        not_rrg = len(rrg_tuple_list)

    return not_qty_sum, not_price, not_bsr, not_title, not_brand, not_img, not_rc, not_rrg


if __name__ == '__main__':
    to_addr_in = 'HSXinqun@aliyun.com,BruceX@selmuch.com'
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    statistics(urlQ, to_addr_in)
