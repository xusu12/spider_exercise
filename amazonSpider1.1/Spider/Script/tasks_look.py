#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import os
import time

from utils.util import Logger, GetRedis


def look_queue_len(myRedis, Qname, url_type=''):
    r = myRedis
    url_len = r.llen(Qname)
    print('\n%s len: %s\n' % (url_type, url_len))

def look_set_len(myRedis, sName, set_type=''):
    r = myRedis
    the_set = r.smembers(sName)
    the_len = len(the_set)
    print('\n%s len: %s\n' % (set_type, the_len))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    while True:
        Qname = ''
        url_type = ''
        msg = input('-1.退出\n1.查看商品队列长度\n2.查看评论队列长度\n3.查看跟卖队列长度\n'
                    '4.查看关键字队列长度\n5.查看有效ip队列长度\n6.查看ip锁数量'
                    '\n7.查看任务总数\n8.查看已完成任务数\n9.查看新任务数\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 1:
                Qname = 'goodsUrlQueue'
                url_type = 'goods'
            if msg == 2:
                Qname = 'reviewsUrlQueue'
                url_type = 'reviews'
            if msg == 3:
                Qname = 'tosellUrlQueue'
                url_type = 'tosell'
            if msg == 4:
                Qname = 'KeywordQueue'
                url_type = 'keyword'
            if msg == 5:
                Qname = 'validIpQueue'
                url_type = 'validIp'
            if msg == 6:
                sName = 'useIpSet'
                set_type = 'ip lock'
                look_set_len(myRedis, sName, set_type)
            if msg == 7:
                sName = 'asinAndKwSet'
                set_type = 'tasks sum queue'
                look_set_len(myRedis, sName, set_type)
            if msg == 8:
                sName = 'successAsinSet'
                set_type = 'tasks success queue'
                look_set_len(myRedis, sName, set_type)
            if msg == 9:
                uType = 'monitor'
                gNme = uType + 'Goods'
                look_queue_len(myRedis, gNme, url_type=gNme)
                rNme = uType + 'Reviews'
                look_queue_len(myRedis, rNme, url_type=rNme)
                tNme = uType + 'Tosell'
                look_queue_len(myRedis, tNme, url_type=tNme)
                kNme = uType + 'Keyword'
                look_queue_len(myRedis, kNme, url_type=kNme)

        if Qname:
            look_queue_len(myRedis, Qname, url_type=url_type)
