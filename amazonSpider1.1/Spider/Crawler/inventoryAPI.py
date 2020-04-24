#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
sys.path.append("../../")
import os
import re
import time
import lxml.etree
from random import randint
from lxml.html import etree
from lxml.html import tostring
from copy import deepcopy

import requests
from retrying import retry
from fake_useragent import UserAgent
from conf.setting import BASE_DIR
from conf.setting import PROXY_HTTP, PROXY_HTTPS
from conf.setting import PROXY_HTTP_INV, PROXY_HTTPS_INV
from conf.setting import PROXY_VERIFY
from utils.decorator import async_lock
from utils.decorator import timer


url_type = 'inventory'

'''product and inventory'''
# 是否二手
def is_buy_used(**kwargs):
    if kwargs.get('html_code', ''):
        pattern_list = [
            re.compile('Buy used:'),
        ]
        need_param = dict(
            pattern_list=pattern_list,
            pattern_str=kwargs.get('html_code'),
            url_type=kwargs.get('url_type'),
        )
        if len(get_data(**need_param)) > 0:
            return True
    return False


# 是否prime
def is_try_prime(**kwargs):
    if kwargs.get('html_code', ''):
        pattern_list = [
            re.compile('Try Prime free for 30 days'),
            re.compile('<a id="pe-bb-signup-button-announce".*?Try Prime.*?</', re.S),
        ]
        need_param = dict(
            pattern_list=pattern_list,
            pattern_str=kwargs.get('html_code'),
            url_type=kwargs.get('url_type'),
        )
        if len(get_data(**need_param)) > 0:
            return True
    return False


# 是否404
def is_not_found(**kwargs):
    if kwargs.get('status_code', None) == 404:
        return True
    elif kwargs.get('html_code', ''):
        pattern_list = [
            re.compile('Page Not Found', re.S),
            re.compile('Sorry! We couldn', re.S),
            re.compile('Dogs of Amazon', re.S),
        ]
        need_param = dict(
            pattern_list=pattern_list,
            pattern_str=kwargs.get('html_code'),
            url_type=kwargs.get('url_type'),
        )
        if len(get_data(**need_param)) > 0:
            return True
    return False


# 是否验证码
def is_robot_check(**kwargs):
    if kwargs.get('html_code', ''):
        pattern_list = [
            re.compile('Robot Check', re.S),
            re.compile('Bot Check', re.S),
            re.compile('Amazon CAPTCHA', re.S),
        ]
        need_param = dict(
            pattern_list=pattern_list,
            pattern_str=kwargs.get('html_code'),
            url_type=kwargs.get('url_type'),
        )
        if len(get_data(**need_param)) > 0:
            return True
    return False


# 是否不可售
def is_currently_unavailable(**kwargs):
    if kwargs.get('xpath_obj') is not None:
        xpath_list = [
            '//*[contains(@id, "uybox")]//*[contains(text(), "urrently unavailable")]//text()',
            '//*[contains(@id, "uyBox")]//*[contains(text(), "urrently unavailable")]//text()',
        ]
        need_param = dict(
            xpath_list=xpath_list,
            xpath_obj=kwargs.get('xpath_obj'),
            url_type=kwargs.get('url_type'),
        )
        result_list = get_data(**need_param)
        if len(result_list) > 0:
            the_html = ''.join(result_list)
            if re.search('[Cc]urrently unavailable', the_html):
                return True
        return False
    return False


# 是否buying options
def is_see_all_buying_options(**kwargs):
    if kwargs.get('html_code', ''):
        pattern_list = [
            re.compile('id="buybox-see-all-buying-choices-announce"', re.S),
            re.compile('See All Buying Options', re.S),
        ]
        need_param = dict(
            pattern_list=pattern_list,
            pattern_str=kwargs.get('html_code'),
            url_type=kwargs.get('url_type'),
        )
        if len(get_data(**need_param)) > 0:
            return True
    return False


