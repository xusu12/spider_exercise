#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import time
from functools import wraps

from utils.util import Logger
from utils.util import GetRedis


def timer(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        the_type = sys.argv[0].split('/')[-1].split('.')[0]
        print(args, kwargs)
        log = Logger(log_level='info', log_name=the_type + '_timer')
        log_type = the_type if the_type else kwargs.get('url_type')
        print('type', the_type, 'log_type', log_type)
        datenow = lambda time_int: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_int))
        timenow = lambda: time.time()
        time1 = timenow()
        print('%s => function: %s, start, %s' % (log_type, func.__name__, datenow(time1)))
        result = func(*args, **kwargs)
        print('%s => function: %s, end, %s, timer:%.6fs' % (log_type, func.__name__, datenow(time1), timenow() - time1))
        log.info('type,%s,function,%s,start,%s,end,%s,timer,%.6f' % (
        log_type, func.__name__, datenow(time1), datenow(timenow()), timenow() - time1))
        return result
    return wrap


def async_lock(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        R = GetRedis().return_redis(None)
        def get_lock(*args, **kwargs):
            proxy = args[0] if len(args) > 0 and type(args[0]) is dict else kwargs
            print(proxy)
            print(kwargs)
            if 'proxy.crawlera.com' in proxy.get('proxies', {}).get('https', ''):
                # 从crawler1集合(待取锁), 获取锁
                the_lock = R.spop('crawler1')
                print(the_lock)
                if the_lock:
                    # 加入crawler2集合(在用锁)后, 增加使用状态(用来检查锁是否活跃), 返回锁
                    if R.sadd('crawler2', the_lock):
                        if R.set(the_lock, 'used', 60):
                            return the_lock
            elif 'cld-us-dxig.tp-ns.com' in proxy.get('proxies', {}).get('https', ''):
                # 从dxig1集合(待取锁), 获取锁
                the_lock = R.spop('dxig1')
                # 如果锁用过, 返回空.
                if R.get(the_lock):
                    return None
                else:
                    # 标记锁(此proxy每分钟不能超过600次请求, 所以每分钟每个锁只能用一次), 后返回锁.
                    if R.set(the_lock, 'used', 60):
                        return the_lock
            else:
                pass

        def rele_lock(*args, **kwargs):
            proxy = args[0] if len(args) > 0 and type(args[0]) is dict else kwargs
            if 'proxy.crawlera.com' in proxy.get('proxies', {}).get('https', ''):
                # 用完后, 将所从crawler2(在用锁)删除, 并加回crawler1(待取锁)
                if R.srem('crawler2', kwargs.get('the_lock')):
                    return R.sadd('crawler1', kwargs.get('the_lock'))
            elif 'cld-us-dxig.tp-ns.com' in proxy.get('proxies', {}).get('https', ''):
                pass
            else:
                pass

        i = 0
        while 1:
            i += 1
            the_lock = get_lock(*args, **kwargs)  # 获取锁
            print(the_lock)
            if the_lock:
                break
            elif i == 100:
                break
            else:
                print('restart get locak')
                time.sleep(0.1)
        if the_lock:
            result = func(*args, **kwargs)
            # 还回锁, 再返回值
            kwargs['the_lock'] = the_lock
            rele_lock(*args, **kwargs)
            return result
        else:
            raise Exception('get asycn lock timeout')
    return wrap


@timer
# @async_lock
def func():
    return 'locak'


if __name__ == '__main__':
    print(func())