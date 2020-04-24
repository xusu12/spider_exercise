#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()
import sys

sys.path.append("../")
# import os
import re
import time
from urllib import parse
from datetime import datetime
from threading import Thread
from random import randint
from lxml import etree
import demjson
from lxml.html import tostring
from bs4 import BeautifulSoup

from Crawler.BaseParser import BaseParser
from utils.util import return_PST
from Crawler.DataOutput import DataOutput
from Crawler.inventoryAPI import inv_start
# from utils.util import IpQueue
# from utils.util import Logger
from utils.decorator import timer


class GoodsParser(BaseParser):
    def __init__(self, html_code=None):
        self.url = None
        self.html_code = html_code
        self.xpath_obj = etree.HTML(html_code) if html_code else None
        self.quantity = -1
        self.qtydt = 0
        self.quantity_state = 0
        self.head_html = None
        self.desc_html = None
        self.buy_box_html = None

    # 解析商品详情
    @timer
    def parser_goods(self, html_code, the_asin, monitor_type, ip='', ua='', info_log=None, debug_log=None,
                     download_url='', cookies=None):
        if not html_code:
            return
        self.asin = the_asin
        self.html_code = html_code
        self.xpath_obj = etree.HTML(html_code)
        self.head_html = self.get_head_html(html_code)
        self.desc_html = self.get_description_html(html_code)
        self.buy_box_html = self.get_buy_box_html(html_code)
        self.cookie = cookies
        self.ip = ip
        self.ua = ua
        self.debug_log = debug_log
        if download_url:
            self.url = download_url
        # 是否多标签商品
        # son_asin_list = self.has_son_goods(html_code)
        # print('son_asin_list', type(son_asin_list), son_asin_list)
        if self._is_Currently_unavailable():
            asin_state = 2
        else:
            asin_state = 3
        customize = self._is_Customize()
        home_services = self._is_Home_Business_Services()
        if asin_state == 3 and not home_services and not customize:
            self.quantity_state = 1

        gimage = self._get_image_group()
        # print('parser_goods.gimage: ', gimage)
        # asin = self._get_current_asin()  # asin
        pasin = self._get_parent_asin() or ""  # 父asin
        title = self._get_title()  # 标题
        image = GoodsParser._get_log_image(gimage)  # 图片
        if not image:
            image = self._get_image()
        brand = self._get_brand()  # 品牌
        sname = self._get_seller_name()  # 卖家
        seller_id = self._get_seller_id()
        if not sname:
            seller_id = ''
        dpre = self._get_original_price()  # 原价
        price = self._get_discount_price()  # 产品价格
        if price <= 0:
            price = self._get_cart_price()
        # 如果是不可售, 价格又为负数, 则赋值为0
        if asin_state == 2 and price < 0:
            price = 0
        ts_min_price = self._to_price()  # 跟卖最低价格
        if ts_min_price <= 0 or ts_min_price > price:
            if price > 0:
                ts_min_price = price
        if price <= 0 and ts_min_price > 0:
            price = ts_min_price
        to_sell = self._to_sell()  # 跟卖数
        if to_sell <= 0 and asin_state == 3:
            to_sell = 1
        bsr, bsrTuple_list = self._get_bsrRank(html_code)  # 销量排名（取大类排名包含(See Top 100)字样）
        best_seller_1 = self._is_best_seller_1(bsr)  # 分类销量是否第一, 0(为否)
        qa_count = self._get_qa_count()  # 问答数
        rc = self._get_review_count()  # 评论数
        rrg = self._get_review_rating()  # 综合评分
        byb = self._has_buy_button()  # 是否有黄金购物车按钮, 0(为否)
        print('byb1', byb)
        r5p = self._get_review_5_percent()  # 5星评价百分比
        r4p = self._get_review_4_percent()  # 4星评价百分比
        r3p = self._get_review_3_percent()  # 3星评价百分比
        r2p = self._get_review_2_percent()  # 2星评价百分比
        r1p = self._get_review_1_percent()  # 1星评价百分比
        feature = self._get_feature()  # 商品说明
        image_more = GoodsParser._get_image_more(gimage)  # 更多图片
        # print('parser_goods.image_more1: ', image_more)
        # variant = self._get_variant()
        variant = ''
        # try_prime 也定义成黄金购物车
        try_prime = self._has_try_prime()
        if rc <= 0:
            rrg = r5p = r4p = r3p = r2p = r1p = 0
        if try_prime > 0:
            byb = 1
        print('byb2', byb)
        if not image_more:
            image_more = self._get_ima_more()
        # print('parser_goods.image_more2: ',image_more)
        if the_asin == pasin:
            asin_type = 1
        elif not pasin:
            asin_type = 3
        else:
            asin_type = 2
        release_date = self._get_release_date()  # 发布日期
        if byb > 0:
            cart_price = price  # 购物车价格
        else:
            cart_price = 0
        discount_price = price
        if dpre <= 0:
            dpre = price
        # # 未解决字段
        # category = ''       # 分类
        #
        if self.quantity_state == 1:
            pass
        if asin_state == 2:
            to_sell = 0
            quantity = 0
        else:
            quantity = self.quantity
        qtydt = self.qtydt
        if quantity < 0:
            qtydt = 1
        goods_data = dict(
            asin=the_asin,  # asin
            pasin=pasin,  # 父asin
            # aid="", # 亚马逊帐号id
            title=title,  # 标题
            image=image,  # 图片
            brand=brand,  # 品牌
            price=price,  # 产品价格
            cart_price=cart_price,
            # quantity=quantity,  # 库存
            is_monitor=1,  # 是否监控（从数据库读取）
            monitor_type=monitor_type,  # 是否监控（从数据库读取）
            # state=0,        # （从数据库读取）
            # refresh_tm=int(time.time()),  # 似乎不用存
            # sale_quantity=sale_quantity,    # 销售总量
            sale_price=discount_price,  # 优惠价格
            sname=sname,  # 卖家
            seller_id=seller_id,  # 商家id
            ts_min_price=ts_min_price,  # 跟卖最低价格
            to_sell=to_sell,  # 跟卖数
            byb=byb,  # 是否有黄金购物车按钮, 0(为否)
            bsr=bsr,  # 销量排名  65 （取下面三个Best Sellers Rank中最小的那个）
            rc=rc,  # 评论数
            rrg=rrg,  # 综合评分
            r5p=r5p,  # 5星评价百分比
            r4p=r4p,  # 4星评价百分比
            r3p=r3p,  # 3星评价百分比
            r2p=r2p,  # 2星评价百分比
            r1p=r1p,  # 1星评价百分比
            feature=feature,  # 商品说明
            refresh_tm=0,  # 更新时间
            collect_tm=0,  # 收集时间
            getinfo_tm=int(BaseParser.get_redis_time()),  # 得到信息时间
            bs1=best_seller_1,  # 分类销量是否第一, 0(为否)
            qc=qa_count,  # 问答数
            release_date=release_date,  # 发布日期
            asin_type=asin_type,
            image_more=image_more,  # 更多图片
            variant=variant,  # 变体
            asin_state=asin_state,
            dpre=dpre,  # 原价, 只有历史库要存
            # qtydt=qtydt,    # 库存, 只有历史库要存
            aday=return_PST().strftime("%Y%m%d"),  # 获取数据的太平洋日期
        )
        # print('getinfo_tm', goods_data['getinfo_tm'])
        bsr_data = {}
        # print('selfcesser bsrTuple_list', bsrTuple_list)
        if len(bsrTuple_list) > 0:
            bsr_data = {the_asin: bsrTuple_list}
        # print('processer bsrdata', bsr_data)
        goods_datas = {the_asin: goods_data}

        # if self.url:
        #     data['url'] = self.url
        # if the_asin == asin:
        #     data['is_ok'] = 1
        # else:
        #     data['is_ok'] = 0
        print('goods_datas, bsr_data', goods_datas, bsr_data)
        # 如果这四个参数都没有, 说明爬取失败.
        if not title and not image and price <= 0 and not brand:
            goods_datas = {}
        print('goods_datas, bsr_data', goods_datas, bsr_data)
        return goods_datas, bsr_data

    @staticmethod
    def get_head_html(html_code):
        result = ''
        xpath_list = [
            '//*[@id="ppd"]',
            '//*[@id="centerCol"]',
        ]
        result_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        if len(result_list) > 0:
            result = str(tostring(result_list[0]), encoding='utf-8')
        return result

    @staticmethod
    def get_buy_box_html(html_code):
        result = ''
        xpath_list = [
            '//*[@id="buybox"]',
        ]
        result_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        if len(result_list) > 0:
            result = str(tostring(result_list[0]), encoding='utf-8')
        return result

    @staticmethod
    def get_description_html(html_code):
        result = ''
        xpath_list = [
            '//*[@id="detail-bullets"]',
            '//*[@id="descriptionAndDetails"]',
        ]
        result_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        if len(result_list) > 0:
            result = str(tostring(result_list[0]), encoding='utf-8')
        return result

    def _is_Home_Business_Services(self, html_code=None):
        'Home & Business Services'
        if not html_code:
            html_code = self.html_code
        xpath_list = [
            '//*[@id="wayfinding-breadcrumbs_feature_div"]',
            '//*[@id="nav-subnav"]',
        ]
        html_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        # print(html_list)
        if len(html_list) > 0:
            html = str(tostring(html_list[0]), encoding='utf-8')
            pattern_list = [
                re.compile('Home & Business Services', re.S),
                re.compile('Prime Video', re.S),
                re.compile('Gift Cards', re.S),
                re.compile('Business Services', re.S),
            ]

            result = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=html)
            if len(result) > 0:
                return True

        return False

    def _is_Currently_unavailable(self, html_code=None):
        if not html_code:
            html_code = self.html_code
        xpath_list = [
            '//*[contains(@id, "uybox")]//*[contains(text(), "urrently unavailable")]//text()',
            '//*[contains(@id, "uyBox")]//*[contains(text(), "urrently unavailable")]//text()',
            '//*[contains(@id, "availability")]//*[contains(text(), "urrently unavailable")]//text()',
            '//*[contains(@id, "availability")]//*[contains(text(), "item will be back in stock")]//text()',
            # We don't know when or if this item will be back in stock.
        ]
        result_list = GoodsParser.get_new_data(xpath_obj=self.xpath_obj, xpath_list=xpath_list)
        if len(result_list) > 0:
            the_html = ''.join(result_list)
            if re.search('[Cc]urrently unavailable', the_html):
                return True
            if re.search("this item will be back in stock", the_html):
                return True
        return False

    def _is_Customize(self, html_code=None):

        if not html_code:
            html_code = self.html_code

        RobotCheck_patterns = [

            re.compile('Customize Now', re.S),

        ]

        unavailable = GoodsParser.get_new_data(pattern_list=RobotCheck_patterns, html_code=html_code)

        if len(unavailable) > 0:
            return True

        return False

    def _get_quantity(self, html_code=None):
        print('_get_quantity 启动')
        self.quantity, self.qtydt = inv_start(self.asin, self.html_code, self.cookie, self.ua)

    # 销量排名
    def _get_bsrRank(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        # print(html_code)
        # if self.desc_html:
        #     html_code = self.desc_html
        top_pattern = re.compile('[Ss]ee [Tt]op 100')
        aday = return_PST().strftime("%Y%m%d")
        tm = int(BaseParser.get_redis_time())
        bsr_pattern = re.compile('[\d,]+')
        bsrInt = -1
        bsr_tuple_list = []
        xpath_list = [
            '//*[contains(text(), "Sellers Rank")]/..//text()',  # 案例 B01G8UTA3S B000YJ2SLG 076115678x
        ]
        result_list = GoodsParser.get_new_data(xpath_obj=self.xpath_obj, xpath_list=xpath_list)
        style_xpath = [
            '//*[contains(text(), "Sellers Rank")]/..//style/text()', ]  # 案例 B01G8UTA3S B000YJ2SLG 076115678x
        style_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=style_xpath)
        bsrRank_list = []
        if style_list:
            for i in result_list:
                for j in style_list:
                    # print('i', i, '\nj', j)
                    if i != j:
                        # print('bsrRank_list_i:', i)
                        if re.search('[Ss]ellers [Rr]ank', i):
                            i = i.split(':')[0] + ':'
                        i = i.strip().lstrip()
                        # print('bsrRank_list_i1:', i)
                        bsrRank_list.append(i)
        else:
            for i in result_list:
                i = i.strip().lstrip()

                if i:
                    if re.search('[Ss]ellers [Rr]ank', i):
                        i = i.split(':')[0] + ':'
                    bsrRank_list.append(i)

        if bsrRank_list:
            # print('bsrRank_list', bsrRank_list)
            bsr_str = ''.join(bsrRank_list)
            # print('bsr_str: ', bsr_str)
            bsr_str = bsr_str.split(':')[1]
            # print('bsr_str1: ', bsr_str)
            bsr_str_list = bsr_str.split('#')
            # print('bsr_str_list: ', bsr_str_list)
            result_list = []
            if type(bsr_str_list) is list:
                # print('bsr_str_list1', bsr_str_list)
                for item in bsr_str_list:
                    item = item.strip().lstrip()
                    # print('item: ', item)
                    item = ' '.join(item.split('\xa0'))
                    # print('item1: ', item)
                    result_list.append(item)
            bsrint_list = []
            if result_list:
                # print('result_list', result_list)
                for item in result_list:
                    # print('item', item)
                    if item:
                        bsrList = item.split('in')
                        bsrstr = bsrList[0].strip().lstrip()
                        bsrNum = bsr_pattern.search(bsrstr).group(0)
                        # print(bsrstr, 1)
                        # print(bsrNum, 1)
                        # print(bsrList, 12345)
                        bsr1 = bsrList[1:len(bsrList)]
                        # print(bsr1, 121)
                        bsrstring = 'in'.join(bsr1).strip().lstrip()
                        # print(bsrstring, 111)
                        item = bsrstr + ' in ' + bsrstring
                        # print(bsrstr, 1.1)
                        bsrNum = ''.join(bsrNum.split(','))
                        # print(bsrstr, 2)
                        if bsrNum.isdigit():
                            bsrint = int(bsrNum)
                            # print(bsrint, 2.1)
                            bsrTuple = (bsrint, item, aday, tm)
                            bsr_tuple_list.append(bsrTuple)
                            # print(item, 2.1, 1)

                            if top_pattern.search(item):
                                # print(bsrint, 2.2)
                                bsrInt = bsrint
                            # print(bsrInt, 2.3)
                            bsrint_list.append(bsrint)
                # print(bsrInt, 3)
                if bsrInt < 1:
                    if len(bsrint_list) > 0:
                        bsrInt = min(bsrint_list)
                        # print('bsrInt', bsrInt)
                        # print('bsrTuple_list', bsrTuple_list)
            return bsrInt, bsr_tuple_list

        soup = BeautifulSoup(html_code, 'lxml')
        table = soup.select('table[id="productDetails_detailBullets_sections1"]')
        if len(table) > 0:
            html_code = str(table[0])
            # print(html_code)
        xpath_list = [
            '//table[@id="productDetails_detailBullets_sections1"]//span[starts-with(text(), "#")]//text()',
        ]
        bsr_str_result_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        print('_get_bsrRank.result_list 2', bsr_str_result_list)
        if len(bsr_str_result_list) > 0:
            bsr_list = []
            for item in bsr_str_result_list:
                item = item.strip().lstrip()
                if item:
                    bsr_list.append(item)
            if len(bsr_list) > 0:
                bsr_str_list = ''.join(bsr_list).split('#')
                bsr_str_result_list = []
                if type(bsr_str_list) is list:
                    # print('bsr_str_list1', bsr_str_list)
                    for item in bsr_str_list:
                        item = item.strip().lstrip()
                        # print('item: ', item)
                        item = ' '.join(item.split('\xa0'))
                        # print('item1: ', item)
                        bsr_str_result_list.append(item)
                bsrint_list = []
                if bsr_str_result_list:
                    # print('result_list', result_list)
                    for item in bsr_str_result_list:
                        # print('item', item)
                        if item:
                            bsrList = item.split('in')
                            bsrstr = bsrList[0].strip().lstrip()
                            bsrNum = bsr_pattern.search(bsrstr).group(0)
                            # print(bsrstr, 1)
                            # print(bsrNum, 1)
                            # print(bsrList, 12345)
                            bsr1 = bsrList[1:len(bsrList)]
                            # print(bsr1, 121)
                            bsrstring = 'in'.join(bsr1).strip().lstrip()
                            # print(bsrstring, 111)
                            item = bsrstr + ' in ' + bsrstring
                            # print(bsrstr, 1.1)
                            bsrNum = ''.join(bsrNum.split(','))
                            # print(bsrstr, 2)
                            if bsrNum.isdigit():
                                bsrint = int(bsrNum)
                                # print(bsrint, 2.1)
                                bsrTuple = (bsrint, item, aday, tm)
                                bsr_tuple_list.append(bsrTuple)
                                # print(item, 2.1, 1)

                                if top_pattern.search(item):
                                    # print(bsrint, 2.2)
                                    bsrInt = bsrint
                                # print(bsrInt, 2.3)
                                bsrint_list.append(bsrint)
                    # print(bsrInt, 3)
                    if bsrInt < 1:
                        if len(bsrint_list) > 0:
                            bsrInt = min(bsrint_list)
                            # print('bsrInt', bsrInt)
                            # print('bsrTuple_list', bsrTuple_list)
                return bsrInt, bsr_tuple_list

        return bsrInt, bsr_tuple_list

    # 获取标题
    def _get_title(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        result_title = ''
        title_xpath = [
            '//h1[@id="title"]//text()',
            '//h1[@id="aiv-content-title"]//text()',
            '//h1[@class="parseasinTitle"]//text()',
            '//div[@data-feature-name="title"]//text()',  # 特殊案例 B005ZOJ5R0
        ]
        title = GoodsParser.get_new_data(xpath_list=title_xpath, xpath_obj=self.xpath_obj)
        if len(title) > 0:
            t_list = []
            for t in title:
                t = t.strip().lstrip()
                if t:
                    t_list.append(t)
            if t_list:
                result_title = ''.join(t_list)
        else:
            title_xpath = [
                '//h1[contains(@id, "title")]//span[contains(@id, "Title")]/text()',  # 图书可能存在三列标题 案例　076115678X
                '//*[@id="btAsinTitle"]/text()',
                '//h1[@data-automation-id="title"]/text()',  # 电影类别的title
                '//*[@id="mas-title"]//span[contains(@class, "a-text-bold")]/text()',  # 特殊案例 B071FW2BB6
                '//div[contains(@class, "title")]//h1[contains(@class, "title")]/text()',  # 特殊案例 B01HQS5954
            ]
            title = GoodsParser.get_new_data(xpath_list=title_xpath, xpath_obj=self.xpath_obj)
            if len(title) > 0:
                result_title = title[0].strip().lstrip()

        if len(result_title) > 255:
            result_title = result_title[0:247] + '...'
        return result_title

    # 获取图片组
    def _get_image_group(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        image_patterns = [
            re.compile("colorImages'.+?{(.+)'colorToAsin", re.S),

        ]
        image_json = GoodsParser.get_new_data(html_code=html_code, pattern_list=image_patterns)
        # print('_get_image_group.image_json: ', image_json)
        if image_json is None:
            return []
        else:
            img_str = ''.join(image_json).strip()
            if 'initial' in img_str and img_str.endswith('},'):
                son_goods_list1 = img_str.rstrip('},')
                img_str = son_goods_list1.lstrip("'initial':").strip()
                image_json = demjson.decode(img_str) if img_str else None
            gimage = [{'hiRes': i['large'], 'variant': i['variant']} for i in image_json]
            # print('_get_image_group.gimage: ', gimage)
            return gimage

    # 获取urltitle(存redis拼url用)
    @staticmethod
    def get_urltitle(asin, html_code):
        urlTitle = ''
        pattern_list = [
            re.compile('<link rel="canonical.+?com/([A-Za-z0-9\-]+)/dp/.*?/>', re.S),
        ]
        urlT = GoodsParser.get_new_data(html_code=html_code, pattern_list=pattern_list)
        # print('urlT', urlT, asin)
        if len(urlT):
            urlTitle = urlT[0]
        return urlTitle

    # 获取主图
    @staticmethod
    def _get_log_image(gimage):
        log_image = ''
        if len(gimage) > 0:
            log_image = gimage[0].get('hiRes', '')
        return log_image

    def _get_image(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''
        img_xpath = [
            '//*[@id="landingImage"]/@src',
            '//*[@id="ebooksImgBlkFront"]/@src',
            '//*[@id="gc-standard-design-image"]/@src',
        ]
        imgs = GoodsParser.get_new_data(xpath_list=img_xpath, xpath_obj=self.xpath_obj)
        if len(imgs) > 0:
            img = imgs[0].strip().lstrip()
            return img
        else:
            xpath_list = [
                '//*[@id="imgBlkFront"]',
                '//*[contains(@id, "img")]'
                '//*[contains(@id, "image")]'
                '//*[contains(@id, "images")]'
            ]
            result_list = GoodsParser.get_new_data(xpath_list=xpath_list, html_code=html_code)
            if len(result_list) > 0:
                html = str(tostring(result_list[0]), encoding='utf-8')
                pattern_lsit = [
                    re.compile('http.*?amazon.com/images.*?jpg'),
                ]
                result1 = GoodsParser.get_new_data(pattern_list=pattern_lsit, html_code=html)
                if len(result1) > 0:
                    result = result1[0].strip().lstrip()
            return result

    # 更多图片
    @staticmethod
    def _get_image_more(gimage):
        gimage_list = []
        variant_list = []
        result_gimage = ''
        # result_variant = ''
        if len(gimage) > 0:
            more_image = gimage[1:]
            # print(more_image)
            for itme in more_image:
                image = itme.get('hiRes') or ''
                # variant = itme.get('variant', '')
                # print(image)
                if image:
                    gimage_list.append(image)
                    # if variant:
                    #     variant_list.append(variant)
            if len(gimage_list) > 0:
                result_gimage = r'%s' % ('\n'.join(gimage_list))
                # if len(variant_list):
                #     result_variant = r'%s' % ('\n'.join(variant_list))
        # print('_get_image_more.result_gimage: ', result_gimage)
        return result_gimage

    def _get_ima_more(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        img_xpath = [
            '//*[@id="altImages"]//img/@src',
        ]
        result_gimage = ''
        imgs = GoodsParser.get_new_data(xpath_list=img_xpath, xpath_obj=self.xpath_obj)
        if imgs:
            result_gimage = r'%s' % ('\n'.join(imgs))
        return result_gimage

    # 获取品牌
    def _get_brand(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        result_brand = ''
        brand_xpath = [
            '//*[@id="brand"]/text()',
            '//*[@id="gc-brand-name-link"]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_sr_book_1")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_sr_ebooks_1")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_cont_book_1")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_cont_ebooks_1")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_cont_book")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_cont_ebooks")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_sr_book")]/text()',
            '//*[@id="bylineInfo"]//a[contains(@href, "dp_byline_sr_ebooks")]/text()',
            '//div[@class="a-section a-spacing-medium"]//div[@id="mbc"]/@data-brand',
            '//*[@class="a-row item-title"]/span/text()',
            '//*[@class="qpHeadline"]/b/text()',
            '//*[@id="mbc"]/@data-brand',
            '//*[@id="bylineInfo"]/text()',
            '//*[@id="ProductInfoArtistLink"]/text()',  # 特殊案例 B005ZOJ5R0
        ]
        brand = GoodsParser.get_new_data(xpath_list=brand_xpath, xpath_obj=self.xpath_obj)
        # print(brand)
        if len(brand) > 0:
            result_brand = brand[0].lstrip().strip()
        else:
            brand_xpath = [
                '//img[@id="brand"]/@src',
                '//img[@id="logoByLine"]/@src'
            ]
            brand_url = GoodsParser.get_new_data(xpath_list=brand_xpath, xpath_obj=self.xpath_obj)
            if brand_url:
                result_brand = brand_url[0].strip().lstrip()

        return result_brand

    # 获取父asin
    def _get_parent_asin(self, html_code=None):
        '''
        "currentAsin" : "B00CM220CK",
            "parentAsin" : "B017X9JIBM",
        :param html_code:
        :return:
        '''
        if html_code is None:
            html_code = self.html_code
        asin_patterns = [
            re.compile('parentAsin".*?"([A-Za-z0-9]+?)",', re.S),
            re.compile('parentAsin".*?"(.+?)",', re.S),
        ]
        asin = GoodsParser.get_new_data(pattern_list=asin_patterns, xpath_obj=self.xpath_obj)
        if len(asin) > 0:
            asin = asin[0]
            asin = GoodsParser.filter_str(asin)
            return asin
        else:
            return ''

    # 获取当前asin(用来做逻辑校验)
    def _get_current_asin(self, html_code=None):
        '''
        "currentAsin" : "B00CM220CK",
            "parentAsin" : "B017X9JIBM",
        :param html_code:
        :return:
        '''
        if html_code is None:
            html_code = self.html_code
        asin_xpath = [
            '//input[@id="ASIN"]/@value',
        ]
        asin = GoodsParser.get_new_data(xpath_list=asin_xpath, xpath_obj=self.xpath_obj)
        if len(asin) > 0:
            asin = asin[0]
            asin = GoodsParser.filter_str(asin)
            return asin
        else:
            return ''

    # 获取商家名称
    def _get_seller_name(self, html_code=None):
        if self._is_Currently_unavailable():
            return ''
        if self._is_see_all_Buying():
            return 'none'
        if html_code is None:
            html_code = self.html_code
        not_sold_by_list = ['View shipping rates and policies', 'Shipping']
        sold_by = ''
        xpath_list = [
            '//*[@id="merchant-info"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            soldby_html = str(tostring(result_list[0]), encoding='utf-8')
            # print(soldby_html)
            pattern_list = [
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
            ]
            sold_by_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=soldby_html)
            # print('Sold by: ', sold_by_list)
            if len(sold_by_list) > 0:
                sold_by = sold_by_list[0].strip().lstrip()
                print('sold_by1', sold_by)
                if len(sold_by) > 128 or sold_by in not_sold_by_list:  # print('Sold by1: ', sold_by)
                    sold_by = ''
                if sold_by:
                    print('sold_by2', sold_by)
                    return sold_by
            sold_by_pattern = [
                re.compile('[Ss]old merchants on (Amazon.com)', re.S),
                re.compile('Ships from and [Ss]old by (Amazon.com)', re.S),
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=.*?>([\w].*?)</', re.S),
                re.compile('Ships from and [Ss]old by ([\w][A-Za-z0-9 ,\'\&\(\)\.-_]+)\..*?</', re.S),
                re.compile('[Ss]old and delivered by([[\w]A-Za-z0-9 ,\'\&\(\)\.-_]+),.*?</', re.S),
                re.compile('[Ss]old by.*?<b>([\w][A-Za-z0-9]+).*?</', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
            ]
            sold_by_list = GoodsParser.get_new_data(pattern_list=sold_by_pattern, html_code=soldby_html)
            # print('Sold by: ', sold_by_list)
            if len(sold_by_list) > 0:
                sold_by = sold_by_list[0].strip().lstrip()
                if len(sold_by) > 128 or sold_by in not_sold_by_list:  # print('Sold by1: ', sold_by)
                    sold_by = ''
                if sold_by:
                    print('sold_by2', sold_by)
                    return sold_by
        xpath_list = [
            '//*[contains(text(), "Sold by")]/../..',
            '//*[contains(text(), "Ships from and sold by")]/../..',
            '//*[contains(text(), "hips from and sold by")]/../..',
            '//*[contains(text(), "old merchants on")]/../..',
            '//*[contains(text(), "old and delivered by")]/../..',
            '//*[contains(text(), "old by")]/../..',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            soldby_html = str(tostring(result_list[0]), encoding='utf-8')
            # print(soldby_html)
            pattern_list = [
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
            ]
            sold_by_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=soldby_html)
            # print('Sold by: ', sold_by_list)
            if len(sold_by_list) > 0:
                sold_by = sold_by_list[0].strip().lstrip()
                print('sold_by3', sold_by)
                if sold_by in not_sold_by_list:
                    sold_by = ''
                if sold_by:
                    return sold_by
            sold_by_pattern = [
                re.compile('[Ss]old merchants on (Amazon.com)', re.S),
                re.compile('Ships from and [Ss]old by (Amazon.com)', re.S),
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=.*?>([\w].*?)</', re.S),
                re.compile('Ships from and [Ss]old by ([\w][A-Za-z0-9 ,\'\&\(\)\.-_]+)\..*?</', re.S),
                re.compile('[Ss]old and delivered by([[\w]A-Za-z0-9 ,\'\&\(\)\.-_]+),.*?</', re.S),
                re.compile('[Ss]old by.*?<b>([\w][A-Za-z0-9]+).*?</', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=[a-zA-Z0-9]+.*?>([\w].*?)</', re.S),
            ]
            sold_by_list = GoodsParser.get_new_data(pattern_list=sold_by_pattern, html_code=soldby_html)
            # print('Sold by: ', sold_by_list)
            if len(sold_by_list) > 0:
                sold_by = sold_by_list[0].strip().lstrip()
                print('Sold by4.1: ', sold_by)
                print(sold_by in not_sold_by_list)
            if len(sold_by) > 128 or sold_by in not_sold_by_list:  # print('Sold by1: ', sold_by)
                sold_by = ''
            print('sold_by4', sold_by)
            if sold_by:
                return sold_by
        xpath_list = [
            '//*[@id="merchant-info"]//a[@target="_blank"]/text()',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            print('sold_by5', result_list)
            sold_by = result_list[0]
            if sold_by in not_sold_by_list:
                sold_by = ''
            if sold_by:
                return sold_by
        return sold_by

    # 获取商家ID
    def _get_seller_id(self, html_code=None):
        if self._is_Currently_unavailable():
            return ''
        if self._is_see_all_Buying():
            return 'none'
        if html_code is None:
            html_code = self.html_code
        seller_id = ''
        xpath_list = [
            '//*[@id="merchant-info"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            seller_html = str(tostring(result_list[0]), encoding='utf-8')
            # print(seller_html)
            pattern_list = [
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=([a-zA-Z0-9]+)\&.*?>', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=([a-zA-Z0-9]+).*?>', re.S),
            ]
            seller_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=seller_html)
            # print('seller_id: ', seller_list)
            if len(seller_list) > 0:
                seller_id = seller_list[0].strip().lstrip()
                return seller_id
        xpath_list = [
            '//*[contains(text(), "Sold by")]/../..',
            '//*[contains(text(), "Ships from and sold by")]/../..',
            '//*[contains(text(), "hips from and sold by")]/../..',
            '//*[contains(text(), "old merchants on")]/../..',
            '//*[contains(text(), "old and delivered by")]/../..',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            seller_html = str(tostring(result_list[0]), encoding='utf-8')
            # print(seller_html)
            pattern_list = [
                re.compile('[Ss]old by.*?<a.*?dp_merchant_link.*?seller=([a-zA-Z0-9]+)\&.*?>', re.S),
                re.compile('[Ss]old by.*?<a.*?seller=([a-zA-Z0-9]+).*?>', re.S),
            ]
            seller_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=seller_html)
            # print('seller_id: ', seller_list)
            if len(seller_list) > 0:
                seller_id = seller_list[0].strip().lstrip()
                return seller_id

        pattern_list = [
            re.compile('<input.*?[Mm]erchantID.*?value="([A-Za-z0-9]+)".*?>'),
            re.compile('<input.*?erchantID.*?value="([A-Za-z0-9]+)".*?>'),
        ]

        seller_id_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=html_code)
        if len(seller_id_list) > 0:
            seller_id = seller_id_list[0].strip().lstrip()
        return seller_id

    def _is_see_all_Buying(self, html_code=None):
        if not html_code:
            html_code = self.html_code
        # print('_is_see_all_Buying')

        RobotCheck_patterns = [
            re.compile('id="buybox-see-all-buying-choices-announce"', re.S),
            re.compile('title="See All Buying Options"', re.S),
        ]
        unavailable = GoodsParser.get_new_data(pattern_list=RobotCheck_patterns, html_code=html_code)
        # print(unavailable)
        if len(unavailable) > 0:
            return True
        return False

    # 获取原价(仅历史表有用)
    def _get_original_price(self, html_code=None):
        if not html_code:
            html_code = self.html_code
        pattern = re.compile('\$[\d,\.]+')
        result = -1
        xpath_list = [
            '//*[contains(text(), "List Price:")]/../..//text()',
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(@id, "snsPrice")]//*[contains(@class, "strike")]/text()'
            # 案例　B01G8UTA3S 此案例中用下面两个会抓到假价格, 所以优先级排到第一.
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        xpath_list = [
            '//*[contains(@id, "buyNew")]//*[contains(@class, "strike")]/text()'  # 案例　0060012781　　0060899220
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        xpath_list = [
            '//*[contains(@id, "price")]//*[contains(@class, "strike")]/text()'  # 案例 B008XMBWK4 B00B4YVU4G
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        return result

    # 获取当前价格(更新表都存此价格)
    def _get_discount_price(self, html_code=None):
        if not html_code:
            html_code = self.html_code
        result = -1
        pattern = re.compile('\$[\d,\.]+')
        xpath_list = [
            '//*[@id="priceInsideBuyBox_feature_div"]//*[@id="price_inside_buybox"]/text()',  # B00XLBELKK 优先拿购物车价格
            '//*[contains(text(), "Price:")]/..//*[contains(@class, "a-color-price")]//text()',
            # '//*[contains(text(), "Sale:")]/..//*[contains(@id, "priceblock")]//text()', # B00XLBELKK 特例情况价格在Sale.
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        print('_get_discount_price.result_str: ', result_str)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            # print('_get_discount_price.result: ', result)
            if result.isdigit():
                return int(result)
        xpath_list = [
            '//*[contains(text(), "Price:")]/../..//*[contains(@class, "a-color-price")]//text()',
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(text(), "Buy New")]/../..//text()',
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(@id, "snsPrice")]//*[contains(@class, "price")]/text()',  # 案例 B014TF6LRC
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        xpath_list = [
            '//*[contains(@id, "buybox")]//*[contains(@id, "buyNew")]//*[contains(@class, "price")]/text()'
            # 案例　0060012781　0060899220
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        xpath_list = [
            '//*[contains(@id, "addToCart")]//*[contains(@id, "price")]/text()',  # 案例　B01LYCX1GU　B016X6SEAC
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(@id, "newPrice")]//*[contains(@class, "priceblock")]//text()',  # 案例　B01N5OKGLH 游戏类
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        item_list = []
        if len(result_list) > 0:
            for item in result_list:
                item = item.lstrip.strip()
                if item:
                    item_list.append(item)
        result_str = ''.join(item_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(@id, "price")]//*[contains(@id, "priceblock")]/text()',  # 案例 B014TF6LRC
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)

        xpath_list = [
            '//*[contains(@id, "price")]//*[contains(@class, "a-color-price")]/text()',  # 案例　B016X6SEAC
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        result_str = ''.join(result_list)
        serch_result = pattern.search(result_str)
        if serch_result:
            result = ''.join(''.join(''.join(serch_result.group(0).split('$')).split(',')).split('.')).strip().lstrip()
            if result.isdigit():
                return int(result)
        return result

    # 获取购物车价格(若找不到价格， 就用这个再找一遍)
    def _get_cart_price(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result_price = -1
        price_xpath = [
            '//*[@id="soldByThirdParty"]/span[1]/text()',
        ]
        price = GoodsParser.get_new_data(xpath_list=price_xpath, xpath_obj=self.xpath_obj)
        if len(price) > 0:
            price = price[0]
            if '-' in price:
                price = price.split('-')[0].strip().lstrip()
            price = ''.join(''.join(''.join(price.split("$")).split('.')).split(',')).strip().lstrip()
            if price.isdigit():
                result_price = int(price)
            # print(type(price))
            else:
                return -1
            return result_price
        else:
            price_pattern = [
                re.compile('"buyboxPrice":"\$([\d,\.]+)"', re.S),
            ]

            price = GoodsParser.get_new_data(pattern_list=price_pattern, html_code=html_code)

            # print('buyboxPrice: ', price)
            if price:

                price = price[0]

                price = ''.join(''.join(price.split('.')).split(','))

                # print('buyboxPrice1: ', price)

                if price.isdigit():
                    result_price = int(price)
                else:
                    return -1
        return result_price

    # 跟卖最低价格(如无存0)
    def _to_price(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result_price = -1
        xpath_list = [
            '//*[text()="Other Sellers on Amazon"]/../../../../..',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            # print(result_html)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('[Oo]ther [Ss]ellers.+?<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('<a.*?condition.*?>.*?[\d,]+.*?new.*?from.*?<span.*?price.*>.*?\$([0-9\.,]+).*?<', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                # print('result_list: ', result_list)
                result = result_list[0].strip().lstrip()
                result = ''.join(''.join(result.split('.')).split(','))
                if result.isdigit():
                    # print('to_price1', result)
                    return int(result)
            else:
                xpath_list = [
                    '//*[@id="mbc"]//*[contains(@class, "price")]/text()'
                ]
                result_list = GoodsParser.get_new_data(xpath_list=xpath_list, html_code=result_html)
                if len(result_list) > 0:
                    item_list = []
                    for item in result_list:
                        item = item.strip().lstrip()
                        item = ''.join(''.join(''.join(item.split('$'))).split(','))
                        if item.isdigit():
                            item_list.append(int(item))
                    if len(item_list) > 0:
                        return min(item_list)
        xpath_list = [
            '//*[@id="olpDiv"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('[Oo]ther [Ss]ellers.+?<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                result = ''.join(''.join(result.split('.')).split(','))
                if result.isdigit():
                    # print('to_price1', result)
                    return int(result)
        xpath_list = [
            '//*[@id="olp_feature_div"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('[Oo]ther [Ss]ellers.+?<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                result = ''.join(''.join(result.split('.')).split(','))
                if result.isdigit():
                    # print('to_price1', result)
                    return int(result)
        xpath_list = [
            '//*[@id="mbc"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('[Oo]ther [Ss]ellers.+?<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
                re.compile('<a.*?>.*?from.*?\$([0-9\.,]+).*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                result = ''.join(''.join(result.split('.')).split(','))
                if result.isdigit():
                    # print('to_price1', result)
                    return int(result)
        xpath_list = [
            '//*[@id="toggleBuyBox"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?[\d,]+.*?new.*?from.*?<span.*?price.*>.*?\$([0-9\.,]+).*?<', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                # print('result_list: ', result_list)
                result = result_list[0].strip().lstrip()
                result = ''.join(''.join(result.split('.')).split(','))
                if result.isdigit():
                    return int(result)

        xpath_list = [
            '//*[@id="mbc"]//*[contains(@class, "price")]/text()'
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            item_list = []
            for item in result_list:
                item = item.strip().lstrip()
                item = ''.join(''.join(''.join(item.split('$'))).split(','))
                if item.isdigit():
                    item_list.append(int(item))
            if len(item_list) > 0:
                return min(item_list)

        return result_price

    # 跟卖数(如无存1)
    def _to_sell(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        xpath_list = [
            '//*[text()="Other Sellers on Amazon"]/../../../../..',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?from.*?</', re.S),
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?new.*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                if result.isdigit():
                    return int(result)
            else:
                xpath_list = [
                    '//*[@id="mbc"]//a[contains(@id, "a-autoid")]',
                ]
                result_list = GoodsParser.get_new_data(xpath_list=xpath_list, html_code=result_html)
                if len(result_list) > 0:
                    if len(result_list) == 1:
                        result = 2
                    else:
                        result = len(result_list)
                    return result
        xpath_list = [
            '//*[@id="olp_feature_div"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?from.*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                if result.isdigit():
                    return int(result)
        xpath_list = [
            '//*[@id="olpDiv"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?from.*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                if result.isdigit():
                    return int(result)
        xpath_list = [
            '//*[@id="mbc"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?from.*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                if result.isdigit():
                    return int(result)
        xpath_list = [
            '//*[@id="toggleBuyBox"]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            result_xpath = result_list[0]
            result_html = tostring(result_xpath)
            pattern_list = [
                re.compile('<a.*?condition.*?>.*?([\d,]+).*?new.*?</', re.S),
            ]
            result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=result_html)
            if len(result_list) > 0:
                result = result_list[0].strip().lstrip()
                if result.isdigit():
                    return int(result)
        xpath_list = [
            '//*[@id="mbc"]//a[contains(@id, "a-autoid")]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            if len(result_list) == 1:
                result = 2
            else:
                result = len(result_list)
            return result
        return -1

    # 是否id="SalesRank"（某些商品销量例外）
    def is_SalesRank(self, html_code):
        SalesRank_pattern = [
            re.compile('id="SalesRank"', re.S),
        ]
        SalesRank_list = GoodsParser.get_new_data(pattern_list=SalesRank_pattern, html_code=html_code)
        if SalesRank_list:
            return True
        else:
            return False

    # 是否销量第一
    def _is_best_seller_1(self, bsrRank, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if bsrRank == 1:
            return 1
        else:
            return 0

    # 是否有黄金购物车
    def _has_buy_button(self, html_code=None):
        '''有黄金购物车页面,有title="Add to Shopping Cart"的a或者input标签, 没有黄金购物车的页面,没有这个标签'''
        if html_code is None:
            html_code = self.html_code
        result = 0
        title = content = ''
        button_title_xpath = [
            '//a[@title="Add to Shopping Cart"]/text()',
        ]
        xpath_list = [
            '//input[@title="Add to Shopping Cart"]/@value',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=button_title_xpath, xpath_obj=self.xpath_obj)
        button_content = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            title = result_list[0]
            title = GoodsParser.filter_str(title)
            # print(1, 'buy_button: ', title)
        if len(button_content) > 0:
            # print(1, 'buy_button: ', button_content)
            content = button_content[0]
            content = GoodsParser.filter_str(content)
            # print(2, 'buy_button: ', content)
        if 'Add to Cart' in title or 'Add to Cart' in content:
            return 1
        else:
            xpath_list = [
                '//*[@id="add-to-cart-button"]'
            ]
            result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
            if len(result_list) > 0:
                return 1
            else:
                pattern_list = [
                    re.compile('Add to Cart'),
                    re.compile('Add to Cart', re.S),
                ]
                result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=html_code)
                if len(result_list) > 0:
                    return 1
        return result

    def _has_try_prime(self):
        'Try Prime'
        pattern_list = [
            re.compile('Try Prime free for 30 days'),
            re.compile('<a id="pe-bb-signup-button-announce".*?Try Prime.*?</', re.S),
        ]
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=self.html_code)
        # print('condition1: ', result_list)
        if len(result_list) > 0:
            result = 1
        else:
            result = 0
        return result

    # 问答数
    def _get_qa_count(self, html_code=None):
        '''
        <span id="acrCustomerReviewText" class="a-size-base">397 customer reviews</span>
        <span class="a-size-base">24 answered questions</span>
        '''
        result = 0
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        qa_xpath = [
            '//a[@id="askATFLink"]/span/text()',
            '//*[@id="askATFLink"]/span/text()',
        ]
        qa_count = GoodsParser.get_new_data(xpath_list=qa_xpath, xpath_obj=self.xpath_obj)
        if len(qa_count) > 0:
            qa_count = qa_count[0]
            qa_count = GoodsParser.filter_str(qa_count)
            qa_count = qa_count.split(' ')
            if len(qa_count) > 0:
                qa_count = qa_count[0]
                if ',' in qa_count:
                    qa_count = ''.join(qa_count.split(','))
                if qa_count.isdigit():
                    result = int(qa_count)
                    # print(type(qa_count))
                    return result
        return result

    # 评论数
    def _get_review_count(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        pattern_list = [
            re.compile('here are no customer reviews yet.'),
        ]
        result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=self.html_code)
        if len(result_list) > 0:
            result1 = 0
            return int(result1)
        review_xpath = [
            '//div[@id="reviewSummary"]//span[@data-hook="total-review-count"]/text()',
            '//*[@id="reviewSummary"]//span[@data-hook="total-review-count"]/text()',
        ]
        review = GoodsParser.get_new_data(xpath_list=review_xpath, xpath_obj=self.xpath_obj)
        if len(review) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[id="reviewSummary"]')
            # print(table)
            if len(table) > 0:
                html_code = str(table[0])
                review = GoodsParser.get_new_data(xpath_list=review_xpath, html_code=html_code)

        if len(review) > 0:
            review = review[0]
            review = ''.join(review.split(','))
            if review.isdigit():
                return int(review)
        return -1

    # 综合评分
    def _get_review_rating(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        result = 0
        rating_xpath = [
            '//div[@id="reviewSummary"]//*[@data-hook="rating-out-of-text"]/text()',
            '//*[@data-hook="rating-out-of-text"]/text()',
            '//span[@id="acrPopover"]/@title',
            '//*[@id="acrPopover"]/@title',

        ]
        rating = GoodsParser.get_new_data(xpath_list=rating_xpath, xpath_obj=self.xpath_obj)
        if len(rating) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[id="reviewSummary"]')
            # print(table)
            if len(table) > 0:
                html = str(table[0])
                rating = GoodsParser.get_new_data(xpath_list=rating_xpath, html_code=html)

        if len(rating) > 0:
            rating = rating[0].strip().lstrip()
            # print(0.0, rating)
            rating = rating.split(' ')
            if len(rating) > 0:
                rating = rating[0]
                # print(1.0, rating)
                if '.' in rating and rating.split('.')[0].isdigit():
                    # print(rating, type(rating))
                    return float(rating) * 10
        pattern_list = [
            re.compile('<span data-hook="rating-out-of-text".*?>([\d\.]+) out of 5 stars</span>', re.S),
        ]
        result_list = GoodsParser.get_new_data(pattern_list=pattern_list, html_code=self.html_code)
        if len(result_list) > 0:
            result1 = result_list[0]
            return float(result1) * 10
        return result

    # 5星评价百分比
    def _get_review_5_percent(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        percent_xpath = [
            '//div[@class="a-meter 5star"]/@aria-label',
        ]
        percent = GoodsParser.get_new_data(xpath_list=percent_xpath, xpath_obj=self.xpath_obj)
        print('_get_review_5_percent 1', percent)
        if len(percent) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[class="a-meter 5star"]')
            if len(table) > 0:
                html_code = str(table[0])
                percent = GoodsParser.get_new_data(xpath_list=percent_xpath, html_code=html_code)
        print('_get_review_5_percent 2', percent)
        if len(percent) > 0:
            percent = percent[0]
            percent = GoodsParser.filter_str(percent)
            percent = GoodsParser.percent_convert(percent)
            return percent
        return result

    # 4星评价百分比
    def _get_review_4_percent(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        percent_xpath = [
            '//div[@class="a-meter 4star"]/@aria-label',
        ]
        percent = GoodsParser.get_new_data(xpath_list=percent_xpath, xpath_obj=self.xpath_obj)
        print('_get_review_4_percent 1', percent)
        if len(percent) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[class="a-meter 4star"]')
            if len(table) > 0:
                html_code = str(table[0])
                percent = GoodsParser.get_new_data(xpath_list=percent_xpath, html_code=html_code)
        print('_get_review_4_percent 2', percent)
        if len(percent) > 0:
            percent = percent[0]
            percent = GoodsParser.filter_str(percent)
            percent = GoodsParser.percent_convert(percent)
            return percent
        return result

    # 3星评价百分比
    def _get_review_3_percent(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        percent_xpath = [
            '//div[@class="a-meter 3star"]/@aria-label',
        ]
        percent = GoodsParser.get_new_data(xpath_list=percent_xpath, xpath_obj=self.xpath_obj)
        print('_get_review_3_percent 1', percent)
        if len(percent) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[class="a-meter 3star"]')
            if len(table) > 0:
                html_code = str(table[0])
                percent = GoodsParser.get_new_data(xpath_list=percent_xpath, html_code=html_code)
        print('_get_review_3_percent 2', percent)
        if len(percent) > 0:
            percent = percent[0]
            percent = GoodsParser.filter_str(percent)
            percent = GoodsParser.percent_convert(percent)
            return percent
        return result

    # 2星评价百分比
    def _get_review_2_percent(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        percent_xpath = [
            '//div[@class="a-meter 2star"]/@aria-label',
        ]
        percent = GoodsParser.get_new_data(xpath_list=percent_xpath, xpath_obj=self.xpath_obj)
        print('_get_review_2_percent 1', percent)
        if len(percent) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[class="a-meter 2star"]')
            if len(table) > 0:
                html_code = str(table[0])
                percent = GoodsParser.get_new_data(xpath_list=percent_xpath, html_code=html_code)
        print('_get_review_2_percent 2', percent)
        if len(percent) > 0:
            percent = percent[0]
            percent = GoodsParser.filter_str(percent)
            percent = GoodsParser.percent_convert(percent)
            return percent
        return result

    # 1星评价百分比
    def _get_review_1_percent(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        percent_xpath = [
            '//div[@class="a-meter 1star"]/@aria-label',
        ]
        percent = GoodsParser.get_new_data(xpath_list=percent_xpath, xpath_obj=self.xpath_obj)
        print('_get_review_1_percent 1', percent)
        if len(percent) < 1:
            soup = BeautifulSoup(html_code, 'lxml')
            table = soup.select('div[class="a-meter 1star"]')
            if len(table) > 0:
                html_code = str(table[0])
                percent = GoodsParser.get_new_data(xpath_list=percent_xpath, html_code=html_code)
        print('_get_review_1_percent 2', percent)
        if len(percent) > 0:
            percent = percent[0]
            percent = GoodsParser.filter_str(percent)
            percent = GoodsParser.percent_convert(percent)
            return percent
        return result

    # 商品说明
    def _get_feature(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        result = ''
        feature_xpath = [
            '//div[@id="feature-bullets"]/ul[@class="a-unordered-list a-vertical a-spacing-none"]/li/span/text()',
            '//*[@id="feature-bullets"]/ul[@class="a-unordered-list a-vertical a-spacing-none"]/li/span/text()',
            '//div[@id="feature-bullets"]/ul/li/span/text()',
            '//*[@id="feature-bullets"]/ul/li/span/text()',
            '//*[@id="fbExpandableSectionContent"]/ul//text()',
            '//*[@id="productDescription"]/p/text()',
            '//*[@id="bookDesc_iframe"]/p/b/text()',
            '//div[contains(@id, "feature")]//span[contains(@id, "shortDescription")]/text()',
            '//div[@data-automation-id="synopsis"]//text()',
            '//div[@id="mas-atf-app-permissions"]//text()',
        ]
        feature = GoodsParser.get_new_data(xpath_list=feature_xpath, xpath_obj=self.xpath_obj)
        if len(feature) > 0:
            item_list = []
            for item in feature:
                # print('feature item: ', item)
                item = item.lstrip().strip()
                if item:
                    item_list.append(item)
            # print('item_list: ', item_list)
            if item_list:
                result = '\n'.join(item_list).strip()
        else:
            feature_xpath = [
                '//div[@id="bookDescription_feature_div"]/noscript',
            ]
            feature = GoodsParser.get_new_data(xpath_list=feature_xpath, xpath_obj=self.xpath_obj)
            if len(feature) > 0:
                html = str(tostring(feature[0]), encoding='utf-8')
                print(html)
                xpath_list = [
                    '//div/p//text()',
                    '//div//text()',
                ]
                feature = self.get_new_data(xpath_list=xpath_list, html_code=html)
                if len(feature) > 0:
                    item_list = []
                    for item in feature:
                        item = item.strip().lstrip()
                        item_list.append(item)
                    if len(item_list) > 0:
                        result = ' '.join(item_list)

        return result

    # 发布日期
    def _get_release_date(self, html_code=None):
        '''June 20, 2017 日期要进行换算，并转换成int型'''
        date_time = 0
        if html_code is None:
            html_code = self.html_code
        date_pattern = re.compile('[A-Za-z]+ \d+, \d{4}')
        xpath_list = [
            '//*[contains(text(), "Date First Available")]/..',
            '//*[contains(text(), "Date first listed on Amazon")]/..',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            for item in result_list:
                if item:
                    html = str(tostring(item), encoding='utf-8')
                    # print(html, type(html))
                    datestr = date_pattern.search(html)
                    if datestr:
                        date1 = datestr.group(0).lstrip().strip()
                        date_format = datetime.strptime(date1, "%B %d, %Y")
                        if not date_format:
                            date_format = datetime.strptime(date1, "%b %d, %Y")
                        date_time = int(date_format.strftime('%Y%m%d'))
                        return date_time

        xpath_list = [
            '//*[contains(@id, "productDetails")]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            for item in result_list:
                if item:
                    html = str(tostring(item), encoding='utf-8')
                    # print(html, type(html))
                    datestr = date_pattern.search(html)
                    if datestr:
                        date1 = datestr.group(0).lstrip().strip()
                        date_format = datetime.strptime(date1, "%B %d, %Y")
                        if not date_format:
                            date_format = datetime.strptime(date1, "%b %d, %Y")
                        date_time = int(date_format.strftime('%Y%m%d'))
                        return date_time

        xpath_list = [
            '//*[contains(@id, "detail-bullets")]',
        ]
        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            for item in result_list:
                if item:
                    html = str(tostring(item), encoding='utf-8')
                    # print(html, type(html))
                    datestr = date_pattern.search(html)
                    if datestr:
                        date1 = datestr.group(0).lstrip().strip()
                        date_format = datetime.strptime(date1, "%B %d, %Y")
                        if not date_format:
                            date_format = datetime.strptime(date1, "%b %d, %Y")
                        date_time = int(date_format.strftime('%Y%m%d'))
                        return date_time
        return date_time

    def _get_variant(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if self.head_html:
            html_code = self.head_html
        color = ''
        size = ''
        style = ''
        xpath_list = [
            '//*[contains(@id, "color")]//*[contains(text(), "Colors:")]/..//text()',
            '//*[contains(@id, "color")]//*[contains(text(), "Color:")]/..//text()',
        ]

        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            item_list = []
            for item in result_list:
                item = item.strip().lstrip()
                if item:
                    item_list.append(item)
            if len(item_list) > 0:
                color = ''.join(item_list)
        xpath_list = [
            '//*[contains(@id, "size")]//*[contains(text(), "Sizes:")]/..//text()',
            '//*[contains(@id, "size")]//*[contains(text(), "Size:")]/..//text()',
        ]

        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            item_list = []
            for item in result_list:
                item = item.strip().lstrip()
                if item:
                    item_list.append(item)
            if len(item_list) > 0:
                size = ''.join(item_list)

        xpath_list = [
            '//*[contains(@id, "style")]//*[contains(text(), "Styles:")]/..//text()',
            '//*[contains(@id, "style")]//*[contains(text(), "style:")]/..//text()',
        ]

        result_list = GoodsParser.get_new_data(xpath_list=xpath_list, xpath_obj=self.xpath_obj)
        if len(result_list) > 0:
            item_list = []
            for item in result_list:
                item = item.strip().lstrip()
                if item:
                    item_list.append(item)
            if len(item_list) > 0:
                style = ''.join(item_list)
        result = color + " " + size + " " + style
        return result

    # 百分数换算
    @staticmethod
    def percent_convert(percent_str=''):
        float_num = 0
        if percent_str.endswith('%'):
            num = percent_str.split('%')[0]
            if num.isdigit():
                float_num = int(num)  # / 100
                # print(float_num)
        return float_num

    @staticmethod
    def has_son_goods(html_code):
        '''
        :param html_code: string
        :return: has son return son_asin_json "{'B01M13AYYA': ['10-Piece'], 'B01GBT9NJC': ['5-Piece']}"
        '''
        patterns = [
            re.compile('dimensionValuesDisplayData".*?:(.*?)"prioritizeReqPrefetch', re.S),
            # re.compile('dimensionValuesDisplayData" :(.*?)"prioritizeReqPrefetch', re.S),
        ]
        son_goods_list = GoodsParser.get_new_data(html_code=html_code, pattern_list=patterns)
        # print(1, 'son', type(son_goods_list), son_goods_list)
        if son_goods_list is None:
            return False
        else:
            son_goods_list = ''.join(son_goods_list).strip()
            # print(2, 'son', type(son_goods_list), son_goods_list)
            if son_goods_list.endswith(','):
                son_goods_list = son_goods_list.rstrip(',')
                # print(3, 'son', type(son_goods_list), son_goods_list)
            son_asin_json = demjson.decode(son_goods_list) if son_goods_list else None
            # print(4, 'son', type(son_goods_list), son_asin_json)
            return son_asin_json

    # 获取商品详情页分类信息的方法
    def get_category(self, html_code=None):
        if not html_code:
            html_code = self.html_code
        # 获取详情页商品分类的xpath
        category = ''
        xpath_list = ['//ul[@class="a-unordered-list a-horizontal a-size-small"]//span[@class="a-list-item"]/a/text()',]
        # 获取分类信息的数据
        result_list = GoodsParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        # 新列表保存提取后的分类信息
        if len(result_list) > 0:
            category = result_list[0].strip().lstrip()
        # 返回第一个大分类的信息
        return category


if __name__ == '__main__':
    from pprint import pprint

    # 导入测试HTML代码
    from tests.goods_html1 import goods_html1

    from tests.goods_html2 import goods_html2
    from tests.goods_html3 import goods_html3
    from tests.goods_html4 import goods_html4
    # from tests.goods_html5 import goods_html5
    # from tests.goods_html6 import goods_html6
    # from tests.goods_html7 import goods_html7
    # from tests.goods_html8 import goods_html8
    # from tests.goods_html9 import goods_html9
    # from tests.goods_html10 import goods_html10
    # from tests.goods_html11 import goods_html11
    # from tests.quantity_html1 import quantity_html1
    # from tests.quantity_html2 import quantity_html2
    # from tests.quantity_html3 import quantity_html3

    time_now = lambda: time.time()
    time1 = time_now()
    html = goods_html1
    html = goods_html2
    html = goods_html3
    html = goods_html4
    # html = goods_html5
    # html = goods_html6
    # html = goods_html7
    # html = goods_html8
    # html = goods_html9
    # html = goods_html10
    # html = goods_html11
    # html = quantity_html1
    # html = quantity_html2
    # html = quantity_html3

    self = GoodsParser()
    # self.get_urltitle('B000PQJW12', html)
    # print(self._get_release_date(html))
    # print(self._get_variant(html))
    # print(self._parser_quantity(html))
    # print(self._get_post_data(html))
    # print(self._is_Home_Business_Services(html))

    pprint(self.parser_goods(html, 'B00R1J3RNA', ''))
    # print(self.parser_goods(html, 'B07BDRTHX7', ''))
    # self.parser_goods('www', html)
    # print(self._get_title(html), '\n')
    # print(self._get_image_group(html), '\n')
    # print(self._get_image_more(self._get_image_group(html)), '\n')
    # print(self._get_ima_more(html), '\n')
    # print(self._get_image(html), '\n')
    # print(1.1, self._get_brand(html), '\n')
    # print(self._get_current_asin(html), '\n')
    # print(self._get_parent_asin(html), '\n')
    # print(self._get_seller_id(html), '\n')
    print(self._get_seller_name(html), '\n')
    # print(self._get_discount_price(html), '\n')
    # print(self._get_original_price(html), '\n')
    # print(self._get_cart_price(html), '\n')

    # print(self._to_price(html), '\n')
    # print(self._to_sell(html), '\n')
    # print(self._is_best_seller_1(2, html), '\n')
    print(self._has_buy_button(html), '\n')
    # print(self._get_bsrRank(html), '\n')
    # print(self.is_SalesRank(html), '\n')
    # print(self._get_qa_count(html), '\n')
    # print(self._get_review_count(html), '\n')
    # print(self._get_review_rating(html), '\n')
    # print(self._get_review_5_percent(html), '\n')
    # print(self._get_review_4_percent(html), '\n')
    # print(self._get_review_3_percent(html), '\n')
    # print(self._get_review_2_percent(html), '\n')
    # print(self._get_review_1_percent(html), '\n')
    # print(self._get_feature(html), '\n')
    # HtmlParser.has_son_goods(html)

    print(time_now() - time1)