# 是否没有库存
def is_not_qty(**kwargs):
    if kwargs.get('xpath_obj') is not None:
        xpath_list = [
            '//*[@id="wayfinding-breadcrumbs_feature_div"]//text()|//*[@id="nav-subnav"]//text()',
        ]
        need_param = dict(
            xpath_list=xpath_list,
            xpath_obj=kwargs.get('xpath_obj'),
            url_type=kwargs.get('url_type'),
        )
        result_list = get_data(**need_param)
        if len(result_list) > 0:
            html = ''.join(result_list)
            pattern_list = [
                            # not_qty 不拿库存的类别
                re.compile('Home & Business Services'),   # 家庭服务
                re.compile('Prime Video'),                # 电影类
                re.compile('Apps & Games'),               # app类
                re.compile('Kindle Store'),               # kindle 电子书
                re.compile('Gift Card'),                  # Gift Cards 定制卡片
                re.compile('Handmade Products'),          # 手工制品
                re.compile('Books'),                      # 书籍类(业务不拿)
                re.compile('Movies & TV'),                # 视频类
                re.compile('Digital Music'),              # 数字音乐
                re.compile('Alexa Skill'),                # Alexa Skill 类
                re.compile('Download Store'),             # 下载类音乐等(一个小类.)
                # re.compile('Home & Kitchen'),             # Home & Kitchen (要继续拿库存了)
            ]
            need_param = dict(
                pattern_list=pattern_list,
                pattern_str=html,
                url_type=kwargs.get('url_type'),
            )
            if len(get_data(**need_param)) > 0:
                return True
    return False


# 是否需要定制
def if_customize(**kwargs):
    if kwargs.get('xpath_obj') is not None:
        xpath_list = [
            '//*[@id="buybox"]//*[contains(text(), "Customize Now")]',
            '//*[@id="buybox"]//*[contains(text(), "This product needs to be customized before adding to cart")]',
        ]
        need_param = dict(
            xpath_list=xpath_list,
            xpath_obj=kwargs.get('xpath_obj'),
            url_type=kwargs.get('url_type'),
        )
        result_list = get_data(**need_param)
        if len(result_list) > 0:
                return True
    return False


# 产品分析
def product_analyze(**kwargs):
    result = dict(
        not_qty=is_not_qty,
        buy_used=is_buy_used,
        try_prime=is_try_prime,
        not_found=is_not_found,
        robot_check=is_robot_check,
        unavailable=is_currently_unavailable,
        buying_options=is_see_all_buying_options,
        customize=if_customize
    )
    kwargs.setdefault('pattern_str', kwargs.get('html_code', ''))
    kwargs.setdefault('xpath_obj', etree.HTML(kwargs.get('html_code', '')))
    for item in result:
        result[item] = result[item](**kwargs)
    result.setdefault('asin', kwargs.get('asin'))
    return result


# user agent
get_ua = lambda location: UserAgent(use_cache_server=False, path=location).random


# 缺省请求头
default_headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8,tr;q=0.7,ru;q=0.6',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'close',
}


# 验证码检测
def check_errors(ret):
    if "Enter the characters you see below" in ret:
        if "--debug" in sys.argv or True: print("captcha")
        raise Exception("Exception: Captcha")
    if "Sorry! Something went wrong!" in ret:
        if "--debug" in sys.argv or True: print("block")
        raise Exception("Exception: block")


# requests.get

# @async_lock
@retry(stop_max_attempt_number=10)
def get_use_requests(params):
    '''
    :param params: need the dict
    :return:
    '''
    try:
        # 必要参数
        url = params['url']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception('Required parameter missing: url')

    # 用于动态调整参数
    need_param = dict(
        headers=None,
        cookies=None,
        proxies=None,
        verify=None,
        timeout=60,
    )
    # 过滤参数
    need_param = filter_params(need_param=need_param, params=params)
    the_headers = deepcopy(default_headers)
    try:
        # 设置'User-Agent'
        location = os.path.join(BASE_DIR, 'conf/UAPOND.json')
        the_headers['User-Agent'] = get_ua(location)
        # 检查headers, 设置缺省值
        need_param.setdefault('headers', the_headers)
        need_param['url'] = url
        print(get_use_requests.__name__, params.get('num'), need_param)
        resp = requests.get(**need_param)
        check_errors(resp.text)
        time.sleep(3)
        return resp.text, resp, need_param
    except Exception as e:
        if "NotFound" in str(e):
            raise Exception("NOT_FOUND")
        raise e


