#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
import re
from functools import wraps
from lxml import etree
from lxml.html import tostring
import time

from Crawler.BaseParser import BaseParser
from utils.util import return_PST


# from tests.keyword_not_found import keyword_not_found


def is_page_not_match(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        not_match = False
        # print('is_page_not_match.args', args)
        for arg in args:
            if type(arg) is list:
                for item in arg:
                    if type(item) is str:
                        if re.search('did not match any products', item):
                            # print(item)
                            not_match = True

        kwargs['not_match'] = not_match
        print('is_page_not_match.kwargs', kwargs)
        data = func(*args, **kwargs)
        return data
    return wrap


class KwParser(BaseParser):
    def __init__(self):
        pass

    @is_page_not_match
    def kw_parser(self, html_code_list, keyword, cid, not_match=False):
        result_dict = {}
        # print(len(html_code))
        print('not_match', not_match)
        price_list = []
        rrg_list = []
        rc_list = []
        keyword_data_list = []
        search_num = self._get_search_num(html_code_list[0])
        print('html_code_list len: ', len(html_code_list))
        j = 0
        for html_code in html_code_list:
            j += 1
            self.html_code = html_code
            resultId = KwParser.get_results_tag(html_code)
            resultNum = len(resultId)
            # 保存html样本, 测试用
            # print('resultId len: ', resultNum)
            # file = '%s%s.html' % (keyword, j)
            # with open(file, 'w', encoding='utf-8') as f:
            #     f.write(html_code)
            i = -1
            for result in resultId:
                i += 1
                html = str(tostring(result), encoding='utf-8')
                result = etree.HTML(html)
                asin = self._get_asin(result, i)
                title = self._get_title(result, i)
                brand = self._get_brand(result, i)
                price = self._get_price(result, i)
                rrg = self._get_rrg(result, i)
                rc = self._get_rc(result, i)
                img = self._get_img(result, i)
                issp = self._get_issp(result, i)
                if asin:
                    keyword_data_dict = dict(
                        kw=keyword,  # 关键字
                        cid=cid,  # 分类id(0代表所有分类）
                        asin=asin,  # 产品
                        title=title,  # 产品标题
                        img=img,  # 产品图片
                        brand=brand,  # 品牌
                        msn=0,  # 月搜索量
                        issp=issp,  # 是否付费推广
                        srn=search_num,  # 搜索结果数
                        price=price,  # 产品价格
                        rrg=rrg,  # 产品评分
                        rc=rc,  # 产品评论数
                        special=1,  # 均分程序跑数据
                        tm=int(BaseParser.get_redis_time()),  # 获取数据的时间（毫秒级)
                        aday=return_PST().strftime("%Y%m%d"),  # 获取数据的太平洋日期
                    )
                    keyword_data_list.append(keyword_data_dict)
            print(j, '数据长度:　', len(keyword_data_list))
        i = 0
        for item in keyword_data_list:
            i += 1
            item['pr'] = i

        print(keyword, 'keyword_data_list len: ', len(keyword_data_list))
        if len(keyword_data_list) > 50:
            keyword_data_list = keyword_data_list[0: 50]
        for item in keyword_data_list:
            price = item.get('price')
            rrg = item.get('rrg')
            rc = item.get('rc')
            # 价格
            if type(price) is int and price > 0:
                price_list.append(price)
            # 评论
            if type(rc) is int and rc >= 0:
                rc_list.append(rc)
            # 评分
            if type(rrg) is int and rrg > 0:
                rrg_list.append(rrg)


        # if len(price_list) > 50:
        #     price_list = price_list[0: 50]
        # if len(rrg_list) > 50:
        #     rrg_list = rrg_list[0: 50]
        # if len(rc_list) > 50:
        #     rc_list = rc_list[0: 50]

        print('price_list: ', len(price_list), price_list)
        print('rrg: ', len(rrg_list), rrg_list)
        print('rc: ', len(rc_list), rc_list)
        price_max = self._get_price_max(price_list)
        price_min = self._get_price_min(price_list)
        price_ave = self._get_price_ave(price_list)
        # print('rrg_list: ', rrg_list)
        rrg_max = self._get_rrg_max(rrg_list)
        rrg_min = self._get_rrg_min(rrg_list)
        rrg_ave = self._get_rrg_ave(rrg_list)
        # print('rc_list: ', rc_list)
        rc_max = self._get_rc_max(rc_list)
        rc_min = self._get_rc_min(rc_list)
        rc_ave = self._get_rc_ave(rc_list)

        date = self._get_date()
        # print(date, type(date))
        if search_num < 50 and search_num < len(keyword_data_list):
            search_num = len(keyword_data_list)
            for data in keyword_data_list:
                data['srn'] = search_num
        kwData_dict = dict(
            kw=keyword,  # 关键词
            cid=cid,  # 分类id(0代表所有分类）
            mon_search=0,  # 月搜索量（废弃）
            search_num=search_num,  # 搜索结果数
            price_max=price_max,  # 最高价格
            price_min=price_min,  # 最低价格
            price_ave=price_ave,  # 平均价格
            rrg_max=rrg_max,  # 最高评分
            rrg_min=rrg_min,  # 最低评分
            rrg_ave=rrg_ave,  # 平均评分
            rc_max=rc_max,  # 最高评论数
            rc_min=rc_min,  # 最低评论数
            rc_ave=rc_ave,  # 平均评论数
            date=date,  # 采集的日期（Ymd)
            mon_search_state=0,  # 月搜索数量采集的状态
            other_state=1,  # 其它数据采集状态
            getinfo_tm=int(BaseParser.get_redis_time()),  # 获取数据的时间（毫秒级）
        )
        print(keyword, 'keyword_data_list　len1: ', len(keyword_data_list))
        if search_num > 100:
            if len(keyword_data_list) == 50:
                result_dict[keyword] = (kwData_dict, keyword_data_list)
            else:
                if not_match and len(keyword_data_list) <= 50:
                    result_dict[keyword] = (kwData_dict, keyword_data_list)

        else:
            if len(keyword_data_list) <= 50:
                result_dict[keyword] = (kwData_dict, keyword_data_list)
        if search_num == 0 and price_max == 0 and price_ave == 0 and rrg_max == 0 and rc_max == 0:
            result_dict = {}
        print(result_dict)
        return result_dict

    # 是否存在这个关键字
    @staticmethod
    def has_not_found_keyword(html_code):
        found_pattern = [
            re.compile('not match any products', re.S),
            re.compile('search.+?did not match any products', re.S),
            re.compile('found 0 results', re.S),
        ]
        found_result = KwParser.get_new_data(pattern_list=found_pattern, html_code=html_code)
        if found_result:
            return False
        else:
            return True

    # 获取搜索结果的li标签id
    @staticmethod
    def get_search_results_id(html_code):
        result = []
        results_id_pattern = [
            re.compile('id=\"(result_\d+)\"', re.S),
        ]
        results_id = KwParser.get_new_data(pattern_list=results_id_pattern, html_code=html_code)
        if len(results_id) > 0:
            for item in results_id:
                # print('item: ', item)
                if 'result' in item:
                    result.append(item)
            # print('result: ', type(result), result)
            return result
        else:
            return result

    @staticmethod
    def get_data_from_xpthObj(xpthObj, xpath_list):
        '''传入一个xpath抓取到的对象, 以及一个xpath规则列表'''
        time1 = time.time()
        result = []
        for xpath in xpath_list:
            data = []
            try:
                # print('data_from_xpthObj xpath: ', xpath)
                data = xpthObj.xpath(xpath)
            except Exception as e:
                print('xpath[%s] 提取时[%s]' % (xpath, e))
            # print(3, 'data_from_xpthObj', data, type(data), len(data))
            if len(data) > 0:
                # print('xpath: ', xpath)
                result = data
                # print(result, 5)
                time2 = time.time()
                times = '%2f' % (time2 - time1)
                # print(4, 'times: ', times)
                return result
        time2 = time.time()
        times = '%2f' % (time2 - time1)
        # print(4, 'times: ', times)
        return result

    # 抓取翻页url
    @staticmethod
    def get_search_page_url(html_code, page, Next=False):
        result = ''
        xpath_list = [
            '//*[@id="pagn"]',
        ]
        result_list = KwParser.get_new_data(html_code=html_code, xpath_list=xpath_list)
        if len(result_list) > 0:
            html = str(tostring(result_list[0]), encoding='utf-8')
            # print(type(html), html)
            # pattern_str = r'<a.*?href="(.*?page=[0-9].*?)".*?>'
            pattern_str = r'<a.*?href="(.*?sr_pg_%s.*?page=%s.*?)".*?>' % (page, page)
            if Next:
                # 抓下一页
                pattern_str = r'<a.*?Next.*?href="(.*?page=[0-9].*?)".*?>'

            # print(pattern_str)
            pattern_list = [
                re.compile(pattern_str, re.S),
            ]
            # print(pattern_list)
            result_list = KwParser.get_new_data(html_code=html, pattern_list=pattern_list)
            if len(result_list) > 0:
                url = ''.join(result_list[0].split('amp;'))
                result = 'https://www.amazon.com%s' % (url)
        return result

    # 是否付费推广
    def _get_issp(self, resultsObj, pr):
        # print('\nget asin')
        result = 0
        # print('asin_resultsObj: ', resultsObj)
        pattern_list = [
            re.compile('Sponsored', re.S),
            re.compile('sponsored', re.S),
        ]
        html_code = tostring(resultsObj)
        result_list = self.get_new_data(pattern_list=pattern_list, html_code=html_code)
        if len(result_list) > 0:
            result = 1
        return result

    def _get_asin(self, resultsObj, pr):
        # print('\nget asin')
        result = ''
        # print('asin_resultsObj: ', resultsObj)
        asin_xpath = [
            '//li[starts-with(@id, "result_")]/@data-asin',
            '//*[starts-with(@id, "result_")]/@data-asin',
        ]

        result_list = self.get_data_from_xpthObj(resultsObj, asin_xpath)
        if len(result_list) > 0:
            result = result_list[0].strip().lstrip()
        return result

    @staticmethod
    def get_results_tag(html_code):
        results_tags = []
        xpath_list = [
            '//*[starts-with(@id, "result_")]',
        ]
        result_list = KwParser.get_new_data(xpath_list=xpath_list, html_code=html_code)
        if len(result_list) > 0:
            results_tags = result_list
        return results_tags

    def _get_title(self, resultsObj, pr):
        # print('\nget title')
        result = ''
        # print('title_resultsObj: ', resultsObj)
        xpath_list = [
            '//li[starts-with(@id, "result_")]//h2[@class="a-size-medium s-inline s-access-title a-text-normal"]/@data-attribute',
            '//*[starts-with(@id, "result_")]//h2[@class="a-size-medium s-inline s-access-title a-text-normal"]/text()',
            '//*[starts-with(@id, "result_")]//h2[@data-attribute]/@data-attribute',
            '//*[starts-with(@id, "result_")]//h2[@data-attribute]/text()',
        ]

        result_list = self.get_data_from_xpthObj(resultsObj, xpath_list)
        if len(result_list) > 0:
            result = result_list[0].strip().lstrip()
            if len(result) > 255:
                result = result[0:247] + '...'
        return result

    def _get_img(self, resultsObj, pr):
        # print('\nget img')
        result = ''
        xpath_list = [
            '//li[starts-with(@id, "result_")]//img[@class="s-access-image cfMarker"]/@src',
            '//li[starts-with(@id, "result_")]//img[@data-search-image-load]/@src',
            '//li[starts-with(@id, "result_")]//img/@src',
        ]
        # print('img_resultsObj: ', resultsObj)
        result_list = self.get_data_from_xpthObj(resultsObj, xpath_list)
        if len(result_list) > 0:
            result = result_list[0].strip().lstrip()
        return result

    def _get_brand(self, resultsObj, pr):
        # print('\nget brand')
        # print('brand_resultsObj: ', resultsObj)
        result = ''
        html = tostring(resultsObj)
        # xpath_list = [
        #     '//*[starts-with(@id, "result_")]//div[@class="a-box-group acs_product-metadata__brand"]/span/text()',
        # ]
        # print('img_resultsObj: ', resultsObj)
        # result_list = self.get_data_from_xpthObj(resultsObj, xpath_list)
        pattern_list = [
            re.compile('>by </span><span class="a-size-small a-color-secondary">([\w -;]+)</span>', re.S),
            re.compile('>by </span><span class="a-size-small a-color-secondary"><a.*?>([\w -;]+)</a>', re.S),
            re.compile('<a.*?a-link-normal a-text-normal.*?><span.*?"a-color-secondary s-overflow-ellipsis s-size-mild">([\w -;]+)</span></a>', re.S),
            re.compile('a-color-secondary s-overflow-ellipsis s-size-mild">([\w -;]+)</span>', re.S),
            re.compile('<span .*?s-size-mild.*?>([\w -;]+)< ', re.S),
        ]
        result_list = self.get_new_data(html_code=html, pattern_list=pattern_list)
        # print(result_list)
        if len(result_list) > 0:
            item = result_list[0].lstrip().strip()
            if '&amp;' in item:
                item = '&'.join(item.split('&amp;'))
            if len(item) > 128:
                item = item.split(' ')[0]
            result = item


        return result

    def _get_pr(self, resultsObj, pr):
        # print('\nget pr')
        result = 0
        # print('asin_resultsObj: ', resultsObj)
        xpath_list = [
            '//li[starts-with(@id, "result_")]/@data-result-rank',
            '//*[starts-with(@id, "result_")]/@data-result-rank',
        ]
        result_list = self.get_data_from_xpthObj(resultsObj, xpath_list)
        if len(result_list) > 0:
            pr1 = result_list[0].strip().lstrip()
            if pr1.isdigit():
                result = int(pr1) + 1
        else:
            result = pr + 1
        return result

    # 获取价格
    def _get_price(self, resultsObj, pr):
        # print('\nget price')
        result = 0
        # print('price_resultsObj: ', resultsObj)
        # xpath_list = [
        #     '//*[starts-with(@id, "result_")]//a/span[@class="a-offscreen"]/text()',
        #     '//*[starts-with(@id, "result_")]//a/span[@class="a-offscreen xh-highlight"]/text()',
        #     '//*[starts-with(@id, "result_")]//a[@class="a-link-normal a-text-normal"]/span[1]/text()',
        #     '//*[starts-with(@id, "result_")]//a[@class="a-link-normal a-text-normal"]/span[@class="sx-price sx-price-large xh-highlight"]//text()',
        #     '//*[starts-with(@id, "result_")]//a[@class="a-link-normal a-text-normal"]/span[2]//text()',
        #     '//*[starts-with(@id, "result_")]//a[@class="a-link-normal a-text-normal"]/span[@class="a-offscreen"]/text()',
        #     '//*[starts-with(@id, "result_")]//a[@class="a-link-normal a-text-normal"]/span[@class="a-offscreen xh-highlight"]/text()',
        # ]
        # result_list = self.get_data_from_xpthObj(resultsObj, xpath_list)
        html = tostring(resultsObj)
        pattern_list = [
            re.compile('<.*?a-offscreen.*?>\$([\d,\.]+).*?<', re.S),
            re.compile('>\$([\d,\.]+).*?<', re.S),
            re.compile('>\$([\d,\.]+).*?<', re.S),
        ]
        result_list = self.get_new_data(html_code=html, pattern_list=pattern_list)
        # print('price search num: ', result_list)
        if len(result_list) > 0:
            price = result_list[0].strip().lstrip()
            result_list = ''.join(''.join(price.split('.')).split(',')).strip().lstrip()
            if result_list.isdigit():
                result = int(result_list)
            else:
                return -1
        else:
            pattern_list = [
                re.compile('price.*?>([\d,]+).*?<.*?price.*?>([0-9]{2})<', re.S),
            ]
            result_list = self.get_new_data(html_code=html, pattern_list=pattern_list)
            if len(result_list) > 0:
                price = ''.join(result_list[0]).strip().lstrip()
                if price.isdigit():
                    result = int(price)
                else:
                    return -1


        # print(result, type(result))
        return result

    # 获取评分
    def _get_rrg(self, resultsObj, pr):
        # print('\nget rrg')
        result = 0
        # print('rrg_resultsObj: ', resultsObj)
        pattern_list = [
            re.compile('>([\d\.]+) out of 5 stars<', re.S),
        ]
        # print('rrg_xpath: ',rrg_xpath)
        html = tostring(resultsObj)
        result_list = self.get_new_data(html_code=html, pattern_list=pattern_list)
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

    # 获取评论数
    def _get_rc(self, resultsObj, pr):
        # print('\nget rc')
        result = 0
        # print(html_code)
        # print('rc_resultsObj: ', resultsObj)
        html = tostring(resultsObj)
        pattern_list = [
            re.compile('<a.*?\#customerReviews.*?>([\d,]+).*?<', re.S),
            re.compile('<.*?Reviews.*?>([\d,]+).*?<', re.S),
        ]
        result_list = self.get_new_data(html_code=html, pattern_list=pattern_list)
        # print(rc)
        if len(result_list) > 0:
            rc1 = result_list[0].strip().lstrip()
            rc = ''.join(rc1.split(','))
            if rc.isdigit():
                result = int(rc)
            else:
                return -1
        # print(num, type(num))
        return result

    # 搜索结果数
    def _get_search_num(self, html_code=None):
        if html_code is None:
            html_code = self.html_code
        result = 0
        '1-24 of over 1,000 results for <span>'
        search_num_xpath = [
            '//span[@id="s-result-count"]/text()',
            '//*[@id="s-result-count"]/text()',
        ]
        search_nums = self.get_new_data(xpath_list=search_num_xpath, html_code=html_code)
        if len(search_nums) > 0:
            search_num1 = ''.join(search_nums)
            # print(search_num1)
            pattern_list = [
                re.compile('of[a-zA-Z ]*([0-9,]+) results'),
                re.compile('[a-zA-Z ]*([0-9,]+) results'),
            ]
            search_num2 = self.get_new_data(html_code=search_num1, pattern_list=pattern_list)
            if len(search_num2) > 0:
                print('searche_num2', search_num2)
                search_num3 = search_num2[0].strip().lstrip()
                result1 = ''.join(search_num3.split(','))
                print('searche_num3: ', result1)
                if result1.isdigit():
                    result = int(result1)
                else:
                    return -1
        return result

    # 最高价格
    def _get_price_max(self, price_list):
        if type(price_list) is list and len(price_list) >= 1:
            return max(price_list)
        else:
            return 0

    # 最低价格
    def _get_price_min(self, price_list):
        if type(price_list) is list and len(price_list) >= 1:
            return min(price_list)
        else:
            return 0

    # 平均价格
    def _get_price_ave(self, price_list):
        if type(price_list) is list and len(price_list) >= 1:
            ave = int(sum(price_list) / len(price_list))
            return ave
        else:
            return 0

    # 最高评分
    def _get_rrg_max(self, rrg_list):
        if type(rrg_list) is list and len(rrg_list) >= 1:
            return max(rrg_list)
        else:
            return 0

    # 最低评分
    def _get_rrg_min(self, rrg_list):
        if type(rrg_list) is list and len(rrg_list) >= 1:
            return min(rrg_list)
        else:
            return 0

    # 平均评分
    def _get_rrg_ave(self, rrg_list):
        if type(rrg_list) is list and len(rrg_list) >= 1:
            ave = int(sum(rrg_list) / len(rrg_list))
            return ave
        else:
            return 0

    # 最高评论数
    def _get_rc_max(self, rc_list):
        if type(rc_list) is list and len(rc_list) >= 1:
            return max(rc_list)
        else:
            return 0

    # 最低评论数
    def _get_rc_min(self, rc_list):
        if type(rc_list) is list and len(rc_list) >= 1:
            return min(rc_list)
        else:
            return 0

    # 平均评论数
    def _get_rc_ave(self, rc_list):
        if type(rc_list) is list and len(rc_list) >= 1:
            ave = int(sum(rc_list) / len(rc_list))
            return ave
        else:
            return 0

    # 采集日期（Ymd)
    def _get_date(self):
        return int(return_PST().strftime('%Y%m%d'))

    # 月搜索数量采集的状态
    def _get_monsearch_state(self, html_code=None):
        pass

    # 其它数据采集的状态
    def _get_other_state(self, html_code=None):
        pass


if __name__ == '__main__':
    from tests.keyword_html1 import keyword_html1
    from tests.keyword_html2 import keyword_html2
    from tests.keyword_html3 import keyword_html3
    # from tests.keyword_html5 import keyword_html5
    from pprint import pprint
    time_now = lambda: time.time()
    time1 = time_now()

    # 抓关键字测试
    # html = keyword_html1
    html = keyword_html2
    # html = keyword_html3
    # html = keyword_html5
    # html = keyword_not_found
    # print(len(html))
    self = KwParser()
    # Next = True
    # url = self.get_search_page_url(html, 2, Next=Next)
    # print(url)
    # url1 = re.sub('sr_pg_\d+\?', 'sr_pg_%s?' % (4), url)
    # url2 = re.sub('page=\d+\&', 'page=%s&' % (4), url1)
    # print(url1)
    # print(url2)
    # if self.has_not_found_keyword(html):
    #     print(self)
    pprint(self.kw_parser([html, keyword_html3], '', 0))
    # print('\n', self._get_search_num(html))
    # resultId = self.get_results_tag(html)
    # print(len(resultId))
    # i = -1
    # for result in resultId:
    #     i += 1
    #     print('\n')
    #     print(i, result)
        # print(i, tostring(result))
        # print(len(tostring(result)))
        # print(i, self._get_asin(result, i))
        # print(i, self._get_title(result, i))
        # print(i, self._get_img(result, i))
        # print(i, self._get_brand(result, i))
        # print(i, self._get_pr(result, i))
        # print(i, self._get_price(result, i))
        # print(i, self._get_rrg(result, i))
        # print(i, self._get_rc(result, i))
        # print(i, self._get_issp(result, i))



    print(time_now() - time1)
