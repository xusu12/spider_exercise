#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import pickle

from utils.util import Logger, GetRedis, KeyWordQueue


def add_keyword(KwQ, keyword_tuple):
    keyword_bytes = pickle.dumps(keyword_tuple)
    result = KwQ.jump_queue_to_keyword(keyword_bytes)
    if not result:
        KwQ.add_keyword_to_queue(keyword_bytes)


def func(KwQ, sql):
    print(sql)
    keywords = KwQ.retrieve_keyword(sql)
    print('keywords: ', len(keywords))
    for keyword in keywords:
        add_keyword(KwQ, keyword)

if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    KwQ = KeyWordQueue(myRedis, debug_log)
    sql = "select kw, cid, aid from public.amazon_keyword_monitor where aid='3';"
    # func(KwQ, sql)
    '''keyword_tuple = (kw, cid, aid)'''
    keyword_tuple = ('sterling silver engagement rings', 0, '3')
    add_keyword(KwQ, keyword_tuple)

