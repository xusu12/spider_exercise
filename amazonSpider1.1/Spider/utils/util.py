#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import time
from cloghandler import ConcurrentRotatingFileHandler
from datetime import datetime
import pickle
import logging
import hashlib
from random import choice
from random import randint
from random import random

import psycopg2
from redis import Redis
from redis import ConnectionPool
import pytz
from fake_useragent import UserAgent

# 导入base目录
from conf.setting import BASE_DIR
# redis 配置字典
from conf.setting import REDIS_CONFIG
# db 配置字典
from conf.setting import DATADB_CONFIG
# 运行类型(开发\测试\生产)
from conf.setting import BASE_TYPE
# 休眠间隔区间
from conf.setting import SLEEP1, SLEEP2

# 日志文件路径
from conf.setting import LOG_DIR
# 日志模板
from conf.setting import LOG_TEM_DEBUG
from conf.setting import LOG_TEM_INFO
from conf.setting import LOG_TEM_ERROR
from conf.setting import LOG_TEM_DB
# 测试asin与ip
from conf.IpPond import IPPOND

# 导入UA池
from conf.UaPond import UAPOND


# 覆写Redis类
class MyRedis(Redis):
    obj = None

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = object.__new__(cls)
        return cls.obj


# 获取redis实例
class GetRedis:
    def return_redis(self, debug_log):
        try:
            redisPool = ConnectionPool(**REDIS_CONFIG[BASE_TYPE])
            redisObj = MyRedis(connection_pool=redisPool)
            # print(id(debug_log))
            # print('1[redis连接成功 {}]'.format(redisObj))
            debug_log.info('[redis连接成功 {}]'.format(redisObj))
            # print('2[redis连接成功 {}]'.format(redisObj))
            return redisObj
        except Exception as e:
            debug_log.error('[redis连接失败,1秒后重试] [%s]' % (e))
            time.sleep(1)
            for i in range(10):
                debug_log.error('[redis第%s次连接重试...]' % (i))
                self.return_redis(debug_log)
                time.sleep(1)
            return


