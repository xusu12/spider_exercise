#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
from utils.util import Logger, GetRedis, IpQueue


def update_ip_crontab(ipQ):
    '''无脑补充ip, 启动服务的时候运行一次'''
    ipList = ipQ.retrieve_ip()
    print(len(ipList))
    if len(ipList) > 0:
        for ip in ipList:
            ipQ.add_validIp_to_queue(ip)

if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    ipQ = IpQueue(myRedis, debug_log)
    update_ip_crontab(ipQ)