# requests.post
# @async_lock
@retry(stop_max_attempt_number=10)
def post_use_requests(params):
    '''
    :param params: need the dict
    :return:
    '''
    try:
        # 必要参数
        url = params['url']
        data = params['data']
        user_anget = params['user_anget']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception('Required parameter missing: url, user_anget')
    # 用于动态调整参数
    need_param = dict(
        headers=None,
        cookies=None,
        proxies=None,
        verify=None,
        timeout=60,
    )
    # 过滤参数
    need_param = filter_params(need_param=need_param, params=params)
    the_headers = deepcopy(default_headers)
    try:
        # 设置'User-Agent'
        the_headers['User-Agent'] = user_anget
        # 检查headers, 设置缺省值
        need_param.setdefault('headers', the_headers)
        need_param['url'] = url
        need_param['data'] = data
        print(post_use_requests.__name__, params.get('num'), need_param)
        time.sleep(3)
        resp = requests.post(**need_param)
        check_errors(resp.text)
        return resp.text, resp, need_param
    except Exception as e:
        if "NotFound" in str(e):
            raise Exception("NOT_FOUND")
        raise e


# 参数过滤
def filter_params(need_param=None, params=None):
    if type(need_param) is not dict or type(params) is not dict:
        return
    give_up_params = []
    for param in need_param:
        need_param[param] = params.get(param, None)
    for param in need_param:
        if need_param[param] is None:
            give_up_params.append(param)
    # print(give_up_params)
    for param in give_up_params:
        need_param.pop(param)
    return need_param


# 解析函数
# @timer
def get_data(xpath_obj=None, xpath_list=None, pattern_list=None, pattern_str=None, url_type=None):
    result = []
    if pattern_list is not None and pattern_str is not None :
        if type(pattern_str) is str:
            for pattern in pattern_list:
                data = []
                try:
                    data = pattern.findall(pattern_str)
                except Exception as e:
                    print('pattern, {}, extract, {} unsuccessful, error, {}'.format(pattern, url_type, e))
                if len(data) > 0:
                    # print('pattern, {}, extract, {} successful, result, {}'.format(pattern, url_type, data))
                    result = data
                    return result

    if xpath_obj is not None and xpath_list is not None:
        if type(xpath_obj) is lxml.etree._Element:
            for xpath in xpath_list:
                data = []
                try:
                    data = xpath_obj.xpath(xpath)
                except Exception as e:
                    print('xpth, {}, extract, {}, error, {}'.format(xpath, url_type, e))
                if len(data) > 0:
                    # print('xpth, {}, extract, {}, result, {}, type, {}'.format(xpath, 'succeed', data, type(data)))
                    result = data
                    return result

    return result


# 解析基类
class Parse:
    @staticmethod
    # @timer
    def get_new_data(xpath_obj=None, xpath_list=None, pattern_list=None, pattern_str=None, url_type=None):
        parameter = dict(
            xpath_obj=xpath_obj,
            xpath_list=xpath_list,
            pattern_list=pattern_list,
            pattern_str=pattern_str,
            url_type=url_type,
        )
        data = get_data(**parameter)
        return data


