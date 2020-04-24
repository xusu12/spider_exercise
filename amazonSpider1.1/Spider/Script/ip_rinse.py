#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os

from conf.setting import BASE_DIR
from utils.util import Logger, GetRedis, IpQueue


def ip_rinse(ipQ):
    ip_list = []

    dataOut = os.path.join(BASE_DIR, 'Script/update_ip.py')
    shell = 'nohup python3 %s > /dev/null 2>&1 &' % (dataOut)
    print(shell)
    req = os.system(shell)
    print(req)
    if req == 0:
        print('update_ip.py done\n')

    while True:
        ip = ipQ.get_new_ip_from_set()
        if not ip:
            break
        ip_list.append(ip)
    print('\n当前ip队列长度: %s\n' % (len(ip_list)))
    ip_list = set(ip_list)
    print('\n去重后ip队列长度: %s\n' % (len(ip_list)))
    for ip in ip_list:
        if ip:
            ipQ.add_validIp_to_queue(ip)


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    ipQ = IpQueue(myRedis, debug_log)
    ip_rinse(ipQ)