class BaseQueue:
    def __init__(self, RedisQ, log):
        self.RedisQ = RedisQ
        self.log = log

    # 获取md5码
    @staticmethod
    def get_md5_key(value_str):
        '''value_str 必须是一个字符串, 只返回其中16位md5码, 节约内存'''
        return hashlib.md5(value_str.encode('utf-8')).hexdigest()[8: -8]

    def _get_value_from_string(self, the_key, key_type):
        try:
            req = self.RedisQ.get(the_key)
            if req:
                self.log.debug('get一个[%s]成功[%s]' % (key_type, req))
                return req
            else:
                self.log.debug('get一个[%s]失败, [%s]的值不存在' % (key_type, the_key))
                return None
        except Exception as e:
            self.log.error('get一个[%s]时[%s]' % (key_type, e))
            return None


    def _set_key_value_to_string(self, the_key, the_value, key_type, overtime=60):
        try:
            req = self.RedisQ.set(the_key, the_value, overtime)
            if req:
                self.log.debug('set1个[%s]成功' % (key_type))
                return True
            else:
                self.log.debug('set1个[%s]失败' % (key_type))
                return False
        except Exception as e:
            self.log.error('set1个[%s][key: %s][value: %s]时[%s]' % (key_type, the_key, the_value, e))
            return False

    # 返回有序集合成员及分数的元组列表
    def _return_member_list_form_zset(self, zset_name, num=1, i=1, amount=100):
        '''默认返回失效1次以上的成员100个, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        try:
            req = self.RedisQ.zrangebyscore(zset_name, num * i, float('Inf'), 0, amount, withscores=True)
            if len(req) > 0:
                self.log.debug('读取[%s]成功' % (zset_name))
                return req
            else:
                self.log.debug('读取[%s]失败, 集合为空' % (zset_name))
                return []
        except Exception as e:
            self.log.error('读取[%s]时[%s]' % (zset_name, e))

    # 返回有序集合的成员分数
    def _return_zscore(self, zset_name, member):
        try:
            req = self.RedisQ.zscore(zset_name, member)
            if req and type(req) is float:
                self.log.debug('[从%s 读取[%s]分数成功]' % (zset_name, member))
                return int(req)
            else:
                self.log.debug('[从%s 读取[%s]分数失败]' % (zset_name, member))
                return 0
        except Exception as e:
            self.log.error('从%s 读取[%s]分数时[%s]' % (zset_name, member, e))
            return 0

    # 删除有序集合中的成员
    def _pop_zset_member(self, zset_name, member):
        try:
            req = self.RedisQ.zrem(zset_name, member)
            if req > 0:
                self.log.debug('从[%s]中移除[%s]成功' % (zset_name, member))
                return True
            else:
                return False
        except Exception as e:
            self.log.error('从[%s]中移除[%s]时[%s]' % (zset_name, member, e))
            return False

    # 记录成员分数(统计次数)
    def _record_member_times(self, zset_name, member):
        try:
            req = self.RedisQ.zincrby(zset_name, member, 1)
            if req > 0:
                self.log.debug('[%s]写入[%s]成功' % (member, zset_name))
                return True
            else:
                self.log.debug('[%s]写入[%s]失败' % (member, zset_name))
                return False
        except Exception as e:
            self.log.error('[%s]写入[%s]时[%s]' % (member, zset_name, e))
            return False

    # 返回集合中的成员
    def _return_member_from_set(self, set_name):
        try:
            req = self.RedisQ.smembers(set_name)
            if len(req) > 0:
                self.log.debug('读取[%s]成功' % (set_name))
                return req
            else:
                self.log.debug('读取[%s]失败, 集合为空' % (set_name))
                return set()
        except Exception as e:
            self.log.error('读取[%s]时[%s]' % (set_name, e))
            return set()

    # 增加成员到集合(去重)
    def _add_member_to_set(self, set_name, member):
        try:
            req = self.RedisQ.sadd(set_name, member)
            if req > 0:
                self.log.debug('[%s] 写入[%s]成功' % (set_name, member))
                return True
            else:
                self.log.debug('[%s] 写入[%s]失败' % (set_name, member))
                return False
        except Exception as e:
            self.log.error('[%s] 写入[%s]时[%s]' % (member, set_name, e))
            return False

    # 从集合弹出成员
    def _pop_member_from_set(self, set_name):
        try:
            req = self.RedisQ.spop(set_name)
            if req:
                self.log.debug('从[%s]弹出一个[%s]成功' % (set_name, req))
                return req
            else:
                self.log.debug('从[%s]弹出一个成员失败成功, 集合为空' % (set_name))
                return None
        except Exception as e:
            self.log.error('从[%s]弹出成员时[%s]' % (set_name, e))
            return None
        
    # 增加成员到队列
    def _add_member_to_queue(self, queue_name, member):
        try:
            req = self.RedisQ.lpush(queue_name, member)
            if req > 0:
                self.log.debug('[%s]写入[%s]成功' % (member, queue_name))
                return True
            else:
                self.log.debug('[%s]写入[%s]失败' % (member, queue_name))
                return False
        except Exception as e:
            self.log.error('[%s]写入[%s]时[%s]' % (member, queue_name, e))
            return False
    
    # 从队列获取成员(timeout)
    def _get_member_from_queue(self, queue_name, timeout=30):
        try:
            req = self.RedisQ.brpop(queue_name, timeout=timeout)
            if req:
                self.log.debug('从[%s]中获取[%s]成功' % (queue_name, req))
                return req
            else:
                self.log.debug('从[%s]中获取成员超时[timeout=%s]' % (queue_name, timeout))
                return tuple()
        except NameError as e:
            self.log.error('从[%s]中获取成员时[%s]' % (queue_name, e))
            return tuple()
        except Exception as e:
            self.log.error('从[%s]中获取成员时[%s]' % (queue_name, e))
            return tuple()

    # 从队列获取成员(not timeout)
    def _get_member_from_q(self, queue_name):
        try:
            req = self.RedisQ.rpop(queue_name)
            # print('\n', req, '\n')
            if req:
                self.log.debug('从[%s]中获取[%s]成功' % (queue_name, req))
                return req
            else:
                self.log.debug('从[%s]中获取成员失败' % (queue_name))
                return ''
        except NameError as e:
            self.log.error('从[%s]中获取成员时[%s]' % (queue_name, e))
            return ''
        except Exception as e:
            self.log.error('从[%s]中获取成员时[%s]' % (queue_name, e))
            return ''

    # 优先插入到队列
    def _rpushx_member_to_queue(self, queue_name, member):
        try:
            req = self.RedisQ.rpushx(queue_name, member)
            if req > 0:
                self.log.debug('[%s]插队写入[%s]成功' % (member, queue_name))
                return True
            else:
                self.log.debug('[%s]插队写入[%s]失败' % (member, queue_name))
                return False
        except Exception as e:
            self.log.error('[%s]插队写入[%s]时[%s]' % (member, queue_name, e))
            return False

    # 获取队列长度
    def _get_queue_len(self, queue_name):
        try:
            req = self.RedisQ.llen(queue_name)
            if req > 0:
                self.log.debug('获取队列[%s]的长度成功' % (queue_name))
                return req
            else:
                self.log.debug('获取队列[%s]的长度失败' % (queue_name))
                return 0
        except Exception as e:
            self.log.error('获取队列[%s]的长度时[%s]' % (queue_name, e))
            return 0

    # 判断成员是否存在于集合
    def _the_member_is_exist_in_set(self, set_name, member):
        try:
            req = self.RedisQ.sismember(set_name, member)
            if req > 0:
                self.log.debug('[%s] 存在[%s]中' % (member, set_name))
                return True
            else:
                self.log.debug('[%s] 不存在[%s]中' % (member, set_name))
                return False
        except Exception as e:
            self.log.error('查询 [%s] 是否存在[%s]中时[%s]' % (member, set_name, e))
            return False

    # 删除集合中的成员
    def _srem_member_from_set(self, set_name, member):
        try:
            req = self.RedisQ.srem(set_name, member)
            if req > 0:
                self.log.debug('从[%s]中删除[%s]成功' % (set_name, member))
                return True
            else:
                self.log.debug('从[%s]中删除[%s]失败, 集合中没有此成员' % (set_name, member))
                return False
        except Exception as e:
            self.log.error('从[%s]中删除[%s]时[%s]' % (set_name, member, e))
            return False


class BaseUrlQueue(BaseQueue):

    # 增加到asin与kw集合(去重)
    def add_asinAndKw_to_set(self, asin_kw_md5key):
        set_name = 'asinAndKwSet'
        result = self._add_member_to_set(set_name, asin_kw_md5key)
        return result

    # 从asin与kw集合弹出bytes
    def pop_asinAndKw_from_set(self):
        set_name = 'asinAndKwSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 读取asin与kw集合长度
    def retrieve_asinAndKwSet(self):
        set_name = 'asinAndKwSet'
        result = self._return_member_from_set(set_name)
        return result

    # 删除asin与kw集合中的成员
    def srem_asinAndKw_from_set(self, md5key):
        set_name = 'asinAndKwSet'
        result = self._srem_member_from_set(set_name, md5key)
        return result

    # 是否已添加
    def is_exists_asinAndKwSet(self, asin_kw_md5key):
        set_name = 'asinAndKwSet'
        result = self._the_member_is_exist_in_set(set_name, asin_kw_md5key)
        return result

    # 增加到下载失败集合
    def add_defeated_url_to_set(self, url_tuple):
        set_name = 'defeated_urlSet'
        result = False
        if type(url_tuple) is tuple:
            url_bytes = pickle.dumps(url_tuple)
            result = self._add_member_to_set(set_name, url_bytes)
        return result

    # 读取下载失败集合
    def retrieve_defeated_urlSet(self):
        set_name = 'defeated_urlSet'
        result = self._return_member_from_set(set_name)
        return result

    # 从下载失败集合弹出
    def pop_defeated_urlSet(self):
        set_name = 'defeated_urlSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 增加到已下载asin集合
    def add_success_asin_to_set(self, asin):
        set_name = 'successAsinSet'
        result = self._add_member_to_set(set_name, asin)
        return result

    # 读取已下载集合
    def retrieve_successAsinKwSet(self):
        set_name = 'successAsinSet'
        result = self._return_member_from_set(set_name)
        return result

    # 从已下载集合弹出
    def pop_successAsinKwSet(self):
        set_name = 'successAsinSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 判断是否已下载
    def is_downloaded(self, asin_kw_md5key):
        set_name = 'successAsinSet'
        result = self._the_member_is_exist_in_set(set_name, asin_kw_md5key)
        return result

    # 删除已下载集合中的成员
    def srem_successAsinSet_from_set(self, md5key):
        set_name = 'successAsinSet'
        result = self._srem_member_from_set(set_name, md5key)
        return result

    # 更新任务总数
    def update_mission_attempts(self, num):
        num0 = self.get_mission_attempts()
        numSum = num0 + num
        result = self.set_mission_attempts(numSum)
        return result

    # 记录任务总数
    def set_mission_attempts(self, num):
        value = pickle.dumps(num)
        str_key = 'urlSum'
        result = self._set_key_value_to_string(str_key, value, str_key, overtime=72000)
        return result

    # 读取任务总数
    def get_mission_attempts(self):
        str_key = 'urlSum'
        result = 0
        result0 = self._get_value_from_string(str_key, str_key)
        if result0:
            result1 = pickle.loads(result0)
            if type(result1) is int:
                result = result1
        return result

    # 记录url被反爬次数
    def record_RobotCheck_url_times(self, url):
        zset_name = 'urlRobotCheckTimes'
        result = self._record_member_times(zset_name, url)
        return result

    # 获取url被反爬的次数
    def get_RobotCheck_url_times(self, url):
        zset_name = 'urlRobotCheckTimes'
        score = self._return_zscore(zset_name, url)
        return score

    # 读取被反爬 N 次的url
    def return_RobotCheck_url_times(self, num=1, i=1, amount=1000):
        '''默认返回失效1次以上的ip, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        zset_name = 'urlRobotCheckTimes'
        result_list = self._return_member_list_form_zset(zset_name, num=num, i=i, amount=amount)
        return result_list

    # 弹出被反爬 N 次的url
    def pop_RobotCheck_url_times(self, url):
        zset_name = 'urlRobotCheckTimes'
        result = self._pop_zset_member(zset_name, url)
        return result

    # 记录url失败次数
    def record_defeated_url_times(self, url):
        zset_name = 'urlDefeatedTimes'
        result = self._record_member_times(zset_name, url)
        return result

    # 获取url下载失败的次数
    def get_defeated_url_times(self, url):
        zset_name = 'urlDefeatedTimes'
        score = self._return_zscore(zset_name, url)
        return score

    # 读取失败 N 次的url
    def return_defeated_url_times(self, num=1, i=1, amount=1000):
        '''默认返回失效1次以上的ip, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        zset_name = 'urlDefeatedTimes'
        result_list = self._return_member_list_form_zset(zset_name, num=num, i=i, amount=amount)
        return result_list

    # 弹出失败 N 次的url
    def pop_defeated_url_times(self, url):
        zset_name = 'urlDefeatedTimes'
        result = self._pop_zset_member(zset_name, url)
        return result

    # 记录HTML下载成功次数(包含反爬页面代码的次数)
    def record_html_ok_times(self):
        zset_name = 'htmlTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取HTML下载成功次数(包含反爬页面代码的次数)
    def get_html_ok_times(self):
        zset_name = 'htmlTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出HTML下载成功次数
    def pop_html_ok_times(self):
        zset_name = 'htmlTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result


# Data队列
class DataQueue(BaseQueue):
    def __init__(self, RedisQ, log):
        super().__init__(RedisQ, log)
    
    def get_new_goods_data(self, timeout=10):
        datas = {}
        queue_name = 'goodsData'
        data_tuple = self._get_member_from_queue(queue_name, timeout=timeout)
        if type(data_tuple) is tuple and len(data_tuple) == 2:
            datas = pickle.loads(data_tuple[1])
        return datas

    # 写入goods_data队列
    def add_goods_data_to_queue(self, datas_betys):
        queue_name = 'goodsData'
        result = self._add_member_to_queue(queue_name, datas_betys)
        return result
    
    def get_new_bsrData(self, timeout=10):
        datas = {}
        queue_name = 'bsrData'
        data_tuple = self._get_member_from_queue(queue_name, timeout=timeout)
        if type(data_tuple) is tuple and len(data_tuple) == 2:
            datas = pickle.loads(data_tuple[1])
        return datas

    # 写入bsrData队列
    def add_bsrData_to_queue(self, datas_betys):
        queue_name = 'bsrData'
        result = self._add_member_to_queue(queue_name, datas_betys)
        return result

    # 获得 reviewsData
    def get_new_reviewsData(self, timeout=10):
        datas = {}
        queue_name = 'reviewsData'
        data_tuple = self._get_member_from_queue(queue_name, timeout=timeout)
        if type(data_tuple) is tuple and len(data_tuple) == 2:
            datas = pickle.loads(data_tuple[1])
        return datas

    # 写入reviews_data队列
    def add_reviews_to_queue(self, datas_betys):
        queue_name = 'reviewsData'
        result = self._add_member_to_queue(queue_name, datas_betys)
        return result

    # 记录已完成评论第一次下载的商品
    def the_reviews_first_download(self, md5key):
        set_name = 'reviewsFirst'
        result = self._add_member_to_set(set_name, md5key)
        return result

    # 查询是否是第一次下载
    def is_first_download(self, md5key):
        set_name = 'reviewsFirst'
        result = self._the_member_is_exist_in_set(set_name, md5key)
        if result:
            # 如果存在第一次已经下载集合中, 则说明不是第一次下载了.
            return False
        else:
            return True

    # 获得 tosellData 队列
    def get_new_tosellData(self, timeout=10):
        datas = {}
        queue_name = 'tosellData'
        data_tuple = self._get_member_from_queue(queue_name, timeout=timeout)
        if type(data_tuple) is tuple and len(data_tuple) == 2:
            datas = pickle.loads(data_tuple[1])
        return datas

    # 写入tosell_data队列
    def add_tosell_to_queue(self, datas_betys):
        queue_name = 'tosellData'
        result = self._add_member_to_queue(queue_name, datas_betys)
        return result

    # 获得 keywordData 队列
    def get_new_keywordData(self, timeout=10):
        datas = {}
        queue_name = 'keywordData'
        data_tuple = self._get_member_from_queue(queue_name, timeout=timeout)
        if type(data_tuple) is tuple and len(data_tuple) == 2:
            datas = pickle.loads(data_tuple[1])
        return datas

    # 写入keyword_data队列
    def add_keyword_to_queue(self, datas_betys):
        queue_name = 'keywordData'
        result = self._add_member_to_queue(queue_name, datas_betys)
        return result

    # 记录data解析成功次数(不含遇到反爬页面的次数)
    def record_data_ok_times(self):
        zset_name = 'dataTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取data解析成功次数(不含反爬页面代码的次数)
    def get_data_ok_times(self):
        zset_name = 'dataTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出data解析成功次数
    def pop_data_ok_times(self):
        zset_name = 'dataTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录入库成功次数
    def record_db_ok_times(self):
        zset_name = 'dbTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取入库成功次数
    def get_db_ok_times(self):
        zset_name = 'dbTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出入库成功次数
    def pop_db_ok_times(self):
        zset_name = 'dbTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录入库总次数
    def record_dbSum_times(self):
        zset_name = 'dbSumTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取入库总次数
    def get_dbSum_times(self):
        zset_name = 'dbSumTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出入库总次数
    def pop_dbSum_times(self):
        zset_name = 'dbSumTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录keyword解析成功次数(不含遇到反爬页面的次数)
    def record_keyword_ok_times(self):
        zset_name = 'keywordTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取keyword解析成功次数(不含反爬页面代码的次数)
    def get_keyword_ok_times(self):
        zset_name = 'keywordTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出keyword解析成功次数
    def pop_keyword_ok_times(self):
        zset_name = 'keywordTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录keyword不存在次数(不含遇到反爬页面的次数)
    def record_keyword_not_fund_times(self):
        zset_name = 'keywordNotFundTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取keyword不存在次数(不含反爬页面代码的次数)
    def get_keyword_not_fund_times(self):
        zset_name = 'keywordNotFundTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出keyword不存在次数
    def pop_keyword_not_fund_times(self):
        zset_name = 'keywordNotFundTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录tosell成功次数(不含遇到反爬页面的次数)
    def record_tosell_ok_times(self):
        zset_name = 'tosellTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取tosell成功次数(不含反爬页面代码的次数)
    def get_tosell_ok_times(self):
        zset_name = 'tosellTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出tosell成功次数
    def pop_tosell_ok_times(self):
        zset_name = 'tosellTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录reviews成功次数(不含遇到反爬页面的次数)
    def record_reviews_ok_times(self):
        zset_name = 'reviewsTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取reviews成功次数(不含反爬页面代码的次数)
    def get_reviews_ok_times(self):
        zset_name = 'reviewsTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出reviews成功次数
    def pop_reviews_ok_times(self):
        zset_name = 'reviewsTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录商品解析成功次数
    def record_goods_ok_times(self):
        zset_name = 'goodsTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取商品解析成功次数
    def get_goods_ok_times(self):
        zset_name = 'goodsTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出商品解析成功次数
    def pop_goods_ok_times(self):
        zset_name = 'goodsTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result


# Url队列
class UrlQueue(BaseUrlQueue):
    def __init__(self, RedisQ, log):
        super().__init__(RedisQ, log)

    # 从数据库取asin
    @staticmethod
    def retrieve_asin(sql='', data=None):
        # asin_list = ASINS
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        if sql and not data:
            cur.execute(sql)
        elif sql and data:
            cur.execute(sql, data)
        else:
            # cur.execute("select asin, monitor_type, aid from public.amazon_product_monitor where aid='3';")
            # cur.execute("select asin, monitor_type, aid from public.amazon_product_monitor where state > 0 or monitor_type > 0 order by aid asc limit 100;")
            cur.execute("select asin, monitor_type, aid from public.amazon_product_monitor where state > 0 or monitor_type > 0 order by info_tm_crawler;")

        # 是个元组列表， 元组中是查询的元素， 如果无，则返回空列表。
        asin_rows = cur.fetchall()
        # print(asin_rows)
        conn.commit()
        cur.close()
        conn.close()
        #asin_rows = ASINS
        return asin_rows

    # 从数据库取库存下载失败的asin
    @staticmethod
    def retrieve_qty_asin():
        # asin_list = ASINS
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        cur.execute("select asin, monitor_type, aid  from public.amazon_product_data where quantity < 0 and asin_state=1;")
        # 是个元组列表， 元组中是查询的元素， 如果无，则返回空列表。
        asin_rows = cur.fetchall()
        # print(asin_rows)
        conn.commit()
        cur.close()
        conn.close()
        return asin_rows

    # 获取URLstring
    def get_new_asin_url_from_set(self, poptype=''):
        result = {}
        url_bytes = ''
        # try:
        if poptype == 'goods':
            url_bytes = self.pop_goods_url_from_set()
        if poptype == 'tosell':
            url_bytes = self.pop_tosell_url_from_queue()
        if poptype == 'reviews':
            url_bytes = self.pop_reviews_url_from_queue()
        if url_bytes:
            print('get_url %s' % (poptype), url_bytes, type(url_bytes))
            try:
                urls_dict = pickle.loads(url_bytes)
                if type(urls_dict) is dict:
                    result = urls_dict
            except Exception as e:
                self.log.error('get_new_asin_url_from_set get %s 时 [%s]' % (poptype, e))
        return result

    # 存合成url要用到的title
    def add_urlTitle_to_string(self, asin, url_title):
        key_type = 'urlTitle'
        overtime = 3 * 86400
        result = self._set_key_value_to_string(asin, url_title, key_type, overtime=overtime)
        return result

    # 取url要用到的title
    def get_urlTitle_from_string(self, asin):
        key_type = 'urlTitle'
        result = ''
        result0 = self._get_value_from_string(asin, key_type)
        if result0:
            result1 = str(result0, encoding='utf-8')
            if len(result1) <= 72:
                result = result1
        return result

    # 增加到商品URL队列
    def add_goods_url_to_queue(self, url, qType=''):
        set_name = 'goodsUrlQueue'
        if qType == 'monitor':
            set_name = 'monitorGoods'
        result = self._add_member_to_queue(set_name, url)
        return result

    # 从商品URL集合弹出bytes
    def pop_goods_url_from_set(self):
        set_name = 'goodsUrlQueue'
        timeout = 10
        monitor_name = 'monitorGoods'
        if self._get_queue_len(monitor_name) > 0:
            result = self._get_member_from_queue(monitor_name, timeout)
        else:
            result = self._get_member_from_queue(set_name, timeout)
        if result:
            result = result[1]
        return result

    # 读取商品url队列长度
    def retrieve_goodsUrl_len(self):
        set_name = 'goodsUrlQueue'
        result = self._get_queue_len(set_name)
        return result

    # 读取跟卖url队列长度
    def retrieve_tosellUrl_len(self):
        set_name = 'tosellUrlQueue'
        result = self._get_queue_len(set_name)
        return result

    # 读取评论url队列长度
    def retrieve_reviewsUrl_len(self):
        set_name = 'reviewsUrlQueue'
        result = self._get_queue_len(set_name)
        return result

    # 插队加入goodsUrl队列
    def jump_queue_to_goods(self, url):
        set_name = 'goodsUrlQueue'
        result = self._rpushx_member_to_queue(set_name, url)
        return result

    # 增加到tosellURL集合
    def add_tosell_url_to_queue(self, url, qType=''):
        set_name = 'tosellUrlQueue'
        if qType == 'monitor':
            set_name = 'monitorTosell'
        result = self._add_member_to_queue(set_name, url)
        return result

    # 从tosellURL队列弹出
    def pop_tosell_url_from_queue(self):
        set_name = 'tosellUrlQueue'
        timeout = 10
        monitor_name = 'monitorTosell'
        if self._get_queue_len(monitor_name) > 0:
            result = self._get_member_from_queue(monitor_name, timeout)
        else:
            result = self._get_member_from_queue(set_name, timeout)
        if result:
            result = result[1]
        return result

    # 插队加入reviewsUrl队列
    def jump_queue_to_tosell(self, url):
        set_name = 'tosellUrlQueue'
        result = self._rpushx_member_to_queue(set_name, url)
        return result

    # 增加到reviewsURL队列
    def add_reviews_url_to_queue(self, url, qType=''):
        set_name = 'reviewsUrlQueue'
        if qType == 'monitor':
            set_name = 'monitorReviews'
        result = self._add_member_to_queue(set_name, url)
        return result

    # 从reviewsURL队列弹出
    def pop_reviews_url_from_queue(self):
        set_name = 'reviewsUrlQueue'
        timeout = 10
        monitor_name = 'monitorReviews'
        if self._get_queue_len(monitor_name) > 0:
            result = self._get_member_from_queue(monitor_name, timeout)
        else:
            result = self._get_member_from_queue(set_name, timeout)
        if result:
            result = result[1]
        return result

    # 插队加入reviewsUrl队列
    def jump_queue_to_reviews(self, url):
        set_name = 'reviewsUrlQueue'
        result = self._rpushx_member_to_queue(set_name, url)
        return result

    # 记录keywordHTML下载成功次数(包含反爬页面代码的次数)
    def record_keywordHtml_ok_times(self):
        zset_name = 'keywordHtmlTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取keywordHTML下载成功次数(包含反爬页面代码的次数)
    def get_keywordHtml_ok_times(self):
        zset_name = 'keywordHtmlTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出keywordHTML下载成功次数
    def pop_keywordHtml_ok_times(self):
        zset_name = 'keywordHtmlTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录reviewsHTML下载成功次数(包含反爬页面代码的次数)
    def record_reviewsHtml_ok_times(self):
        zset_name = 'reviewsHtmlTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取reviewsHTML下载成功次数(包含反爬页面代码的次数)
    def get_reviewsHtml_ok_times(self):
        zset_name = 'reviewsHtmlTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出reviewsHTML下载成功次数
    def pop_reviewsHtml_ok_times(self):
        zset_name = 'reviewsHtmlTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录tosellHTML下载成功次数(包含反爬页面代码的次数)
    def record_tosellHtml_ok_times(self):
        zset_name = 'tosellHtmlTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取tosellHTML下载成功次数(包含反爬页面代码的次数)
    def get_tosellHtml_ok_times(self):
        zset_name = 'tosellHtmlTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出tosellHTML下载成功次数
    def pop_tosellHtml_ok_times(self):
        zset_name = 'tosellHtmlTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录tosell notFound次数
    def record_tosell_notFound_times(self):
        zset_name = 'tosellnotFound'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取tosell notFound次数
    def get_tosell_notFound_times(self):
        zset_name = 'tosellnotFound'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出tosell notFound次数
    def pop_tosell_notFound_times(self):
        zset_name = 'tosellnotFound'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result

    # 记录goodsHTML下载成功次数(包含反爬页面代码的次数)
    def record_goodsHtml_ok_times(self):
        zset_name = 'goodsHtmlTimes'
        member = 'isOK'
        result = self._record_member_times(zset_name, member)
        return result

    # 获取goodsHTML下载成功次数(包含反爬页面代码的次数)
    def get_goodsHtml_ok_times(self):
        zset_name = 'goodsHtmlTimes'
        member = 'isOK'
        score = self._return_zscore(zset_name, member)
        return score

    # 弹出tosellHTML下载成功次数
    def pop_goodsHtml_ok_times(self):
        zset_name = 'goodsHtmlTimes'
        member = 'isOK'
        result = self._pop_zset_member(zset_name, member)
        return result


# Ip队列
class IpQueue(BaseQueue):
    def __init__(self, RedisQ, log):
        super().__init__(RedisQ, log)

    # 数据库读取IP
    @staticmethod
    def retrieve_ip():
        ip_list = IPPOND  # 从配置中读取IP
        # conn = psycopg2.connect(database='postgres', user='postgres', password='123456', host='192.168.0.149',
        #                         port='15432')
        # conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        # cur = conn.cursor()
        # cur.execute('select public.proxy_ip from config_proxy_ip;')
        # ip_rows = cur.fetchall()
        # # print(ip_list)
        # conn.commit()
        # cur.close()
        # conn.close()
        # ip_list = []
        # if type(ip_rows) is list:
        #     if len(ip_rows) > 0:
        #         for row in ip_rows:
        #             if type(row) is tuple:
        #                 if len(row) == 1:
        #                     ip_list.append(row[0])
        ip_list = set(ip_list)
        ip_list = list(ip_list)
        return ip_list

    # 获取新ip
    def get_new_ip_from_set(self):
        queue_name = 'validIpQueue'
        ip_str = ''
        timeout = 10
        try:
            ip = self._get_member_from_queue(queue_name, timeout)
            if len(ip) == 2:
                ip_str = str(ip[1], encoding='utf-8')
            return ip_str
        except Exception as e:
            self.log.error('[get一个[ip]时[%s]' % (e))
            return ip_str

    # 增加有效IP到队列
    def add_validIp_to_queue(self, ip):
        queue_name = 'validIpQueue'
        result = self._add_member_to_queue(queue_name, ip)
        return result

    # 获取有效IP队列长度
    def retrieve_validIp_len(self):
        set_name = 'validIpQueue'
        result = self._get_queue_len(set_name)
        return result

    # 增加正在使用集合
    def add_useIp_set(self, md5key):
        set_name = 'useIpSet'
        result = self._add_member_to_set(set_name, md5key)
        return result

    # 从正在使用集合删除ip
    def srem_useIp_from_set(self, md5key):
        set_name = 'useIpSet'
        result = self._srem_member_from_set(set_name, md5key)
        return result

    # 判断ip是否正在使用(加锁)
    def is_useIp(self, md5key):
        set_name = 'useIpSet'
        result = self._the_member_is_exist_in_set(set_name, md5key)
        return result

    # 从正在使用集合弹出IP
    def pop_useIp_from_set(self):
        set_name = 'useIpSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 读取正在使用ip集合
    def retrieve_useIp_from_set(self):
        set_name = 'useIpSet'
        result = self._return_member_from_set(set_name)
        return result

    # 增加失效IP到集合
    def add_disabled_set(self, ip):
        set_name = 'disabledIpSet'
        result = self._add_member_to_set(set_name, ip)
        return result

    # 从失效集合弹出IP
    def pop_disabled_from_set(self):
        set_name = 'disabledIpSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 从集合读取失效IP
    def retrieve_disabled_from_set(self):
        set_name = 'disabledIpSet'
        result = self._return_member_from_set(set_name)
        return result

    # 是否失效
    def is_disable(self, ip):
        set_name = 'disabledIpSet'
        result = self._the_member_is_exist_in_set(set_name, ip)
        return result

    # 增加被反爬IP到休眠集合
    def add_sleepIp_to_set(self, ip):
        set_name = 'sleepIpSet'
        result = self._add_member_to_set(set_name, ip)
        return result

    # 从集合读取反爬IP
    def retrieve_sleepip_from_set(self):
        set_name = 'sleepIpSet'
        result = self._return_member_from_set(set_name)
        return result

    # 是否休眠
    def is_sleep(self, ip):
        set_name = 'sleepIpSet'
        result = self._the_member_is_exist_in_set(set_name, ip)
        return result

    # 从反爬集合弹出有效IP
    def pop_sleepip_from_set(self):
        set_name = 'sleepIpSet'
        result = self._pop_member_from_set(set_name)
        return result

    # 记录失效IP, 并统计失效次数
    def record_disabled_times(self, ip):
        zset_name = 'disabledIpTimes'
        record_result = self._record_member_times(zset_name, ip)
        return record_result

    # 读取失效 N 次的IP
    def return_disabled_IP(self, num=1, i=1, amount=100):
        '''默认返回失效1次以上的ip, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        zset_name = 'disabledIpTimes'
        use_list = self._return_member_list_form_zset(zset_name, num=num, i=i, amount=amount)
        return use_list

    # 弹出失效 N 次的IP
    def pop_disabled_IP(self, ip):
        '''默认返回1000次, 如果想返还其它次数,传入num, 或者传入i 返回1000的倍数'''
        zset_name = 'disabledIpTimes'
        pop_result = self._pop_zset_member(zset_name, ip)
        return pop_result

    # 记录被反爬次数
    def record_RobotCheck_times(self, ip):
        zset_name = 'RobotCheckIpTimes'
        record_result = self._record_member_times(zset_name, ip)
        return record_result

    # 返回被反爬 N 次的IP
    def return_RobotChek_IP(self, num=1, i=1, amount=100):
        '''默认返回被反爬1次以上的ip, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        zset_name = 'RobotCheckIpTimes'
        use_list = self._return_member_list_form_zset(zset_name, num=num, i=i, amount=amount)
        return use_list

    # 弹出被反爬 N 次的IP
    def pop_RobotChek_IP(self, ip):
        zset_name = 'RobotCheckIpTimes'
        pop_result = self._pop_zset_member(zset_name, ip)
        return pop_result

    # 记录IP使用次数
    def record_use_times(self, ip):
        zset_name = 'useIpTimes'
        record_result = self._record_member_times(zset_name, ip)
        return record_result

    # 返回使用 N 次的IP
    def return_use_times(self, num=1, i=1, amount=100):
        '''默认返回失效1次以上的ip, 如果想返还其它次数,传入num, 或者传入i 返回相应的倍数'''
        zset_name = 'useIpTimes'
        use_list = self._return_member_list_form_zset(zset_name, num=num, i=i, amount=amount)
        return use_list

    # 弹出使用 N 次的IP
    def pop_use_times(self, ip):
        '''默认返回1000次, 如果想返还其它次数,传入num, 或者传入i 返回1000的倍数'''
        zset_name = 'useIpTimes'
        pop_result = self._pop_zset_member(zset_name, ip)
        return pop_result

    # 返回ip使用总次数
    def return_use_score(self, ip):
        zset_name = 'useIpTimes'
        score = self._return_zscore(zset_name, ip)
        return score

    # 返回ip验证码次数
    def return_RobotChek_score(self, ip):
        zset_name = 'RobotCheckIpTimes'
        score = self._return_zscore(zset_name, ip)
        return score

    # 返回ip失效次数
    def return_disabled_score(self, ip):
        zset_name = 'disabledIpTimes'
        score = self._return_zscore(zset_name, ip)
        return score


# cookies队列
class CookQueue(BaseQueue):
    def __init__(self, RedisQ, log):
        super().__init__(RedisQ, log)

    # 取cookie
    def get_new_cookie_from_str(self, md5key):
        key_type = 'cookie'
        result = self._get_value_from_string(md5key, key_type)
        if result:
            result = pickle.loads(result)

        return result

    # 存cookie
    def add_cookie_to_str(self, md5key, cookiebytes, overtime=3600):
        key_type = 'cookie'
        result = self._set_key_value_to_string(md5key, cookiebytes, key_type, overtime)
        return result

    # 是否有效， 取cookie时先判断是否有效， 无效则不取
    def is_active(self, md5key):
        set_name = 'cookieSet'
        result = self._the_member_is_exist_in_set(set_name, md5key)
        return result

    # 增加到有效cookie集合
    def add_cookie_to_set(self, md5key):
        set_name = 'cookieSet'
        result = self._add_member_to_set(set_name, md5key)
        return result

    # 从cookie集合删除bytes
    def srem_cookie_from_set(self, md5key):
        set_name = 'cookieSet'
        result = self._srem_member_from_set(set_name, md5key)
        return result

    # 读取cookie集合
    def return_cookieSet(self):
        set_name = 'cookieSet'
        result = self._return_member_from_set(set_name)
        return result


class KeyWordQueue(BaseUrlQueue):
    def __init__(self, RedisQ, log):
        super().__init__(RedisQ, log)

    @staticmethod
    def retrieve_keyword(sql=''):
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        if sql:
            cur.execute(sql)
        else:
            # cur.execute("select kw, cid, aid from public.amazon_keyword_monitor where aid='3';")
            # cur.execute("select kw, cid, aid from public.amazon_keyword_monitor where state > 0 limit 100;")
            cur.execute("select kw, cid, aid from public.amazon_keyword_monitor where state > 0 order by aid desc;")

        keyword_rows = cur.fetchall()
        # print(keyword_rows)
        conn.commit()
        cur.close()
        conn.close()
        #keyword_rows = []
        return keyword_rows

    def add_keyword_to_queue(self, keyword_bytes, qType=''):
        set_name = 'KeywordQueue'
        if qType == 'monitor':
            set_name = 'monitorKeyword'
        result = self._add_member_to_queue(set_name, keyword_bytes)
        return result

    def pop_keyword_from_queue(self):
        set_name = 'KeywordQueue'
        timeout = 10
        monitor_name = 'monitorKeyword'
        if self._get_queue_len(monitor_name) > 0:
            result = self._get_member_from_queue(monitor_name, timeout)
        else:
            result = self._get_member_from_queue(set_name, timeout)
        if result:
            result = result[1]
        return result

    def get_new_keyword(self):
        result = {}
        try:
            kw_bytes = self.pop_keyword_from_queue()
            # print(1, kw_bytes, type(kw_bytes))
            # time.sleep(1)
            if kw_bytes:
                kw_dict = pickle.loads(kw_bytes)
                # print(2,kw_dict, type(kw_dict))
                if type(kw_dict) is dict:
                    result = kw_dict
        except Exception as e:
            self.log.error('[get一个[Keyword]时[%s]' % (e))
        # print(3, result, type(result))
        # time.sleep(10)
        return result

    # 读取keyword队列长度
    def return_keyword_len(self):
        set_name = 'KeywordQueue'
        result = self._get_queue_len(set_name)
        return result

    # 插队加入keyword队列
    def jump_queue_to_keyword(self, url):
        set_name = 'KeywordQueue'
        result = self._rpushx_member_to_queue(set_name, url)
        return result


class UaPond:
    ua = UAPOND

    @classmethod
    def get_new_ua(cls):
        result = choice(cls.ua)
        print(1, result)
        location = os.path.join(os.path.join(BASE_DIR, 'conf'), 'UAPOND.json')
        print(location)
        try:
            UA = UserAgent(use_cache_server=False, path=location)
            the_ua = UA.random
        except Exception as e:
            print('get_new_ua error [%s]' % (e))
            the_ua = ''
        if the_ua:
            result = the_ua
        print(2, result)
        return result


class Sleep:
    @staticmethod
    def random_sleep():
        sleep = random() + random()
        return sleep

    @staticmethod
    def randint_sleep(start, end):
        sleep = randint(start, end) + random()
        return sleep

    @classmethod
    def get_sleep(cls, ipQ):
        sleepTime = 0
        sleepTimes = ipQ._get_value_from_string('sleepTimes', '休眠时间')
        if sleepTimes:
            sleepTimes = str(sleepTimes, encoding='utf-8')
            if sleepTimes.isdigit():
                sleepTime = int(sleepTimes)
        if sleepTime > 0:
            SLEEP = randint(sleepTime, sleepTime + 3) + random()
        else:
            SLEEP = randint(SLEEP1, SLEEP2) + random()
        print('SLEEP: ', SLEEP)
        sleep_time = SleepTime(ipQ).sleep_time(SLEEP) + SLEEP 
        return sleep_time


class Logger:

    def __init__(self, log_level='error', log_name='debug'):
        path = os.path.join(LOG_DIR, '%s_%s.csv' % (log_name, log_level))
        if BASE_TYPE == 'develop':
            if log_level == 'error':
                log_level = 'debug'
        if log_level == 'debug':
            formatter = LOG_TEM_DEBUG
            clevel = logging.DEBUG
            flevel = logging.INFO
        if log_level == 'error':
            formatter = LOG_TEM_ERROR
            clevel = logging.INFO
            flevel = logging.WARNING
        if log_level == 'info':
            formatter = LOG_TEM_INFO
            clevel = logging.INFO
            flevel = logging.INFO
        if log_level == 'DB':
            formatter = LOG_TEM_DB
            clevel = logging.DEBUG
            flevel = logging.INFO

        # 初始化日志
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(*formatter)

        # 设置sheel日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        maxBytes = 50 * 1024 * 1024     # 50M
        # 设置file日志
        fh = ConcurrentRotatingFileHandler(path, mode='a', maxBytes=maxBytes, backupCount=10,encoding='utf-8')
        fh.setFormatter(fmt)
        fh.setLevel(flevel)

        # 注册日志
        if not self.logger.handlers:
            self.logger.addHandler(sh)
            self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def war(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)


def return_PST():
    # 设置为洛杉矶时区
    time_zone = pytz.timezone('America/Los_Angeles')
    dateNow = datetime.now(time_zone)
    return dateNow


# 夜间动态调整访问间隔
class SleepTime:
    def __init__(self, ipQ):
        self.ipQ = ipQ
        self.nowhour = return_PST().hour
        # 已废弃
        # sleepSet = ipQ.retrieve_sleepip_from_set()
        # self.sleepNume = len(sleepSet)
        # disabledSet = ipQ.retrieve_disabled_from_set()
        # self.disabledNum = len(disabledSet)

    def sleep_time(self, SLEEP):
        sleep_times = 0
        print('self.nowhour', self.nowhour)
        if 9 >= self.nowhour >= 21:
            sleep_times = 1
        print('sleep_times0', sleep_times)
        if 0 <= self.nowhour <= 3:
            sleep_times = sleep_times + 2
        if 4 <= self.nowhour <= 9:
            sleep_times = sleep_times + 5
        print('sleep_times1', sleep_times)
        # 已废弃
        # print('self.sleepNume', self.sleepNume)
        # if 10 >= self.sleepNume >= 5:
        #     sleep_times = sleep_times + 1
        # if 20 >= self.sleepNume > 10:
        #     sleep_times = sleep_times + 1
        # print('sleep_times2', sleep_times)
        # if self.sleepNume > 20:
        #     sleep_times = sleep_times + 3
        # print('sleep_times3', sleep_times)
        # if 10 >= self.disabledNum >= 5:
        #     sleep_times = sleep_times + 1
        # if 20 >= self.disabledNum > 10:
        #     sleep_times = sleep_times + 1
        # print('sleep_times4', sleep_times)
        # print('disabledNum', type(self.disabledNum), self.disabledNum)
        # if self.disabledNum > 20:
        #     sleep_times = sleep_times + 3
        # print('sleep_times5', sleep_times)
        return sleep_times


if __name__ == '__main__':
    # ip = IpQueue()
    # for i in range(10):
    #     ip.add_valid_ip('127.0.0.%s' % (i))
    # ipstr = ip.get_new_ip()
    # print(ipstr, type(ipstr))

    logyyx1 = Logger('debug')
    # logyyx = Logger('info')
    # logyyx2 = Logger('info')
    # # logyyx = Logger('error')
    # logyyx.debug('一个debug信息')
    logyyx1.debug('一个debug信息')
    # logyyx2.debug('一个debug信息')
    # logyyx.info('一个info信息')
    # logyyx1.info('一个info信息')
    # logyyx2.info('一个info信息')
    # logyyx.war('一个warning信息')
    # logyyx1.war('一个warning信息')
    # logyyx2.war('一个warning信息')
    # logyyx.error('一个error信息')
    # logyyx1.error('一个error信息')
    # logyyx2.error('一个error信息')
    # logyyx.cri('一个致命critical信息')
    # logyyx1.cri('一个致命critical信息')
    # logyyx2.cri('一个致命critical信息')
    # r = GetRedis().return_redis(logyyx1, 'develop')
    # i = r.set('1', 12345)
    # e = r.get('1')
    # print(type(r), i, e, id(r))
    # print(UaPond.get_new_ua())
    print(return_PST().strftime('%Y-%m-%d %H:%M:%S'))
    print(BASE_DIR)
    print(UaPond.get_new_ua())



    # list0 = IpQueue.retrieve_ip()
    # print(list0)
    # print(len(list0))
    # list1 = UrlQueue.retrieve_asin()
    # print(len(list1))

    # ip.record_disabled_times('127.0.0.1')
    # ip.record_use_times('127.0.0.1')
    # print(ip.return_disabled_IP(num=1))