# 解析库存
class InventoryParser(Parse):


    @staticmethod
    def get_post_data(params):
        try:
            # 必要参数
            asin = params['asin']
            xpath_obj = params['xpath_obj']
        except KeyError:
            # 模拟位置参数, 缺则报错
            raise Exception('Required parameter missing: asin, xpath_obj')
        # html = str(tostring(xpath_obj), encoding='utf-8')
        # print(html)
        # with open('%s_post_data.html' % (asin), 'w') as f: f.write(html)
        offerListingID = xpath_obj.xpath('//*[@id="offerListingID"]/@value')[0] if xpath_obj.xpath(
            '//*[@id="offerListingID"]/@value') else ''
        if not offerListingID:
            offerListingID = xpath_obj.xpath('//*[@name="offeringID.1"]/@value')[0] if xpath_obj.xpath(
                '//*[@name="offeringID.1"]/@value') else ''
        if not offerListingID:
            return None
        sessionID = xpath_obj.xpath('//*[@id="session-id"]/@value')[0] if xpath_obj.xpath('//*[@id="session-id"]/@value') else ''
        if not sessionID:
            sessionID = xpath_obj.xpath('//*[@name="session-id"]/@value')[0] if xpath_obj.xpath('//*[@name="session-id"]/@value') else ''

        post_datas = {
            "session-id": sessionID,
            "sr": "8-11",
            "signInToHUC": 0,
            "metric-asin." + asin: 1,
            "registryItemID.1": "",
            "registryID.1": "",
            "quantity.1": 999,
            "offeringID.1": offerListingID,
            "isAddon": 0,
            "submit.addToCart": "Add+to+cart"
        }
        return post_datas


    @staticmethod
    def get_qty(params):
        try:
            # 必要参数
            html_code = params['html_code']
            xpath_obj = params['xpath_obj']
        except KeyError:
            # 模拟位置参数, 缺则报错
            raise Exception('Required parameter missing: html_code, xpath_obj')
        qtydt = 0
        xpath_list = [
            '//*[text()="Cart subtotal"]/../..//text()',  # 案例 B01G8UTA3S B000YJ2SLG 076115678x
        ]
        result_lsit = Parse.get_new_data(xpath_list=xpath_list, xpath_obj=xpath_obj)
        if len(result_lsit) > 0:
            item_list = []
            for item in result_lsit:
                item = item.lstrip().strip()
                item_list.append(item)
            item_str = ''.join(item_list)
            result_list = re.findall("Cart subtotal.*?\((\d+) item[s]*\):.*?\$[\d\.,]+", item_str)
            if len(result_list) > 0:
                result = result_list[0].lstrip().strip()
                if result.isdigit():
                    xpath_list = [
                        '//div[@id="huc-v2-box-warning"]//p/text()',
                    ]
                    limit_list = Parse.get_new_data(xpath_list=xpath_list, xpath_obj=xpath_obj)
                    if len(limit_list) > 0:
                        if re.search("from this seller has a limit of %s per customer" % (result), " ".join(limit_list)):
                            qtydt = 2
                    return int(result), qtydt

        return -1, 1


# get下载器协程封装
def get(**kwargs):
    return get_use_requests(kwargs)


# post下载器协程封装
def post(**kwargs):
    return post_use_requests(kwargs)


# 库存下载器
@timer
def post_inventory(**kwargs):
    proxy = {'https': PROXY_HTTPS_INV, 'http': PROXY_HTTP_INV}
    kwargs.setdefault('proxies', proxy)
    if 'proxy.crawlera.com' in proxy.get('https', ''):
        kwargs['verify'] = PROXY_VERIFY
    return post(**kwargs)


# 产品下载器
@timer
def get_product(**kwargs):
    proxy = {'https': PROXY_HTTPS_INV, 'http': PROXY_HTTP_INV}
    kwargs.setdefault('proxies', proxy)
    if 'proxy.crawlera.com' in proxy.get('https', ''):
        kwargs['verify'] = PROXY_VERIFY
    return get(**kwargs)


def post_html(**kwargs):
    try:
        data = kwargs['data']
        cookies = kwargs['cookies']
        user_anget = kwargs['user_anget']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception(
            'Required parameter missing: '
            'data, xpath_obj, cookies'
        )

    kwargs.setdefault('url', 'https://www.amazon.com/gp/item-dispatch/ref=olp_atc_new_2')
    return post_inventory(**kwargs)


