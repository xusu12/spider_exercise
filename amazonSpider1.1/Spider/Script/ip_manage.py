#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import os
import time

from conf.setting import DATA_DIR
from utils.util import Logger, GetRedis


def look_queue_len(myRedis, Qname, url_type=''):
    r = myRedis
    url_len = r.llen(Qname)
    print('\n%s len: %s\n' % (url_type, url_len))

def save_ip_to_file(msg, filename=''):
    '''msg是一个带换行符的大字符串'''
    file = os.path.join(DATA_DIR, 'delIp.ini')
    if filename:
        file = filename
    with open(file, 'w', encoding='utf-8') as f:
        f.write(msg)

def save_ip(myRedis, sName):
    the_set = read_set(myRedis, sName)
    ip_list = []
    if the_set:
        for ip in the_set:
            ip_list.append(str(ip, encoding='utf-8'))
    msg = '\n'.join(ip_list)
    save_ip_to_file(msg)


def read_set(myRedis, sName):
    r = myRedis
    the_set = r.smembers(sName)
    return the_set

def look_set_len(myRedis, sName, set_type=''):
    the_set = read_set(myRedis, sName)
    the_len = len(the_set)
    print('\n%s len: %s\n' % (set_type, the_len))


def del_ip(myRedis, Qname):
    r = myRedis
    while True:
        ip = r.spop(Qname)
        if not ip:
            break
        print('废ip %s已删除' % (ip))


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    while True:
        Qname = ''
        msg = input('-1.退出\n1.查看废弃ip数量\n2.提取废弃ip到文件\n3.清空废弃ip\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 1:
                Qname = 'disabledIpSet'
                look_set_len(myRedis, Qname)
            if msg == 2:
                Qname = 'disabledIpSet'
                save_ip(myRedis, Qname)
            if msg == 3:
                Qname = 'disabledIpSet'
                del_ip(myRedis, Qname)
