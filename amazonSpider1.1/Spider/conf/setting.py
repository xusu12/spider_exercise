#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# import random
import sys
sys.path.append("../")


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PARENT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(PARENT_DIR, 'data')
REPORT_DIR = os.path.join(PARENT_DIR, 'report')
LOG_DIR = os.path.join(PARENT_DIR, 'log')
CRONTAB_DIR = os.path.join(PARENT_DIR, 'crontabLog')

# 线程数
GOODS_T_NUM = 5
REVIEWS_T_NUM = 0
TOSELL_T_NUM = 0
KEYWORD_T_NUM = 0

# 进程数
DATA_P_NUM =1
GOODS_P_NUM = 4
REVIEWS_P_NUM = 0
TOSELL_P_NUM = 0
KEYWORD_P_NUM = 0



# 访问间隔随机数区间
SLEEP1 = 7      # 开始
SLEEP2 = 12     # 结束

#PROXY_TOKEN = '17ffd18909b543339c08ac106a72fadb:' 
#PROXY_HOST = 'proxy.crawlera.com'
#PROXY_PORT = 8010
PROXY_TOKEN = 'intechannel:xPahemoXHG'
PROXY_HOST = 'cld-us-dxig.tp-ns.com'
PROXY_PORT = 80

PROXY_HTTP = "http://{}@{}:{}/".format(PROXY_TOKEN, PROXY_HOST, PROXY_PORT)
PROXY_HTTPS = "https://{}@{}:{}/".format(PROXY_TOKEN, PROXY_HOST, PROXY_PORT)
PROXY_VERIFY = os.path.join(os.path.join(BASE_DIR, 'conf'), 'crawlera-ca.crt')

PROXY_TOKEN = 'intechannel:xPahemoXHG'
PROXY_HOST = 'cld-us-dxig.tp-ns.com'
PROXY_PORT = 80
PROXY_HTTP_INV = "http://{}@{}:{}/".format(PROXY_TOKEN, PROXY_HOST, PROXY_PORT)
PROXY_HTTPS_INV = "https://{}@{}:{}/".format(PROXY_TOKEN, PROXY_HOST, PROXY_PORT)

LOG_TEM_DEBUG = ('GMT+8:%(asctime)s, PID:%(process)d, TID:[%(thread)d %(threadName)s, LEV:%(levelno)s %(levelname)s, MSG:, %(message)s','%Y-%m-%d %H:%M:%S')
LOG_TEM_INFO = ('GMT+8:%(asctime)s, TID:%(thread)d %(threadName)s, MSG:, %(message)s', '%Y-%m-%d %H:%M:%S')
LOG_TEM_DB = ('GMT+8:%(asctime)s, TID:%(thread)d %(threadName)s, MSG:, %(message)s', '%Y-%m-%d %H:%M:%S')
LOG_TEM_ERROR = ('GMT+8:%(asctime)s, PID:%(process)d, TID:%(thread)d %(threadName)s, LEV:%(levelno)s %(levelname)s, MSG:, %(message)s', '%Y-%m-%d %H:%M:%S')

REDIS_CONFIG = {
    "develop": dict(
        host='127.0.0.1',
        port=6379,
        db=6,
        max_connections=100,
        # decode_responses=True
    ),
    "test": dict(
        host='192.168.0.149',
        port=6379,
        db=6,
        max_connections=100,
    ),
    'production': dict(
        host='192.168.0.149',
        port=6380,
        db=8,
        max_connections=100,
    )
}

DATADB_CONFIG = {
    "develop": dict(
        #minconn=1,
        #maxconn=10,
        database='ic_crawler',
        user='postgres',
        password='123456',
        host='192.168.13.8',
        port='15432'
    ),
    "test": dict(
        database='ic_crawler',
        user='postgres',
        password='123456',
        host='192.168.0.149',
        port='15432'
    ),
    'production': dict(
        database='ic_crawler_online',
        user='postgres',
        password='123456',
        host='192.168.0.149',
        port='15432'
    )
}

# 修改此项, 快速变更数据库等配置
#BASE_TYPE = "develop"
#BASE_TYPE = "test"
BASE_TYPE = 'production'


if __name__ == '__main__':
    print(BASE_DIR)
    print(LOG_DIR)
    print(PROXY_VERIFY)
    print(REDIS_CONFIG)
    # print(SLEEP1)
    # print(SLEEP2)
    # print(DATADB_CONFIG)
