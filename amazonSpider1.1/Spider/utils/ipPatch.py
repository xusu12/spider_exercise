#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
# from threading import Thread
from utils.util import Logger, GetRedis, IpQueue



debug_log = Logger()
myRedis = GetRedis().return_redis(debug_log)
ipQ = IpQueue(myRedis, debug_log)


# 如果做了进程重启, 则需要清空已下ip锁, 不然回造成一些ip永远无法解锁
def func(myRedis):
    r = myRedis
    while True:
        ip = r.spop('useIpSet')
        if not ip:
            break
        print(ip, '弹出成功')


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    func(myRedis)