# See All Buying options opotions 类处理
def get_buying_options(**kwargs):
    try:
        # 必要参数
        asin = kwargs['asin']
        xpath_obj = kwargs['xpath_obj']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception('Required parameter missing: asin, xpath_obj')
    options_url = 'https://www.amazon.com/gp/offer-listing/%s/ref=dp_olp_new_mbc?ie=UTF8&condition=new' % (asin)
    if re.search('^/gp/offer-list.+?condition=\w+$', options_url):
        kwargs['url'] = options_url
        kwargs['cookies'] = None
        kwargs.pop('cookies')      # 不需要cookies
        html_code, resp, param = get_product(**kwargs)
        xpath_obj = etree.HTML(html_code)
        if xpath_obj is not None:
            options_boj_list = xpath_obj.xpath('//*[@id="olpOfferList"]//div[@aria-label="More buying choices"]/div[@class="a-row a-spacing-mini olpOffer"]')
            if len(options_boj_list) > 0:
                html = str(tostring(options_boj_list[0]), encoding='utf-8')
                # print(html)
                #with open('%s_options.html' % (asin), 'w') as f: f.write(html)
                options_obj = etree.HTML(html)
                return (options_obj, resp, param)
    return tuple()


def get_post_data(**kwargs):
    try:
        # 必要参数
        asin = kwargs['asin']
        xpath_obj = kwargs['xpath_obj']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception('Required parameter missing: asin, xpath_obj')
    if kwargs.get('options_obj') is not None:
        kwargs['xpath_obj'] = kwargs['options_obj']
    return InventoryParser.get_post_data(kwargs)


def get_qty(**kwargs):
    if type(kwargs.get('product_xpath')) is lxml.etree._Element:
        xpath_list = [
            '//div[@id="availability"]//*[contains(text(), "left in stock")]/text()',
            '//form[@id="addToCart"]//*[contains(text(), "left in stock")]/text()',
        ]
        #with open('qty.html', 'w') as f: f.write(str(tostring(kwargs['product_xpath']), encoding='utf-8'))
        result_list = get_data(xpath_obj=kwargs['product_xpath'], xpath_list=xpath_list)
        # print(result_list)
        if len(result_list) > 0:
            pattern_str = ''.join(result_list)
            pattern_list = [
                re.compile('Only (\d+) left in stock'),
            ]
            result_list = get_data(pattern_list=pattern_list, pattern_str=pattern_str)
            if len(result_list) > 0:
                # print(result_list)
                if result_list[0].isdigit():
                    result_qty = int(result_list[0])
                    qtydt = 0
                    return result_qty, qtydt
        return None, None

    return InventoryParser.get_qty(kwargs)


def is_continue(**kwargs):
    pattern = re.compile('<form.*?action="/gp/verify-action/templates/add-to-cart/ordering".*?>', re.S)
    if pattern.findall(kwargs.get('post_html', '')):
        return True
    return False


def submit_cart(**kwargs):
    try:
        # 必要参数
        offeringID = kwargs['offeringID']
        sessionid = kwargs['sessionid']
        cookies = kwargs['cookies']
        user_anget = kwargs['user_anget']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception('Required parameter missing: offeringID, sessionid')
    next_data = {
        'addType': 'add-items',
        'cart-interstitial-continue': '1',
        'confirmPage': 'confirm',
        'itemCount': '1',
        'quantity.1': '999',
        'sr': '8-1',
        'submit.add-to-cart': '1',
        'submit.addToCart.x': randint(55, 69),
        'submit.addToCart.y': randint(8, 19),
    }
    next_data['offeringID.1'] = offeringID
    next_data['session-id'] = sessionid
    next_data['SessionId'] = sessionid
    url = 'https://www.amazon.com/gp/verify-action/templates/add-to-cart/ordering'
    need_params = dict(
        data=next_data,
        cookies=cookies,
        user_anget=user_anget,
        url=url,
    )
    print(submit_cart.__name__, 'need_params', need_params)
    return post_html(**need_params)


