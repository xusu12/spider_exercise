#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import time
import pickle
from utils.util import Logger, GetRedis, UrlQueue, KeyWordQueue

def add_url_to_queue(theQueue, url_tuple_list, tm_key='', url_type='', qType=''):
    print('add_url_to_queue.url_type: ', url_type)

    def add_to_queue(theQueue, url_tuple_bytes, url_type='', qType=''):
        print('url_type: ', url_type)
        the_qType = None
        if qType == 'monitor':
            the_qType = qType
        result = False
        if url_type == 'goods':
            result = theQueue.add_goods_url_to_queue(url_tuple_bytes, the_qType)
        if url_type == 'reviews':
            result = theQueue.add_reviews_url_to_queue(url_tuple_bytes, the_qType)
        if url_type == 'tosell':
            result = theQueue.add_tosell_url_to_queue(url_tuple_bytes, the_qType)
            print('tosell result: ', result)
        if url_type == 'keyword':
            result = theQueue.add_keyword_to_queue(url_tuple_bytes, the_qType)
        print('result', result, 'result')
        return result
    monitor_tm_list = []
    # print(url_tuple_list)
    for urlTuple in url_tuple_list:
        # print(urlTuple)
        kw_asin = urlTuple[0]
        cid_monitorType = urlTuple[1]
        aid = urlTuple[2]
        md5value = kw_asin + url_type
        md5key = theQueue.get_md5_key(md5value)
        if not theQueue.is_exists_asinAndKwSet(md5key):
            url_tuple_bytes = pickle.dumps((kw_asin, cid_monitorType, aid))
            print(url_tuple_bytes, 1, md5value)
            result = add_to_queue(theQueue, url_tuple_bytes, url_type, qType)
            print(url_tuple_bytes, 2, md5value)
            if result:
                print(url_tuple_bytes, result, md5value)
                theQueue.add_asinAndKw_to_set(md5key)
                if qType == 'monitor':
                    set_name = 'NewUrl'
                    theQueue._add_member_to_set(set_name, md5key)




def add_the_url_to_queue(url_list, url_type):
    print('add_the_url_to_queue.url_type: ', url_type)
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    kwQ = KeyWordQueue(myRedis, debug_log)
    theQueue = urlQ
    if url_type == 'keyword':
        theQueue = kwQ
    aid = 0
    cid_or_mt = 0
    if url_type == 'goods':
        cid_or_mt = 1
    if url_type == 'reviews':
        cid_or_mt = 3
    if url_type == 'tosell':
        cid_or_mt = 5
    url_tuple_list = []
    for url in url_list:
        url_tuple = (url, cid_or_mt, aid)
        print(url_tuple)
        url_tuple_list.append(url_tuple)

    if len(url_tuple_list) > 0:
        add_url_to_queue(theQueue, url_tuple_list, url_type=url_type)


if __name__ == '__main__':
    # url_type = 'keyword'
    # url_type = 'goods'
    # url_type = 'reviews'
    url_type = 'tosell'
    url_list = [
        'B078RDTF1D',
        'B078RDTF1D',
        'B002B4I8RA',
        'B0785R1DJP',
        'B0753HQ5M1',
        'B07899RFK7',
        'B00E67N6IQ',
        'B076V3RFWP',
        '0451467108',
        'B002EYI19M',
        'B01AFI3ERM',
        'B00WF988BW',
        'B00HV9IM58',
        '0316346934',
        'B07144HYK8',
        'B000677QW2',
        'B01LY5941N',
        'B074VMFW8B',
        'B01K1JVZOE',
        'B077JCLQTK',
        'B00PQ4PJYC',
        'B00VQK6D3G',
        'B01N32NCPM',
        'B00N92MUTU',
        'B076CG985W',
        'B017NGQWA0',
        'B003N9M6YI',
        'B01KXVF6WW',
        'B013QO1KEQ',
        'B00ZIW4AZ6',
        'B002H950DO',
        'B07B8RLX91',
        'B072JKCL7D',
        'B00X8MRBCW',
        'B00BJFJCSQ',
        'B00004Z4DU',
        'B00APKZGBS',
        'B074GLVNHC',
    ]

    add_the_url_to_queue(url_list, url_type)

