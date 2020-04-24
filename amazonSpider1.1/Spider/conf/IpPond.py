#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os

from conf.setting import BASE_DIR

# 提取去重后的ip
def set_ip():
    for ip in IPPOND:
        file = os.path.join(BASE_DIR, 'conf/IPPOND.txt')
        with open(file, 'a', encoding='utf-8') as f:
            f.write(ip + '\n')

def ipPond(filename=''):
    file = os.path.join(BASE_DIR, 'conf/IPPOND.ini')
    result = []
    if filename:
        file = filename
    with open(file, 'r', encoding='utf-8') as f:
        rList = f.readlines()
    for r in rList:
        r = r.lstrip().strip()
        if r:
            result.append(r)
    return set(result)

IPPOND = ipPond()
# print(len(IPPOND))



