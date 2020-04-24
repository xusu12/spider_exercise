#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")

from utils.util import Logger, GetRedis


def empty_url_queue(myRedis, Qname):
    r = myRedis
    i = 0
    while True:
        i += 1
        url = r.rpop(Qname)
        if not url:
            break
    print('\n已删除url %s\n' % (i))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    while True:
        Qname = ''
        msg = input('-1.退出\n1.清空商品队列\n2.清空评论队列\n3.清空跟卖队列\n4.清空关键字队列\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 1:
                Qname = 'goodsUrlQueue'
            if msg == 2:
                Qname = 'reviewsUrlQueue'
            if msg == 3:
                Qname = 'tosellUrlQueue'
            if msg == 4:
                Qname = 'KeywordQueue'

        if Qname:
            empty_url_queue(myRedis, Qname)