def crawler(**kwargs):
    try:
        asin = kwargs['asin']
        xpath_obj = kwargs['xpath_obj']
        cookies = kwargs['cookies']
        user_anget = kwargs['user_anget']
        buy_used = kwargs['buy_used']
        # try_prime = kwargs['try_prime']
        # product_html = kwargs['html_code']
        # not_found = kwargs['not_found']
        # robot_check = kwargs['robot_check']
        # unavailable = kwargs['unavailable']
        # buying_options = kwargs['buying_options']
    except KeyError:
        # 模拟位置参数, 缺则报错
        raise Exception(
            'Required parameter missing: '
            'asin, xpath_obj, cookies, user_anget, buy_used'
            #', try_prime, product_html, not_found, not_found'
            #', robot_check, unavailable, buying_options'
        )
    # 如果产品首页有库存, 就没必要再发postq请求了.
    '''
    <div id="availability" class="a-section a-spacing-none">
    <span class="a-size-medium a-color-price">Only 15 left in stock - order soon.</span>
    </div>  案例 asin B01FSKCC84(未来有可能变化)
    '''
    print('cookies1: ', type(cookies), cookies)
    qty, qtydt = get_qty(product_xpath=xpath_obj)
    print(qty, qtydt)
    if qty is not None:
        return qty, qtydt
    kwargs['data'] = get_post_data(asin=asin, xpath_obj=xpath_obj, options_obj=kwargs.get('options_obj'))
    # if buy_used:
    #     kwargs['url'] = 'https://www.amazon.com/gp/item-dispatch/ref=olp_atc_used_2'
    #     kwargs['data'] = get_post_data(asin=asin, xpath_obj=xpath_obj, used=True)
    # print('datas session-id: ', kwargs['data'].get('session-id'))
    # print('cookies session-id: ', cookies.get('session-id'))
    # cookies 中有时候没有 session-id 因此用网页中的 session-id 补齐
    if kwargs.get('data') is None:
        qtydt = 1
        if buy_used:
            qtydt = 9
        return -1, qtydt
    print(type(kwargs['data']), kwargs['data'])
    if cookies.get('session-id') is None:
        cookies.set('session-id', kwargs['data'].get('session-id'))
    print('cookies: ', cookies)
    if kwargs.get('product_url', '').startswith('https://www.amazon.com/dp'):
        kwargs.setdefault('referer', kwargs.get('product_url', ''))
    html_code, resp, param = post_html(**kwargs)
    #with open('%s_post.html' % (asin), 'w') as f: f.write(html_code)
    if not html_code or type(html_code) is not str:
        return -1, 1
    # 如果时需要二次提交的页面, 则进行二次提交
    if is_continue(post_html=html_code):
        submit_params = dict(
            cookies=cookies,
            user_anget=user_anget,
            offeringID=kwargs['data'].get('offeringID.1'),
            sessionid=cookies.get('session-id')
        )
        print('submit_params', submit_params)
        html_code, resp, param = submit_cart(**submit_params)
        #with open('%s_next_post.html' % (asin), 'w') as f: f.write(html_code)
    qty, qtydt = get_qty(html_code=html_code, xpath_obj=etree.HTML(html_code))
    return qty, qtydt


def inv_crawler(asin, html_code, cookies, user_agent, goods_data):
    xpath_obj = etree.HTML(html_code)
    # 分析html
    analyze_dict = product_analyze(html_code=html_code, asin=asin, xpath_obj=xpath_obj)
    inv_params = dict(
        asin=asin, xpath_obj=xpath_obj, cookies=cookies,
        user_anget=user_agent
    )
    if analyze_dict['buying_options'] or analyze_dict['buy_used']:
        options_tuple = get_buying_options(xpath_obj=xpath_obj, asin=asin)
        if len(options_tuple) == 3:
            options_obj, resp, param = options_tuple
            inv_params['options_obj'] = options_obj
            inv_params['cookies'] = resp.cookies
            inv_params['user_anget'] = param['headers'].get('User-Agent')
    inv_params.update(analyze_dict)
    # 不可售
    if analyze_dict['unavailable']:
        qty = 0
        qtydt = 5
    # 不拿库存的类别
    elif analyze_dict['not_qty']:
        qty = -1
        qtydt = 6
    # 需定制
    elif analyze_dict['customize']:
        qty = -1
        qtydt = 7
    # prime pantry
    elif analyze_dict['try_prime']:
        qty = -1
        qtydt = 8
    else:
        qty, qtydt = crawler(**inv_params)
    return qty, qtydt


def inv_start(asin, html_code, cookies, user_agent, goods_data):
    return inv_crawler(asin, html_code, cookies, user_agent, goods_data)
