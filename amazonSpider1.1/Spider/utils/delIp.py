#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import time

from utils.util import GetRedis
from utils.util import Logger
from conf.setting import BASE_DIR



def func(myRedis, ipList):
    '''用来删除队列中的废ip'''
    r = myRedis
    for ip in ipList:
        ipQueueNum = r.lrem('validIpQueue', ip)
        if ipQueueNum > 0:
            print('\nipQueueNum: ', ipQueueNum, ip, '\n')
        ipNum = r.srem('IpSet', ip)
        if ipNum > 0:
            print('\nipNum: ', ipNum, ip, '\n')
        # time.sleep(0.5)
        sleepNum = r.srem('sleepIpSet', ip)
        if sleepNum > 0:
            print('\nsleepNum: ', sleepNum, ip, '\n')
        # time.sleep(0.5)
        disabledNum = r.srem('disabledIpSet', ip)
        if disabledNum > 0:
            print('\ndisabledNum: ', disabledNum, ip, '\n')
        # time.sleep(0.5)
        disabTimesNum = r.zrem('disabledIpTimes', ip)
        if disabTimesNum > 0:
            print('\ndisabTimesNum: ', disabTimesNum, ip, '\n')
        # time.sleep(0.5)
        sleepTimesNum = r.zrem('RobotCheckIpTimes', ip)
        if sleepTimesNum > 0:
            print('\nsleepTimesNum: ', sleepTimesNum, ip, '\n')
        # time.sleep(0.5)


def readIp(filename=''):
    file = os.path.join(BASE_DIR, 'utils/delIp.ini')
    result = []
    if filename:
        file = filename
    with open(file, 'r', encoding='utf-8') as f:
        rList = f.readlines()
    for r in rList:
        if r:
            result.append(r.lstrip().strip())
    return result


if __name__ == '__main__':
    # 删除已失效ip
    ipList = readIp()
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    func(myRedis, ipList)