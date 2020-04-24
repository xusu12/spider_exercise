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


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    while True:
        Qname = ''
        url_type = ''
        msg = input('-1.退出\n1.商品数据队列\n2.排名数据队列\n3.评论数据队列\n4.跟卖数据队列\n5.关键字数据队列\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 1:
                Qname = 'goodsData'
                url_type = 'goodsData'
            if msg == 2:
                Qname = 'bsrData'
                url_type = 'bsrData'
            if msg == 3:
                Qname = 'reviewsData'
                url_type = 'reviewsData'
            if msg == 4:
                Qname = 'tosellData'
                url_type = 'tosellData'
            if msg == 5:
                Qname = 'keywordData'
                url_type = 'keywordData'

        if Qname:
            look_queue_len(myRedis, Qname, url_type=url_type)