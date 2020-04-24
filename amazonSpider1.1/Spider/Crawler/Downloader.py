#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
import time
import re
# import pickle
from random import randint
from urllib.parse import unquote
from urllib.parse import urlparse
from lxml import etree
import json
# import hashlib

import requests
from retrying import retry
# from selenium import webdriver

# 破解验证码
from captcha_crack import amazon_captcha_crack
from utils.util import UaPond
from utils.util import Sleep
from conf.setting import BASE_TYPE
from conf.setting import PROXY_HTTP, PROXY_HTTPS
from conf.setting import PROXY_VERIFY
from Crawler.BaseParser import BaseParser
from Crawler.DataOutput import DataOutput
# from Crawler.reviewsParser import ReviewsParser
from utils.decorator import timer


class BaseDownload:
    def __init__(self):
        pass


def is_RobotCheck(html_code):
    pattern = re.compile('Robot Check', re.S)
    RobotCheck = pattern.findall(html_code)
    if len(RobotCheck) > 0:
        return True
    return False

@timer
@retry(stop_max_attempt_number=15)
def get_html_useRequest(url, ua, ip, cookie, debug_log, referer, ipQ, urlQ=None, timeout=90, retry=1, goodsUrl='', url_type='', asin=''):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'close',
        'User-Agent': ua,
        'Host': 'www.amazon.com',
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    proxy = {'https': PROXY_HTTPS, 'http': PROXY_HTTP}
    print(proxy)
    html = ''
    cookies = {}
    status_code = 0
    session = requests
    print('\nheaders: ', headers)
    is_error = False
    if url.startswith('https://www.amazon.com') or url.startswith('http://www.amazon.com'):
        try:
            get_parmas = dict(url=url, headers=headers, proxies=proxy, timeout=timeout)
            if 'proxy.crawlera.com' in proxy.get('https', ''):
                get_parmas['verify'] = PROXY_VERIFY
            response = session.get(**get_parmas)
            status_code = response.status_code
            print('status_code', status_code)
            if status_code == 200 or status_code == 302 or status_code == 404:
                response.encoding = 'utf-8'
                responseCookies = response.cookies
                if not cookie:
                    cookies = responseCookies
                if status_code == 404:
                    if url_type == 'goods' and asin:
                        DataOutput.record_not_found_goods(asin)
                    if url_type == 'tosell' and asin:
                        DataOutput.record_not_found_tosell(asin)
                    html = response.text
                else:
                    html = response.text
                    if "Enter the characters you see below" in html:
                        raise Exception("Exception: Captcha")
                    if "Enter the characters you see below" in html:
                        raise Exception("Exception: block")
                if 'proxy.crawlera.com' not in proxy.get('https', ''):
                    time.sleep(3)
                return html, cookies, is_error
        except Exception as e:
            if status_code != 404:
                is_error = True
                debug_log.error('[%s] get_html_useRequest下载 [%s] 时 [%s]' % (ip, url, e))
                if "NotFound" in str(e):
                    raise Exception("NOT_FOUND")
    else:
        debug_log.error('[%s] get_html_useRequest下载 [%s] url不合法' % (ip, url))
    return html, cookies, is_error

