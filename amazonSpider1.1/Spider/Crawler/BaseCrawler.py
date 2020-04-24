#!/usr/bin/env python3
# -*- coding: utf-8-*-
import sys
sys.path.append("../")
import os
import re
import time
import pickle
import hashlib
from random import choice
from threading import Thread
from datetime import datetime
from random import randint

from Crawler.Downloader import get_html_useRequest
from Crawler.goodsParser import GoodsParser
from Crawler.reviewsParser import ReviewsParser
from Crawler.tosellParser import TosellParser
from Crawler.DataOutput import DataOutput

from utils.util import UaPond
from utils.util import return_PST
from conf.setting import DATA_DIR


class BaseCrawler:

    def __init__(self, urlQ, ipQ, dataQ, cookiesQ, kwQ, info_log, debug_log):
        self.urlQ = urlQ
        self.ipQ = ipQ
        self.kwQ = kwQ
        self.dataQ = dataQ
        self.cookiesQ = cookiesQ
        self.info_log = info_log
        self.debug_log = debug_log
        self.url_type = ''

    # 计算时间间隔的函数
    @staticmethod
    def get_the_time():
        # 日期格式
        date_str = '%Y%m%d'
        # 时间格式
        time_str = '%Y%m%d%H%M%S'

        # 当天的日期对象
        the_day = datetime.now()
        the_hour = the_day.hour
        pstNow = return_PST()
        pstHour = pstNow.hour
        # print(1.1, the_day)
        # 当天日期字符串
        date_str = the_day.strftime(date_str)
        # 当天15点整字符串
        the_day_str = '%s150000' % (date_str)
        # 当天15点的时间对象
        time_day = time.strptime(the_day_str, time_str)
        # print(1, time_day)

        the_time = time.mktime(time_day)
        # 当天15点时间戳
        the_date_time = the_time
        # 昨天15点时间戳
        old_date_time = the_date_time - 86400

        # 如果过了太平洋时间0点了, 需要另外计算.
        if 10 >= pstHour >= 0 and 15 <= the_hour <= 23:
            the_date_time = the_time + 86400
            old_date_time = the_time

        return the_date_time, old_date_time

    # 根据关键字和搜索类型，获取搜索url
    def make_search_url(self, kw, cid):
        search_url = GoodsParser.make_search_url(kw, cid)
        return search_url

    def add_sleep_url(self, url_dict, url_type='goods', retry_type=False):
        print('休眠后再将url加回队列')
        time.sleep(5)
        self.add_url_to_queue(url_dict, url_type, retry_type=retry_type)

    # 从redis队列读取关键字以及搜索类型
    def get_keyword(self, retry=10):
        if retry < 1:
            return '', {}
        url_type = 'keyword'
        kw_dict = self.kwQ.get_new_keyword()
        print('get_keyword.kw_dict: ', kw_dict, type(kw_dict))
        # time.sleep(30)
        if not kw_dict:
            return '', {}
        kw = kw_dict.get('kw') or ''
        if not kw:
            return self.get_keyword(retry=retry-1)
        r = re.compile('[\u4e00-\u9fa5]+')
        k = r.search(kw)
        if k:
            return self.get_keyword(retry=retry-1)
        overtime = 60
        new_url_set_name = 'NewUrl'
        url_md5key = kw_dict.get('md5') or ''
        if not url_md5key:
            url_md5key = self.get_md5_key(kw + url_type)
        is_new_url = self.urlQ._the_member_is_exist_in_set(new_url_set_name, url_md5key)
        if is_new_url:
            overtime = 20
        used_md5key = kw_dict.get('umd5') or ''
        used = 'useInterval'
        if not used_md5key:
            used_md5key = self.get_md5_key(kw + url_type + used)
        is_used = self.kwQ._get_value_from_string(used_md5key, used)
        if not self.is_download(kw, url_type):
            if is_used and kw:
                print('url休眠中 %s %s' % (kw, url_type))
                self.add_sleep_url(kw_dict, url_type=url_type, retry_type=True)
                return self.get_keyword(retry=retry-1)
            else:
                # 如果没下载过
                # 设置一个时间间隔
                self.kwQ._set_key_value_to_string(used_md5key, used, used, overtime=overtime)
            return kw, kw_dict
        else:
            time.sleep(0.1)
            return self.get_keyword(retry=retry-1)

    # 获取asin以及监控类型
    def get_asin_monitor(self, url_type='', retry=10):
        '''url_type 不传则默认获取 总asin集合 传参, 只接受 'goods' 'reviews' 'tosell' 'keyword'四种参数'''
        if retry < 1:
            return '', {}
        if url_type == 'keyword':
            return self.get_keyword()
        url_dict = self.urlQ.get_new_asin_url_from_set(poptype=url_type)
        if not url_dict or type(url_dict) is not dict:
            return '', {}
        asin = url_dict.get('asin') or ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(asin)
        if not k:
            return self.get_asin_monitor(url_type, retry=retry - 1)
        overtime = 60
        new_url_set_name = 'NewUrl'
        url_md5key = url_dict.get('md5') or ''
        if not url_md5key:
            url_md5key = self.get_md5_key(asin + url_type)
        is_new_url = self.urlQ._the_member_is_exist_in_set(new_url_set_name, url_md5key)
        if is_new_url:
            overtime = 20
        used = 'useInterval'
        used_md5key = url_dict.get('umd5') or ''
        if not used_md5key:
            used_md5key = self.get_md5_key(asin + url_type + used)
        is_used = self.kwQ._get_value_from_string(used_md5key, used)
        if not self.is_download(asin_kw=asin, url_type=url_type, md5key=url_md5key):
            if is_used and asin:
                print('url休眠中 %s %s' % (asin, url_type))
                self.add_url_to_queue(url_dict, url_type=url_type, retry_type=True)
                time.sleep(0.1)
                return self.get_asin_monitor(url_type, retry=retry - 1)
            # 如果没下载
            print('没下载过', asin, url_dict)
            # 设置一个三分钟的时间间隔
            self.kwQ._set_key_value_to_string(used_md5key, used, used, overtime=overtime)
            return asin, url_dict

        else:
            print('已下载过', asin, url_dict)
            time.sleep(0.1)
            return self.get_asin_monitor(url_type, retry=retry - 1)

    # 根据asin生成url
    @staticmethod
    def make_url(asin, url_type='goods', urltitle='', sessionId=''):
        url_tuple = tuple()
        if url_type == 'goods':
            url, referer = GoodsParser.make_goods_url(asin, urltitle=urltitle, sessionId=sessionId)
            url_tuple = (url, referer)
        if url_type == 'reviews':
            url = ReviewsParser.make_reviews_url(asin, urltitle=urltitle)
            url_tuple = (url,)
        if url_type == 'tosell':
            url = TosellParser.make_tosell_url(asin)
            url_tuple = (url,)
        return url_tuple

    # 将url写入redis集合
    def add_url_to_queue(self, url_dict, url_type='goods', retry_type=False):
        '''url_dict需要一个字典'''

        result = False
        if not url_dict or type(url_dict) is not dict:
            return result
        md5key = url_dict.get('md5') or ''
        new_url_set_name = 'NewUrl'
        qType = 'monitor'
        print('add_url_to_set.url_dict: ', url_dict, type(url_dict))
        if not md5key:
            asin = url_dict.get('asin')
            kw = url_dict.get('kw')
            md5value = ''
            if asin:
                md5value = asin + url_type
            if kw:
                md5value = kw + url_type
            if md5value:
                md5key = self.get_md5_key(md5value)
        is_new_url = self.urlQ._the_member_is_exist_in_set(new_url_set_name, md5key)
        url_bytes = pickle.dumps(url_dict)
        url_mtm = url_dict.get('mtm') or 0
        the_date_time, old_date_time = self.get_the_time()
        # print('add_url_to_set, aid: ', aid, type(aid))
        if not self.is_download(md5key):
            if url_type == 'goods':
                # 如果时间戳是今天之内, 则加入新url队列
                if old_date_time < url_mtm or is_new_url:
                    urllen = self.urlQ._get_queue_len('monitorGoods')
                    url_index = randint(int(urllen*0.3), int(urllen*0.7))
                    # 如果队列大于10, 且时重试的url, 随机插入队列中间
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('monitorGoods', url_index, url_bytes)
                    else:
                        self.urlQ.add_goods_url_to_queue(url_bytes, qType)
                else:
                    urllen = self.urlQ.retrieve_goodsUrl_len()
                    url_index = randint(int(urllen*0.3), int(urllen*0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('goodsUrlQueue', url_index, url_bytes)
                    else:
                        result = self.urlQ.add_goods_url_to_queue(url_bytes)
            if url_type == 'reviews':
                if old_date_time < url_mtm or is_new_url:
                    urllen = self.urlQ._get_queue_len('monitorReviews')
                    url_index = randint(int(urllen*0.3), int(urllen*0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('monitorReviews', url_index, url_bytes)
                    else:
                        result = self.urlQ.add_reviews_url_to_queue(url_bytes, qType)
                else:
                    urllen = self.urlQ.retrieve_reviewsUrl_len()
                    url_index = randint(int(urllen * 0.3), int(urllen * 0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('reviewsUrlQueue', url_index, url_bytes)
                    else:
                        result = self.urlQ.add_reviews_url_to_queue(url_bytes)
            if url_type == 'tosell':
                if old_date_time < url_mtm or is_new_url:
                    urllen = self.urlQ._get_queue_len('monitorTosell')
                    url_index = randint(int(urllen * 0.3), int(urllen * 0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('monitorTosell', url_index, url_bytes)
                    else:
                        result = self.urlQ.add_tosell_url_to_queue(url_bytes, qType)
                else:
                    urllen = self.urlQ.retrieve_tosellUrl_len()
                    url_index = randint(int(urllen * 0.3), int(urllen * 0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('tosellUrlQueue', url_index, url_bytes)
                    else:
                        result = self.urlQ.add_tosell_url_to_queue(url_bytes)
            if url_type == 'keyword':
                if old_date_time < url_mtm or is_new_url:
                    urllen = self.urlQ._get_queue_len('monitorKeyword')
                    url_index = randint(int(urllen * 0.3), int(urllen * 0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('monitorKeyword', url_index, url_bytes)
                    else:
                        result = self.kwQ.add_keyword_to_queue(url_bytes, qType)
                else:
                    urllen = self.kwQ.return_keyword_len()
                    url_index = randint(int(urllen * 0.3), int(urllen * 0.7))
                    if urllen > 10 and retry_type:
                        self.urlQ.RedisQ.lset('KeywordQueue', url_index, url_bytes)
                    else:
                        result = self.kwQ.add_keyword_to_queue(url_bytes)
        #time.sleep(5)
        return result

    # 判断ip是否在休眠
    def the_ip_has_sleep(self, ip):
        result = False
        ipSleep = self.ipQ._get_value_from_string(ip, 'sellpIp')
        if ipSleep:
            ipSleep = str(ipSleep, encoding='utf-8')
            if 'sleep' in ipSleep:
                return True
        return result

    def add_sleep_ip(self, ip):
        print('ip%s休眠中, 延迟10秒再将ip加回队列' % (ip))
        time.sleep(10)
        self.the_ip_is_sleepy(ip)

    # 获取有效ip
    def get_ip(self, ip_type='valid', retry=10):
        result = ''
        if retry < 1:
            return result
        if ip_type == 'valid':
            result = self.ipQ.get_new_ip_from_set()
            if result:
                print(1, result, 'valid ip\n')
                if ':' in result:
                    result = result.split(':')[0] + ':' + choice(['8800', '3128'])
                print(2, result, 'valid ip\n')
                # 如果失效了, 马上换一个
                if self.ipQ.is_disable(result):
                    print('ip %s 失效, 换一个\n' % (result))
                    time.sleep(0.1)
                    return self.get_ip(ip_type=ip_type, retry=retry-1)
                # 如果在休眠, 则开一条线程重新加回队列, 并换一个ip返回
                if self.the_ip_has_sleep(result):
                    print('ip %s 休眠, 换一个\n' % (result))
                    self.the_ip_is_sleepy(result)
                    return self.get_ip(ip_type=ip_type, retry=retry-1)
                ip_locak = result.split(':')
                if type(ip_locak) is list:
                    ip_locak = ip_locak[0]
                else:
                    ip_locak = result
                print('get_ip.ip_locak', ip_locak)
                # ip上锁
                the_lock = self.add_useIp_set(ip_locak)
                # 上锁失败换一个
                if not the_lock:
                    print('ip %s 正在被使用, 换一个\n' % (result))
                    self.the_ip_is_sleepy(result)
                    time.sleep(0.1)
                    return self.get_ip(ip_type=ip_type, retry=retry-1)
        return result

    # 将ip写入队列
    def add_ip_to_queue(self, ip, ip_type='valid'):
        '''ip_type 只接收三种参数 'valid' 'disabled' 'sleep' '''
        result = False
        print('add_ip_to_queue: ', ip, ip_type)
        if ip_type == 'valid':
            result = self.ipQ.add_validIp_to_queue(ip)
        if ip_type == 'disabled':
            # 加入失效集合(要更换的ip)
            result = self.ipQ.add_disabled_set(ip)
        if ip_type == 'sleep':
            # 加入休眠集合(暂时废弃)
            result = self.ipQ.add_sleepIp_to_set(ip)
        return result

    # 计算成功率
    def calculation_rate(self,dividend, divisor):
        result = 0
        if divisor != 0:
            result = dividend / divisor * 100
        return result

    # 分析ip是否应该休眠
    def the_ip_is_sleepy(self, ip):
        # 查ip使用次数, 失败次数, 验证码次数
        ip_use_times = self.ipQ.return_use_score(ip)
        ip_RobotChek_times = self.ipQ.return_RobotChek_score(ip)
        ip_disabled_times = self.ipQ.return_disabled_score(ip)

        if ip_use_times > 100:
            # 算 ip 失败率
            disabled_rate = self.calculation_rate(ip_disabled_times, ip_use_times)
            # 失败率超过80%则表示ip废弃, 不可用(需要更换）
            if disabled_rate > 50:
                ip_type = 'disabled'
                return self.add_ip_to_queue(ip, ip_type)

        if ip_use_times > 100 and ip_use_times % 10 == 0:
            # 算 ip 验证码率
            robotChek_rate = self.calculation_rate(ip_RobotChek_times, ip_use_times)
            if robotChek_rate > 15:
                # 如果验证码率超过30%, 休眠
                ip_type = 'seleepIp'
                self.ipQ._set_key_value_to_string(ip, 'sleep', ip_type, 10)
            # 算 ip 失败率
            disabled_rate = self.calculation_rate(ip_disabled_times, ip_use_times)
            # 如果ip失败率超过50%, 则休眠
            if disabled_rate > 30:
                ip_type = 'seleepIp'
                self.ipQ._set_key_value_to_string(ip, 'sleep', ip_type, 30)
        if ip_use_times > 200 and ip_use_times % 20 == 0:
            time.sleep(5)

        # 将ip加回队列
        result = self.add_ip_to_queue(ip)

        return result

    # 以文件的形式保存被丢弃的url
    def save_discard_url(self, asin, url, num, discard_type):
        pstNow = return_PST()
        timeNow = pstNow.strftime("%Y-%m-%d %H:%M:%S")
        dateNow = pstNow.strftime("%Y_%m_%d")
        filepath = os.path.join(DATA_DIR, 'discard_url_%s.log' % (dateNow))
        msg = '[%s][%s][%s] [%s] [%s] [被放弃]\n' % (timeNow, asin, url, discard_type, num)
        msg.encode('utf-8')
        with open(filepath, 'a') as f:
            f.write(msg)

    # 分析url是否应该丢弃
    def the_url_is_discard(self, asin_or_kw, url_dict, url_type, url_md5key):
        result = False
        url_list = url_dict.get('durl') or []
        if not url_md5key:
            url_md5key = url_dict.get('md5') or ''
        if not asin_or_kw:
            asin_or_kw = url_dict.get('asin') or url_dict.get('kw') or ''
        print('the_url_is_discard.asin_or_kw: ', asin_or_kw)
        # 查url失败次数, 验证码次数
        disabled_num = 10
        if url_type != 'keyword':
            disabled_num = disabled_num + 5
        new_url_set_name = 'NewUrl'
        if not url_md5key:
            url_md5key = self.get_md5_key(asin_or_kw + url_type)
        is_new_url = self.urlQ._the_member_is_exist_in_set(new_url_set_name, url_md5key)
        if is_new_url:
            disabled_num = disabled_num + 5
        if disabled_num > 20:
            disabled_num = 20
        url_RobotChek_times = url_dict.get('rnum') or 0
        if not url_RobotChek_times:
            url_RobotChek_times = self.urlQ.get_RobotCheck_url_times(url_md5key)
        # url_disabled_times = url_dict.get('dnum') or 0
        # if not url_disabled_times:
        #     url_disabled_times = self.urlQ.get_defeated_url_times(url_md5key)
        zset_name = '%s%s' % (self.url_type, 'fail')
        url_disabled_times = self.urlQ._return_zscore(zset_name, asin_or_kw)
        self.urlQ._record_member_times(zset_name, asin_or_kw)
        print('url_RobotChek_times', url_RobotChek_times)
        print('url_disabled_times', url_disabled_times)
        if url_RobotChek_times >= 50:
            # 标记一个更新时间
            if url_type == 'goods':
                DataOutput.record_disabled_goods(asin_or_kw, 'discard')
            if url_type == 'tosell':
                DataOutput.record_disabled_tosell(asin_or_kw)
            if url_type == 'keyword':
                DataOutput.record_disabled_keyword(asin_or_kw)

            self.urlQ.pop_RobotCheck_url_times(url_md5key)
            # 加入下载失败集合
            self.urlQ.add_defeated_url_to_set(url_md5key)
            self.save_discard_url(asin_or_kw, url_list, url_RobotChek_times, '验证码次数过多')

        if url_disabled_times >= disabled_num:
            # 标记一个更新时间
            if url_type == 'goods':
                DataOutput.record_disabled_goods(asin_or_kw, 'discard')
            if url_type == 'tosell':
                DataOutput.record_disabled_tosell(asin_or_kw)
            if url_type == 'keyword':
                DataOutput.record_disabled_keyword(asin_or_kw)
            # 加入下载失败集合
            self.urlQ.add_defeated_url_to_set(url_md5key)
            self.urlQ.pop_defeated_url_times(url_md5key)
            self.save_discard_url(asin_or_kw, url_list, url_disabled_times, '连接失败')
        #else:
        #    result = self.add_url_to_queue(url_dict, url_type, retry_type=True)
        return result

    # 获取md5码
    @staticmethod
    def get_md5_key(value_str):
        '''value_str 必须是一个字符串, 只返回其中16位md5码, 节约内存'''
        return hashlib.md5(value_str.encode('utf-8')).hexdigest()[8: -8]

    # 获取UA
    def get_ua(self):
        return UaPond.get_new_ua()

    # 获取cookie
    def get_cookie(self, md5key):
        pass
        # cookie = self.cookiesQ.get_new_cookie_from_str(md5key)
        # return cookie

    # 存cookie
    def set_cookie(self, md5key, cookiesObj):
        pass
        # cookies_betys = pickle.dumps(cookiesObj)
        # return self.cookiesQ.add_cookie_to_str(md5key, cookies_betys)


    # 检查cookie是否有效
    def cookie_is_active(self, md5key):
        pass
        # return self.cookiesQ.is_active(md5key)

    # 删除无效cookie
    def delete_cookie(self, md5key):
        return self.cookiesQ.srem_cookie_from_set(md5key)

    # 判断是否验证码
    def is_RobotCheck(self, html):
        return GoodsParser.is_RobotCheck(html)

    def is_page_not_found(self, html):
        return GoodsParser.is_page_not_found(html)

    # 保存已下载的asin与关键字
    def save_success_asin_keyword(self, asin_kw='', url_type='', md5key=''):
        md5value = asin_kw + url_type
        md5key = self.get_md5_key(md5value)
        self.urlQ.add_success_asin_to_set(md5key)

    def is_download(self, asin_kw='', url_type='', md5key=''):
        if not md5key:
            md5value = 'none'
            print('is_download.asin_kw: ', asin_kw, type(asin_kw))
            if type(asin_kw) is str:
                md5value = asin_kw + url_type
            md5key = self.get_md5_key(md5value)
        return self.urlQ.is_downloaded(md5key)

    # 解析源码
    def parser(self, html, html_type='', asin='', ip='', url='',  ua='', info_log=None, debug_log=None, monitor_type=0, cookie=None, tosellSum=None, goods_html_code=None):
        '''只写了商品、评论、跟卖, 评论的html要求是一个html_list其余模块根据需要覆写此方法'''
        result = ()
        is_error = False
        if html_type == 'goods':
            try:
                goods_datas, bsr_data = GoodsParser().parser_goods(html, asin, monitor_type, ip=ip, ua=ua, debug_log=debug_log, download_url=url, cookies=cookie)
                result = (goods_datas, bsr_data)
            except Exception as e:
                is_error = True
                self.debug_log.error('[%s] goods parser解析 [%s] 时 [%s]' % (ip, url, e))
        if html_type == 'reviews':
            try:
                reviews_datas = ReviewsParser().reviews_parser(html, asin, ip=ip, download_url=url)
                result = (reviews_datas, )
            except Exception as e:
               is_error = True
               self.debug_log.error('[%s] reviews parser解析 [%s] 时 [%s]' % (ip, url, e))
        if html_type == 'tosell':
            try:
                tosell_info = TosellParser().tosell_parser(html, asin, tosellSum, ip=ip, download_url=url, goods_html_code=goods_html_code)
                result = (tosell_info, )
            except Exception as e:
               is_error = True
               self.debug_log.error('[%s] tosell parser解析 [%s] 时 [%s]' % (ip, url, e))
        return result, is_error

    # 下载html
    def get_html(self, url, ua, ip, cookie, referer, url_type='', asin=''):
        html = ''
        cookiesObj = {}
        html, cookiesObj, is_error = get_html_useRequest(url, ua, ip, cookie, self.debug_log, referer, self.ipQ, url_type=url_type, asin=asin)
        try:
            #html, cookiesObj, is_error = get_html_useRequest(url, ua, ip, cookie, self.debug_log, referer, self.ipQ, url_type=url_type, asin=asin)
            return html, cookiesObj, is_error
        except Exception as e:
            is_error = True
            self.debug_log.error('[%s] get_html 下载 [%s] 时 [%s]' % (ip, url, e))
            return html, cookiesObj, is_error

    # 记录日志
    def record_log(self, asin_keyword, time1, msgInt, msgType, startTime, ip, proxyInfo):
        '''msgInt 1成功 2失败 3报错 代表数据， 4失败 5验证码 6报错 7页面找不到 代表html'''
        time2 = time.time()
        endTime = return_PST().strftime("%Y-%m-%d %H:%M:%S")
        diffTime = time2 - time1
        self.info_log.info('%s, %s, %s, %s, %s, %s, %s, %s' %
                           (ip, asin_keyword, msgType, startTime, endTime, diffTime, msgInt, proxyInfo))

    # html分析
    def analyze_html(self, html, cookie, cookiesObj, ip, asin_or_kw, url_dict, cookie_md5key, time1, startTime, html_type=''):
        url_md5key = url_dict.get('md5')
        if not url_md5key:
            url_md5key = self.get_md5_key(asin_or_kw + html_type)
        if html and type(html) is str:
            self.urlQ.record_html_ok_times()
            if html_type == 'goods':
                self.urlQ.record_goodsHtml_ok_times()
            if html_type == 'keyword':
                self.urlQ.record_keywordHtml_ok_times()
            if html_type == 'reviews':
                self.urlQ.record_reviewsHtml_ok_times()
            if html_type == 'tosell':
                self.urlQ.record_tosellHtml_ok_times()

            if self.is_RobotCheck(html):
                rnum = url_dict.get('rnum') or 0
                url_dict['rnum'] = rnum + 1
                self.ipQ.record_RobotCheck_times(ip)
                self.ipQ._set_key_value_to_string(ip, 'sleep', 'sellpIp', 60)
                self.urlQ.record_RobotCheck_url_times(url_md5key)
                self.the_url_is_discard(asin_or_kw, url_dict, html_type, url_md5key)
                self.delete_cookie(cookie_md5key)
                msgInt = 5
                proxyInfo = 'get html RobotCheck'
                self.record_log(asin_or_kw, time1, msgInt, html_type, startTime, ip, proxyInfo)
                return False
            elif self.is_page_not_found(html):
                msgInt = 7
                proxyInfo = 'get html NotFound'
                self.record_log(asin_or_kw, time1, msgInt, html_type, startTime, ip, proxyInfo)
                self.save_success_asin_keyword(asin_or_kw, html_type)
                if not cookie:
                    if cookiesObj:
                        self.set_cookie(cookie_md5key, cookiesObj)
                return 404

            else:
                if not cookie:
                    if cookiesObj:
                        self.set_cookie(cookie_md5key, cookiesObj)
                return True
        else:
            self.the_url_is_discard(asin_or_kw, url_dict, html_type, url_md5key)
            self.ipQ.record_disabled_times(ip)
            self.delete_cookie(cookie_md5key)
            self.urlQ.record_defeated_url_times(url_md5key)
            msgInt = 4
            proxyInfo = 'get html defeated'
            self.record_log(asin_or_kw, time1, msgInt, html_type, startTime, ip, proxyInfo)
            return False

    # 将加入正在使用集合, 上锁
    def add_useIp_set(self, ip, retry=2):
        ipMd5 = self.get_md5_key(ip)
        result = self.ipQ.add_useIp_set(ipMd5)
        if result:
            print('ip %s 已上锁' % (ip))
        else:
            print('ip %s 上锁失败' % (ip))
            time.sleep(0.1)
            if retry > 0:
                return self.add_useIp_set(ip, retry=(retry - 1))
        return result

    # 将ip从正在使用集合删除, 解锁
    def srem_useIp_set(self, ip, retry=2):
        ipMd5 = self.get_md5_key(ip)

        result = self.ipQ.srem_useIp_from_set(ipMd5)
        if result:
            print('ip %s 已解锁锁' % (ip))
        else:
            print('ip %s 解锁失败' % (ip))
            if retry > 0:
                return self.add_useIp_set(ip, retry=(retry - 1))

    # 判断是否正在使用
    def is_useIp(self, ip):
        ipMd5 = self.get_md5_key(ip)
        self.ipQ.is_useIp(ipMd5)

    def url_len(self):
        urllen = 0.1
        if self.url_type == 'goods':
            urllen1 = self.urlQ.retrieve_goodsUrl_len()
            urllen2 = self.urlQ._get_queue_len('monitorGoods')
            urllen = urllen1 + urllen2
        if self.url_type == 'reviews':
            urllen1 = self.urlQ.retrieve_reviewsUrl_len()
            urllen2 = self.urlQ._get_queue_len('monitorReviews')
            urllen = urllen1 + urllen2
        if self.url_type == 'tosell':
            urllen1 = self.urlQ.retrieve_tosellUrl_len()
            urllen2 = self.urlQ._get_queue_len('monitorTosell')
            urllen = urllen1 + urllen2
        if self.url_type == 'keyword':
            urllen1 = self.kwQ.return_keyword_len()
            urllen2 = self.urlQ._get_queue_len('monitorKeyword')
            urllen = urllen1 + urllen2
        return urllen

    # 覆写下载方法
    def download(self, ip, asin_or_kw, url_dict):
        '''各模块覆写此方法'''
        pass

    # 判断是否已经使用过此ip
    def use_the_ip_download(self, asin_or_kw, retry=10):
        ip = self.get_ip()
        the_key = self.get_md5_key(ip + asin_or_kw + self.url_type)
        key_type = self.url_type + ' the download ip'
        result = self.urlQ._get_value_from_string(the_key, key_type)
        if result:
            ip_locak = ip.split(':')
            if type(ip_locak) is list:
                ip_locak = ip_locak[0]
            else:
                ip_locak = ip
            self.srem_useIp_set(ip_locak)
            # 将ip加回队列
            self.the_ip_is_sleepy(ip)
            # 如果连续10次都是用过的ip, 返回一个空字符串
            if retry < 1:
                return ''
            time.sleep(0.1)
            the_ip = self.use_the_ip_download(asin_or_kw, retry=retry-1)
        else:
            the_ip = ip
        return the_ip

    # 标记使用过的ip
    def the_ip_is_used(self, ip, asin_or_kw):
        the_key = self.get_md5_key(ip + asin_or_kw + self.url_type)
        key_type = self.url_type + ' the download ip'
        the_value = 'used'
        # 6小时内不能使用重复ip下载相同任务
        overtime = 3600 * 6
        return self.urlQ._set_key_value_to_string(the_key, the_value, key_type, overtime=overtime)


    def run(self):
        while True:
            urllen = self.url_len()
            if urllen < 1:
                sys.exit()
            print('%s队列长度: %s' % (self.url_type, urllen))
            asin_or_kw, url_dict = self.get_asin_monitor(self.url_type)
            asin_kw_verify = url_dict.get('asin') or url_dict.get('kw') or ''
            print('asin_or_kw: ', asin_or_kw, '\n', 'asin_kw_verify: ', asin_kw_verify)
            # 先拿到任务
            if asin_or_kw == asin_kw_verify and asin_or_kw:
                print(asin_or_kw)
                ip = ''
                self.download(ip, asin_or_kw, url_dict)






