#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
import re
import time
from lxml import etree
from lxml.html import tostring

from Crawler.BaseParser import BaseParser
from Crawler.goodsParser import GoodsParser
from utils.util import return_PST
# from Crawler.keywordParser import KwParser
from utils.decorator import timer


class TosellParser(BaseParser):
    def __init__(self):
        self.url = None
        self.html_code = None

    # 解析跟卖详情
    @timer
    def tosell_parser(self, html_code_list, the_asin, tosellSum=None, ip='', download_url='', goods_html_code=''):
        fba_list = []
        sn_list = []
        plow_list = []
        plow_dict = {}
        tosell_list = []
        tosell_info = {}
        the_sname, the_seller_id = self._get_byb_merchant(goods_html_code)
        print(the_sname, the_seller_id)
        ts_price = self.get_to_sell_price(goods_html_code)
        print(ts_price)
        for html_code in html_code_list:
            xpathObj_list = self.get_tosell_html(html_code)
            print('xpathObj_list: ', xpathObj_list)
            for xpathObj in xpathObj_list:
                self.html_code = str(tostring(xpathObj), encoding='utf-8')
                # print(self.html_code)
                condition = self._get_condition()
                sname = self._get_sname()
                stype = self._get_stype()
                price = self._get_price()
                demo = self._get_demo()
                positive = self._get_positive(demo)
                total_ratings = self._get_total_ratings(demo)
                reivew_count = self._get_reivew_count(demo)
                seller_id = self._get_seller_id()
                if not sname:
                    seller_id = ''
                fba = self._get_fba()
                delivery = self._get_delivery()
                tosell_dict = dict(
                    asin=the_asin,
                    condition=condition,  # 使用情况
                    sname=sname,  # 卖家
                    stype=stype,  # 货运类型
                    price=price,  # 价格
                    demo=demo,  # 描述
                    positive=positive,  # 好评率
                    total_ratings=total_ratings,  # 总评数量
                    tm=int(BaseParser.get_redis_time()/1000),  # 查询时间
                    fba=fba,  # 是否fba
                    seller_id=seller_id,  # 卖家id
                    reivew_count=reivew_count,  # 评分
                    delivery=delivery,          # 配送方式
                    aday=return_PST().strftime("%Y%m%d"),  # 获取数据的太平洋日期
                )
                if fba:
                    if seller_id:
                        fba_list.append(str(seller_id))
                    else:
                        fba_list.append(str(sname))
                # if seller_id:
                #     sn_list.append(str(seller_id))
                # else:
                #     sn_list.append(str(sname))
                plow_list.append(price)
                price_str = str(price)
                if price_str not in plow_dict:
                    plow_dict[price_str] = dict(sname=sname, seller_id=seller_id)
                tosell_list.append(tosell_dict)
        sn = len(tosell_list)
        # print('\ntosellSum: ', tosellSum)
        # print('sn: ', sn, '\n')
        fba_sn = len(fba_list)      # fbag跟卖数
        if len(plow_list) > 0:
            plow = min(plow_list)
        else:
            plow = 0
        if ts_price > 0 and ts_price - plow > ts_price * 0.5:
            plow = ts_price
        plows1 = plow_dict.get(str(plow)) or {}
        plows = plows1.get('sname') or ''
        plows_id = plows1.get('seller_id') or ''

        tosell_datas = dict(
            asin=the_asin,
            sn=sn,  # 跟卖卖家数量
            fba_sn=fba_sn,  # FBA跟卖卖家数量
            plow=plow,  # 最低价
            plows=plows,  # 最低跟卖卖家名
            plows_id=plows_id,  # 最低跟卖卖家id
            getinfo_tm=int(BaseParser.get_redis_time()),  # 获取时间
            sname=the_sname,          # 黄金购物车卖家
            seller_id=the_seller_id,  # 黄金购物车卖家id
        )

        if len(tosell_list) > 0:
            tosell_info[the_asin] = (tosell_datas, tosell_list)
        else:
            tosell_info = TosellNotFoundParser(goods_html_code).parser_not_found(the_asin, goods_html_code, html_code_list)
        print(tosell_info)
        return tosell_info

    @staticmethod
    # 跟卖数(如无存0)
    def get_to_sell_sum(html_code=None):
        return GoodsParser(html_code)._to_sell(html_code)

    @staticmethod
    # 最低跟卖价(如无存0)
    def get_to_sell_price(html_code=None):
        return GoodsParser(html_code)._to_price(html_code)

    @staticmethod
    def get_tosell_html(html_code):
        tosell_html = []
        xpath_list = [
            '//*[@id="olpOfferList"]//div[@aria-label="More buying choices"]/div[@class="a-row a-spacing-mini olpOffer"]',
        ]
        result_list = TosellParser.get_new_data(xpath_list=xpath_list, html_code=html_code)
        if len(result_list) > 0:
            tosell_html = result_list
        return tosell_html

    #　获取黄金购物车卖家
    def _get_byb_merchant(self, html_code=None):
        if html_code is None:
            return '', ''
        parser = GoodsParser(html_code)
        sname = parser._get_seller_name()
        seller_id = parser._get_seller_id()
        print('_get_byb_merchant.sname', sname)
        print('_get_byb_merchant.seller_id', seller_id)
        if not sname:
            seller_id = ''
        return sname, seller_id

    def _get_fba(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        xpath_list = [
            '//*[contains(text(), "Fulfillment by Amazon")]',
        ]
        result_list = self.get_new_data(xpath_list=xpath_list, html_code=html_code)
        # print('condition1: ', result_list)
        if len(result_list) > 0:
            result = 1
        return result

    def _get_condition(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''
        condition_xpath = [
            '//div[@class="a-column a-span3 olpConditionColumn"]//span[@class="a-size-medium olpCondition a-text-bold"]/text()',
            '//div[@class="a-column a-span3 olpConditionColumn"]//span/text()',
            '//span[@a-size-medium olpCondition a-text-bold]/text()',
        ]
        result_list = self.get_new_data(xpath_list=condition_xpath, html_code=html_code)
        if len(result_list) > 0:
            item = result_list[0].strip().lstrip()
            item = ''.join(item.split('\\n')).strip('\\n').strip().lstrip()
            # print('condition1: ', item)
            if '-' in item:
                item_list = []
                items = item.split('-')
                for item in items:
                    item = item.strip().lstrip()
                    # print('condition2: ', item)
                    item_list.append(item)
                item = '-'.join(item_list)
            result = item
        # print('condition3: ', result)
        return result

    # 抓取跟卖卖家
    def _get_sname(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 'none'
        pattern_list = [
            re.compile('>from seller (\w+.*?) and.*?<', re.S),
        ]
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=html_code)
        # print('sname1: ', result_list)
        if len(result_list) > 0:
            sname = result_list[0].strip().lstrip()
            # print('sname2: ', sname)
            if sname and type(sname) is str:
                result = sname
            else:
                result = ''
        else:
            xpath_list = [
                '//h3[@class="a-spacing-none olpSellerName"]/span/a/text() | //h3[@class="a-spacing-none olpSellerName"]/img/@alt',
                '//h3[@class="a-spacing-none olpSellerName"]/img/@alt | //h3[@class="a-spacing-none olpSellerName"]/img/@src',
                '//h3[@class="a-spacing-none olpSellerName"]//text()',
            ]
            result_list = self.get_new_data(xpath_list=xpath_list, html_code=html_code)
            if result_list:
                item_list = []
                for item in result_list:
                    item = ''.join(item.split('\\n')).strip('\\n').strip().lstrip()
                    if item:
                        item_list.append(item)
                if item_list:
                    sname = ''.join(item_list)
                    if sname and type(sname) is str:
                        result = sname
                    else:
                        result = ''
        return result

    # 抓取货运类型
    def _get_stype(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''
        '''
        <span class="a-color-secondary">




                &amp; <b>FREE Shipping</b> on orders over $25.00 shipped by Amazon. <a href="/gp/help/customer/display.html/ref=mk_gship_olp?ie=UTF8&amp;nodeId=527692&amp;pop-up=1" target="SuperSaverShipping" onclick="return amz_js_PopWin('/gp/help/customer/display.html/ref=mk_gship_olp?ie=UTF8&amp;nodeId=527692&amp;pop-up=1','SuperSaverShipping','width=550,height=550,resizable=1,scrollbars=1,toolbar=0,status=0');">Details</a>

        </span>
        '''

        pattern_list = [
            re.compile('<.*?olpShippingPrice.*?>(\$\d+.+?)<.*?<.*?olpShippingPriceText.*?>(shipping)</span>', re.S),
            re.compile('>(FREE Shipping)<.*?(on orders.*?by.*?n)\..*?<a', re.S),
            re.compile('>(FREE Shipping)<', re.S),
        ]
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=html_code)
        # print('sname1: ', result_list)
        if len(result_list) > 0:
            if type(result_list[0]) is str:
                sname = result_list[0].strip().lstrip()
                # print('sname2: ', sname)
                result = sname
            elif type(result_list[0]) is tuple:
                result = ' '.join(result_list[0])

        else:
            stype_xpath = [
                '//span[@class="a-color-secondary"]//text()'
            ]
            stype = self.get_new_data(xpath_list=stype_xpath, html_code=html_code)
            # print('stype1: ', stype)
            if len(stype) > 0:
                stype_list = []
                for item in stype:
                    item = ''.join(''.join(''.join(''.join(item.split('\\n')).split('&')).split('+')))
                    stype = item.strip().lstrip()
                    # print('stype2: ', stype)
                    if stype:
                        stype = ''.join(stype.split('Details'))
                        stype_list.append(stype)
                if len(stype_list) > 1:
                    print(stype_list)
                    result = ' '.join(stype_list).strip().lstrip()

        return result

    # 抓取价格
    def _get_price(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        pattern_list = [
            re.compile('>.*?price \$([0-9,\.]+)<', re.S),
            re.compile('price.*?([0-9,\.]+)', re.S),
        ]
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=html_code)
        print('result_list1: ', result_list)
        if len(result_list) > 0:
            price = result_list[0].strip().lstrip()
            print(price)
            price = ''.join(''.join(price.split('.')).split(','))
            if price.isdigit():
                result = int(price)
        return result

    # 商品描述
    def _get_demo(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''
        xpath_list = [
            '//div[@class="a-column a-span2 olpSellerColumn"]/p//text()',
        ]
        # result_list = KwParser.get_data_from_xpthObj(xpathObj, xpath_list)
        result_list = self.get_new_data(html_code=html_code, xpath_list=xpath_list)
        # print('demo1: ', result_list)
        if len(result_list) > 0:
            demos_list = []
            for item in result_list:
                item = ''.join(item.split('\\n')).strip('\\n').lstrip('').strip().lstrip()
                # print(item)
                if item:
                    demos_list.append(item)

            if demos_list:
                result = ' '.join(demos_list)
        return result

    # 好评率
    def _get_positive(self, demo, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if not demo:
            demo = ''
        result = 0
        pattern_list = [
            re.compile('(\d+)\%'),
        ]

        positive = self.get_new_data(html_code=demo, pattern_list=pattern_list)
        if positive:
            result1 = positive[0].strip().lstrip()
            result1 = ''.join(result1.split('%')[0]).lstrip().strip()
            print(result1)
            if result1.isdigit():
                result = int(result1)
        else:
            positive = demo.split('%')
            if type(positive) is list:
                positive = positive[0].split(' ')
                if type(positive) is list:
                    positive = positive[-1]
                    # print(positive)
                    if positive.isdigit():
                        result = int(positive)
            else:
                xpath_list = [
                    '//div[@class="a-column a-span2 olpSellerColumn"]/p/a/b/text()',
                    '//div[@class="a-column a-span2 olpSellerColumn"]/p//b/text()',
                ]
                result_list = self.get_new_data(html_code=html_code, xpath_list=xpath_list)
                if result_list:
                    positive = result_list[0].strip().lstrip()
                    if '%' in positive:
                        positive = demo.split('%')[0]
                        if positive.isdigit():
                            result = int(positive)

        return result

    # 总评数
    def _get_total_ratings(self, demo, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if not demo:
            demo = ''
        result = 0
        pattern_list = [
            re.compile('([\d,]+) total'),
        ]
        result_list = self.get_new_data(html_code=demo, pattern_list=pattern_list)
        if result_list:
            total = result_list[0].strip().lstrip()
            total = ''.join(total.split(','))
            if total.isdigit():
                result = int(total)
        return result

    # 评分
    def _get_reivew_count(self, demo, html_code=None):
        if html_code is None:
            html_code = self.html_code
        if not demo:
            demo = ''
        result = 0
        # print('\nget rrg')
        result = 0
        # print('rrg_resultsObj: ', resultsObj)
        pattern_list = [
            re.compile('([\d\.]+) out of 5 stars.*', re.S),
        ]
        # print('rrg_xpath: ',rrg_xpath)
        result_list = self.get_new_data(html_code=demo, pattern_list=pattern_list)
        # print('rrg1: ', rrg)
        if len(result_list) > 0:
            rrg1 = result_list[0].strip().lstrip()
            rrg = ''.join(rrg1.split('.'))
            if rrg.isdigit():
                if len(rrg) == 1:
                    rrg = rrg + '0'
                # print('rrg2: ', rrg, type(rrg))
                result = int(rrg)
                # print('num1: ', num, type(num))
        return result

    # 商家id
    def _get_seller_id(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''

        xpath_list = [
            '//div[@class="a-column a-span2 olpSellerColumn"]/h3/span/a/@href',
            '//h3/span/a/@href',
            '//div[@class="a-column a-span2 olpSellerColumn"]/p/a/@href',
            '//a[contains(@href, "seller=")]/@href'
        ]
        seller_url = self.get_new_data(xpath_list=xpath_list, html_code=html_code)
        # print('sname1: ', seller_url)
        if len(seller_url) > 0:
            seller_id_html = seller_url[0]
            print(seller_id_html)
            pattern = re.compile('seller=([A-Z0-9a-z]+)')
            sller_list = pattern.findall(seller_id_html)
            if sller_list:
                result = sller_list[0]
        print(result)
        return result

    # 配送方式
    def _get_delivery(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = ''
        pattern_list = [
            re.compile('Fulfillment by Amazon', re.S),
            re.compile('>.*?([Ss]hips from[ A-Z,]+[\w ]+)\..*?<', re.S),
        ]
        result_list = self.get_new_data(html_code=html_code, pattern_list=pattern_list)
        if len(result_list) > 0:
            result = result_list[0].strip().lstrip()
        return result


class TosellNotFoundParser(GoodsParser):
    def __init__(self, html_code):
        super(TosellNotFoundParser, self).__init__()
        self.html_code = html_code
        self.xpath_obj = etree.HTML(html_code) if html_code else None
        self.head_html = self.get_head_html(html_code)
        self.desc_html = self.get_description_html(html_code)
        self.buy_box_html = self.get_buy_box_html(html_code)

    def _get_fba(self):
        pattern_list = [
            re.compile('Fulfilled by Amazon'),
            re.compile('Fulfilled by Amazon', re.S),
        ]
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=self.html_code)
        # print('condition1: ', result_list)
        if len(result_list) > 0:
            result = 1
        else:
            result = 0
        return result

    @timer
    def parser_not_found(self, the_asin, goods_html, html_code_list=None):
        self.html_code = goods_html
        self.head_html = self.get_head_html(goods_html)
        self.xpath_obj = etree.HTML(goods_html)
        self.desc_html = self.get_description_html(goods_html)
        self.buy_box_html = self.get_buy_box_html(goods_html)
        tosell_list = []
        tosell_info = {}
        sn = 1
        if self._is_Currently_unavailable():
            sn = 0
        sname = self._get_seller_name()  # 卖家
        seller_id = self._get_seller_id()
        if not sname:
            seller_id = ''
        price = self._get_discount_price()
        total_ratings = self._get_review_count()  # 评论数
        reivew_count = self._get_review_rating()  # 综合评分
        r5p = self._get_review_5_percent()  # 5星评价百分比
        r4p = self._get_review_4_percent()  # 4星评价百分比
        positive = r5p + r4p
        byb = self._has_buy_button()
        fba = self._get_fba()
        tosell_dict = dict(
            asin=the_asin,
            condition='',  # 使用情况
            sname=sname,  # 卖家
            stype='',  # 货运类型
            price=price,  # 价格
            demo='',  # 描述
            positive=positive,  # 好评率
            total_ratings=total_ratings,  # 总评数量
            tm=int(BaseParser.get_redis_time()/1000),  # 更新时间
            fba=fba,  # 是否fba
            seller_id=seller_id,  # 卖家id
            reivew_count=reivew_count,  # 评分
            delivery='',  # 配送方式
            aday=return_PST().strftime("%Y%m%d"),  # 获取数据的太平洋日期
        )

        tosell_list.append(tosell_dict)

        if fba > 0:
            fba_sn = 1
        else:
            fba_sn = 0
        if byb > 0:
            the_sname = sname
            the_seller_id = seller_id
        else:
            the_sname = ''
            the_seller_id = ''
        if not the_sname:
            the_seller_id = ''
        tosell_datas = dict(
            asin=the_asin,
            sn=sn,  # 跟卖卖家数量
            fba_sn=fba_sn,  # FBA跟卖卖家数量
            plow=price,  # 最低价
            plows=sname,  # 最低跟卖卖家名
            plows_id=seller_id,  # 最低跟卖卖家id
            getinfo_tm=int(BaseParser.get_redis_time()),  # 获取时间
            sname=the_sname,  # 黄金购物车卖家
            seller_id=the_seller_id,  # 黄金购物车卖家id
        )
        tosell_html = html_code_list[0] if type(html_code_list) is list and len(html_code_list) >0 else ''
        if re.search('There are currently no listings for this search', tosell_html):
            # 如果没有new跟卖, 则卖家数量为0, fba卖家数量为0, 价格为-, 最低跟卖卖家与卖家id为-
            tosell_datas['sn'] = 0
            tosell_datas['fba_sn'] = 0
            tosell_datas['plow'] = -1
            tosell_datas['plows'] = ''
            tosell_datas['plows_id'] = ''
            tosell_info[the_asin] = (tosell_datas, [])

        elif self._is_Currently_unavailable():
            # 如果不可售, 则卖家数量为0, fba卖家数量为0, 价格为-, 最低跟卖卖家与卖家id为-
            tosell_datas['sn'] = 0
            tosell_datas['fba_sn'] = 0
            tosell_datas['plow'] = -1
            tosell_datas['plows'] = ''
            tosell_datas['plows_id'] = ''
            tosell_datas['sname'] = ''
            tosell_datas['seller_id'] = ''
            tosell_info[the_asin] = (tosell_datas, [])
        else:
            tosell_info[the_asin] = (tosell_datas, tosell_list)
        return tosell_info


if __name__ == '__main__':
    from pprint import pprint

    # from tests.tosell_html1 import tosell_html1
    # from tests.tosell_html2 import tosell_html2
    from tests.goods_html1 import goods_html1
    # from tests.goods_html2 import goods_html2
    time_now = lambda: time.time()
    time1 = time_now()
    html1 = goods_html1
    # html1 = goods_html2
    # print(TosellNotFoundParser(html1).parser_not_found('', html1))
    self = TosellParser()
    # html = goods_html2
    # self._get_byb_merchant(html)

    # html = tosell_html1
    html = ''
    # html = tosell_html2
    print(len(html))

    # print(self.tosell_parser([html], '12131'))
    # pprint(self.tosell_parser([html], '', goods_html_code=html1))
    print(self._get_byb_merchant(html1))
    print(self.get_to_sell_sum(html1))
    print(self.get_to_sell_price(html1))
    # tosell_list = self.get_tosell_html(html)
    # print(tosell_list)
    # i = 0
    # for tosell in tosell_list:
    #     i += 1
    #     html = tostring(tosell)
    #     html = str(html, encoding='utf-8')
    #     print(html, type(html))
    #     print(i, self._get_price(html))
    #     print(i, self._get_delivery(html))
    #     demo = self._get_demo(html)
        # print(i, demo)
        # print(i, self._get_positive(demo))
        # print(i, self._get_total_ratings(demo))
        # print(i, self._get_seller_id(html))
        # print(i, self._get_fba(html))
        # print(i, self._get_sname(html))
        # print(i, self._get_stype(html))
        # print(i, self._get_condition(html))


    print(time_now() - time1)