"""
@retry(stop_max_attempt_number=10)
def psot_useRequest(url, post_data, ua, ip, cookie, debug_log, referer, ipQ=None, urlQ=None, timeout=10, retry=0):
    '''cookie不能为空'''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.5',
        'accept-encoding': 'gzip, deflate, br',
        'user-agent': ua,
        'host': 'www.amazon.com',
        'referer': referer,
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '%s' % (randint(510, 690)),
        'upgrade-insecure-requests': '1',
    }
    proxy = {'https': PROXY_HTTPS, 'http': PROXY_HTTP}
    is_error = False
    html = ''
    session = requests.Session()
    session.cookies = cookie
    if url.startswith('https://www.amazon.com') or url.startswith('http://www.amazon.com'):
        try:
            json_data = json.dumps(post_data)
            get_parmas = dict(url=url, headers=headers, proxies=proxy, data=post_data, json=json_data, timeout=60)
            if 'proxy.crawlera.com' in proxy.get('https', ''):
                get_parmas['verify'] = PROXY_VERIFY
            response = session.post(**get_parmas)
            status_code = response.status_code
            if status_code == 200 or status_code == 302:
                response.encoding = 'utf-8'
                html = response.text
                if "Enter the characters you see below" in html:
                    raise Exception("Exception: Captcha")
                if "Enter the characters you see below" in html:
                    raise Exception("Exception: block")
            return html, is_error
        except Exception as e:
            is_error = True
            debug_log.error('[%s] psot_useRequest 下载 [%s] 时 [%s]' % (ip, url, e))
            if "NotFound" in str(e):
                raise Exception("NOT_FOUND")
    else:
        debug_log.error('[%s] psot_useRequest下载 [%s] url不合法' % (ip, url))

    return html, is_error


def confirm_html(html_code, url, ua, ip, cookie, debug_log, referer, ipQ, retry=2):
    # 验证是否验证码
    result_html = html_code
    if is_RobotCheck(html_code):
        # 获取验证码参数
        action, amzn, amznr = get_verify_parameter(html_code, url)
        # 拼接图片请求referer
        referer1 = 'https://www.amazon.com%s?amzn=%s&amzn-r=%s&field-keywords=' % \
                         (action, amzn, amznr)
        # 先识别验证码图片
        debug_log.info('ip[%s] 第%s次破解验证码程序启动, 原url[%s], 验证码url[%s]' % (ip, 3 - retry + 1, url, referer1))
        verify_string = get_verify_img(html_code, ua, ip, cookie, debug_log, referer1, ipQ)
        if verify_string:
            print('verify_string: ', verify_string)
            # 拼接请求url
            # %s1: action, %s2: amzn, %s3: zmznr, %s4: verify_string,
            verify_url = 'https://www.amazon.com%s?amzn=%s&amzn-r=%s&field-keywords=%s' % \
                         (action, amzn, amznr, verify_string)
            print('verify_url: ', verify_url)
            result_html = get_verify_html(verify_url, ua, ip, cookie, debug_log, referer, ipQ)
            if retry > 0:
                return confirm_html(result_html, url, ua, ip, cookie, debug_log, referer, ipQ, retry=(retry - 1))
    else:
        if retry == 3:
            debug_log.info('url[%s] 没有遇到验证码 ip[%s]' % (url, ip))
        elif retry == 0:
            if is_RobotCheck(result_html):
                debug_log.war('ip[%s] 第%s次破解验证码依然失败, url[%s], 放弃破解' % (ip, 2 - retry + 1, url))
            else:
                debug_log.war('ip[%s] 第%s次破解验证码成功, url[%s]' % (ip, 2 - retry + 1, url))
        else:
            debug_log.war('ip[%s] 第%s次破解验证码成功, url[%s]' % (ip, 2 - retry + 1, url))


    return result_html


def get_verify_html(url, ua, ip, cookie, debug_log, referer, ipQ, timeout=10):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': ua,
        'Host': 'www.amazon.com',
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
    }
    html = ''
    proxy = {'https': 'https://%s' % (ip), 'http': 'http://%s' % (ip)}
    if BASE_TYPE == 'develop':
        proxy = None
    print('request cookie: ', cookie)
    session = requests.Session()
    if cookie:
        session.cookies = cookie
        cookie_dict = requests.utils.dict_from_cookiejar(cookie)
        print('\n', cookie_dict, type(cookie_dict), '\n')
        cookies_list = []
        for k, v in cookie_dict.items():
            kv = '%s=%s' % (k, v)
            cookies_list.append(kv)
        cookie_str = '; '.join(cookies_list)
        headers['Cookie'] = cookie_str
        print('\nCookie_dict: ', cookie_str, '\n')
    print('\nheaders: ', headers)
    SLEEP = Sleep.randint_sleep(9, 16)
    print('\nrequest休眠时间: ', SLEEP, type(SLEEP))
    time.sleep(SLEEP)
    # ipQ.record_use_times(ip)
    if url.startswith('https://www.amazon.com') or url.startswith('http://www.amazon.com'):
        response = session.get(url, headers=headers, proxies=proxy, timeout=timeout)
        status_code = response.status_code
        if status_code == 200 or status_code == 302:
            response.encoding = 'utf-8'
            html = response.text
    else:
        debug_log.error('[%s] get_verify_html下载 [%s] url不合法' % (ip, url))

    return html


def get_verify_parameter(html_code, url):
    action = '/errors/validateCaptcha'
    htmEtree = etree.HTML(html_code)
    amzn = htmEtree.xpath('//input[@name="amzn"]/@value')
    print('amzn: ', amzn)
    if amzn:
        amzn = unquote(amzn[0])
    else:
        amzn = ''

    if 'field-keywords' in url:
        amznr = htmEtree.xpath('//input[name="amzn-r"]/@value')
        if amznr:
            amznr = unquote(amznr[0])
    else:
        url_parse = urlparse(url)
        amznr = unquote(url_parse.path + '?' +url_parse.query)


    return action, amzn, amznr


def get_img(url, ua, ip, cookie, debug_log, referer, ipQ, timeout=10):
    '''cookie不能为空'''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.5',
        'accept-encoding': 'gzip, deflate, br',
        'user-agent': ua,
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'upgrade-insecure-requests': '1',
    }
    proxy = {'https': 'https://%s' % (ip), 'http': 'http://%s' % (ip)}
    if BASE_TYPE == 'develop':
        proxy = None
    # print('img cookie: ', cookie)
    session = requests.Session()
    session.cookies = cookie
    cookie_dict = requests.utils.dict_from_cookiejar(cookie)
    # print('\nimg cookie_dict: ', cookie_dict, type(cookie_dict), '\n')
    cookies_list = []
    for k, v in cookie_dict.items():
        kv = '%s=%s' % (k, v)
        cookies_list.append(kv)
    cookie_str = '; '.join(cookies_list)
    headers['cookie'] = cookie_str
    SLEEP = Sleep.random_sleep() + 3 
    print('\nget img 休眠时间: ', SLEEP, type(SLEEP))
    time.sleep(SLEEP)
    response = session.get(url, headers=headers, proxies=proxy, timeout=timeout)
    status_code = response.status_code
    print('img status_code', status_code)
    img = ''
    if status_code == 200 or status_code == 302:
        response.encoding = 'utf-8'
        img = response.content
        # print('img response.content: ', len(img), type(img))
        # print('\nimg response.cookies: ', response.cookies, '\n')
    return img


def get_verify_img(html_code, ua, ip, cookie, debug_log, referer, ipQ):
    xpath_list = [
        '//div[@class="a-row a-text-center"]/img/@src',
        '//div[@class="a-box"]/div/div/img/@src',
        '//div[@class="a-box"]//img/@src',
    ]
    url = ''
    img_string = ''
    img = None
    img_url = BaseParser.get_new_data(xpath_list=xpath_list, html_code=html_code)
    if len(img_url) > 0:
        url = img_url[0]
    if url and cookie:
        img = get_img(url, ua, ip, cookie, debug_log, referer, ipQ)
    if img:
        print('img: ', len(img), type(img))
        img_str_list= amazon_captcha_crack.main(img)
        img_string = ''.join(img_str_list)
    return img_string

"""

if __name__ == '__main__':
    time1 = time.time()
    # from pprint import pprint
    #
    ip = '192.126.168.2:3128'
    proxy = dict(
        https='https://%s' % (ip),
    )
    print(proxy)
    # html = get_html('https://www.amazon.com/dp/B01C4N6IBA', ip, proxy=proxy)
    # print(type(html))
    # print(len(html))
    # parser = HtmlParser()
    # pprint(parser.parser_goods(html, 'B01C4N6IBA'))
    time2 = time.time()
    print(time2 - time1)
    # from conf.setting import DB_CONFIG, REDIS_CONFIG, BASE_DIR
    #
    UA = UaPond.get_new_ua()
    # print(DB_CONFIG)
    # print(REDIS_CONFIG)
    # print(BASE_DIR)
    print(UA)

