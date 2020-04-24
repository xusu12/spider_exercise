#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
# import time
# from threading import Thread
from utils.util import Logger, GetRedis


def empty_ip_queue(myRedis, Qname):
    r = myRedis
    while True:
        ip = r.rpop(Qname)
        if not ip:
            break
        print('ip %s 已删除' % (ip))


# 如果做了进程重启操作, 则需要清空已下ip锁, 不然会造成一些ip永远无法解锁
def func(myRedis, Qname):
    r = myRedis
    while True:
        ip = r.rpop(Qname)
        if not ip:
            break
        print('ip锁 %s已删除' % (ip))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    while True:
        Qname = ''
        msg = input('-1.退出\n1.清空goodsData\n2.清空ip队列\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 1:
                Qname = 'goodsData'
                func(myRedis, Qname)
            if msg == 2:
                Qname = 'validIpQueue'
                empty_ip_queue(myRedis, Qname)
