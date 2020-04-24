#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import os


# 获得shell返回值
def shell_return(shell):
    pObj = os.popen(shell)
    pstring = pObj.read()
    return pstring


# 获得进程id
def get_pid(pstring):
    pList = pstring.split('\n')
    rList = []
    pidList = []
    for p in pList:
        if p and type(p) is str:
            if not 'grep' in p:
                rList.append(p)
    for r in rList:
        if r and type(r) is str:
            pid = r.split(' ')
            idList = []
            for p in pid:
                p = p.strip().lstrip()
                if p:
                    idList.append(p)
            pidList.append(idList[1])

    return pidList


# 杀死进程
def kill_process(pidList):
    pNum = len(pidList)
    print('\n进程数 %s个' % (pNum))
    if pNum > 0:
        print(pidList)
        pid = ' '.join(pidList)
        shell = 'kill %s' % (pid)
        # print(shell)
        req = os.system(shell)
        if req == 0:
            print('已杀死全部进程 %s个\n' % (pNum))
    else:
        print('')


if __name__ == '__main__':
    while True:
        shell = ''
        msg = input('-1.退出\n0.全部进程\n1.商品进程\n2.评论进程\n3.跟卖进程\n4.关键字进程\n5.数据进程\n请输入相应数字:')
        if msg == '-1':
            break
        if msg.isdigit():
            msg = eval(msg)
            if msg == 0:
                shell = 'ps -ef | grep Spider/Crawler/'
            if msg == 1:
                shell = 'ps -ef | grep goodsCrawler.py'
            if msg == 2:
                shell = 'ps -ef | grep reviewsCrawler.py'
            if msg == 3:
                shell = 'ps -ef | grep tosellCrawler.py'
            if msg == 4:
                shell = 'ps -ef | grep keywordCrawler.py'
            if msg == 5:
                shell = 'ps -ef | grep DataOutput.py'
        if shell:
            kill_process(get_pid(shell_return(shell)))