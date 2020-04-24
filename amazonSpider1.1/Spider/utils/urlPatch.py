#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import time

from utils.util import Logger, GetRedis, UrlQueue


def return_successUrlSet(queue, log):
    try:
        req = queue.smembers('successAsinSet')
        if len(req) > 0:
            log.debug('[读取[successUrlSet]成功]')
            return req
        else:
            log.debug('[读取[successUrlSet]失败]')
            return set()
    except Exception as e:
        log.error('读取[successUrlSet]时[%s]' % (e))
        return set()


def pop_successUrlSet(queue, log):
    try:
        req = queue.spop('successAsinSet')
        if req:
            log.debug('[弹出[successUrlSet]成功]')
            return req
        else:
            log.debug('[弹出[successUrlSet]失败]')
            return None
    except Exception as e:
        log.error('弹出[successUrlSet]时[%s]' % (e))
        return None


def return_UrlSet(queue, log):
    try:
        req = queue.llen('goodsUrlQueue')
        #req = queue.llen('tosellUrlQueue')
        #req = queue.llen('reviewsUrlQueue')
        if req:
            log.debug('[读取[UrlSet]成功]')
            return req
        else:
            log.debug('[读取[UrlSet]失败]')
            return 0
    except Exception as e:
        log.error('读取[UrlSet]时[%s]' % (e))
        return 0


def func(myRedis, urlQ, debug_log, num=60):
    print('url补丁程序启动')
    i = 0
    while True:
        time.sleep(num)
        i += 1
        print('url patch 循环计数 %s \n' % (i))
        if i % 10 == 0:
            i = 0
            print('url patch 开始工作 \n')
            urlSuccess = return_successUrlSet(myRedis, debug_log)
            urlNum = return_UrlSet(myRedis, debug_log)
            #urlNum = 0 
            print('urlSuccess数量：', len(urlSuccess))
            print('urlSet数量：', urlNum)
            if urlNum < 1:
                j = 0
                while True:
                    j += 1
                    req = pop_successUrlSet(myRedis, debug_log)
                    if req:
                        print('第%s个已下载url %s 弹出成功' % (j, req))
                    else:
                        print("已下载集合为空")
                        break
                #url_manager = AsinManager(urlQ, debug_log)
                #url_manager.start()

def pop_UrlSet(queue, log):
    try:
        #req = queue.spop('successUrlSet')
        #req = queue.rpop('goodsUrlQueue')
        #req = queue.rpop('tosellUrlQueue')
        req = queue.rpop('reviewsUrlQueue')
        if req:
            log.debug('[弹出[goodsUrlSet]成功]')
            return req
        else:
            log.debug('[弹出[goodsUrlSet]失败]')
            return None
    except Exception as e:
        log.error('弹出[goodsUrlSet]时[%s]' % (e))
        return None

def empty_UrlSet(myRedis, debug_log):
    while True:
        url = pop_UrlSet(myRedis, debug_log)
        if url is None:
            break
        print(url)

if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    #func(myRedis, urlQ, debug_log, 1)
    empty_UrlSet(myRedis, debug_log)
