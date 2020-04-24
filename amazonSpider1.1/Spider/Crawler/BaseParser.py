#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import re
import time
from urllib import parse
from lxml import etree
from utils.util import GetRedis
from utils.util import Logger


class BaseParser:
    @staticmethod
    def is_RobotCheck(html_code):
        RobotCheck_patterns = [
            re.compile('Robot Check', re.S),
            re.compile('Bot Check', re.S),
            re.compile('Amazon CAPTCHA', re.S),
        ]
        RobotCheck = BaseParser.get_new_data(pattern_list=RobotCheck_patterns, html_code=html_code)
        if len(RobotCheck) > 0:
            return True
        return False

    @staticmethod
    def is_page_not_found(html_code):
        not_found_patterns = [
            re.compile('Page Not Found', re.S),
            re.compile('Sorry! We couldn', re.S),
            re.compile('Dogs of Amazon', re.S),
        ]
        not_found = BaseParser.get_new_data(pattern_list=not_found_patterns, html_code=html_code)
        if len(not_found) > 0:
            return True
        return False

    # 合成商品url
    @staticmethod
    def make_goods_url(the_asin, urltitle='', sessionId='', retry=False):
        '''
        有cookie的情况
        https://www.amazon.com/Devita-Evening-Rich-Nutritional-Moisturizer
        /dp/B00026CZCS/ref=sr_1_1_a_it/146-2962871-2633011?
        ie=UTF8&qid=1526460738&sr=8-1&keywords=B00026CZCS

        https://www.amazon.com/(商品title截取, 需要存redis)
        /dp/(asin)/ref=sr_1_1_a_it/(sessionId)
        ?ie=UTF8&qid=(秒级时间戳)&sr=8-1&keywords=(asin)
        '''
        result = ''
        referer = ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(the_asin)
        if not k:
            return result, referer
        if retry:
            result = parse.urljoin('https://www.amazon.com/dp/', '%s?th=1&psc=1' % (the_asin))
            referer = 'https://www.amazon.com'
        else:
            # qid = int(time.time())
            if urltitle and sessionId:
                result = parse.urljoin('https://www.amazon.com/%s/dp/' % (urltitle),
                                       '%s/%s?pd_rd_i=%s&psc=1&th=1&pf_rd_s=desktop-detail-softlines&ie=UTF8&pf_rd_i=desktop'
                                       % (the_asin, sessionId, the_asin))
                referer = 'https://www.amazon.com'
            elif urltitle:
                result = parse.urljoin('https://www.amazon.com/%s/dp/' % (urltitle),
                                       '%s/?pf_rd_m=ATVPDKIKX0DER&pd_rd_i=%s&psc=1&th=1&_encoding=UTF8&pf_rd_i=desktop'
                                       % (the_asin, the_asin))
                referer = 'https://www.amazon.com'
            else:
                result = parse.urljoin('https://www.amazon.com/dp/', '%s?th=1&psc=1' % (the_asin))
                referer = 'https://www.amazon.com'
        return result, referer

    # 获取新的数据
    @staticmethod
    def get_new_data(html_code=None, xpath_list=None, pattern_list=None, xpath_obj=None):
        time1 = time.time()
        # print(len(html_code))
        result = []
        if xpath_obj and xpath_list:
            for xpath in xpath_list:
                data = []
                try:
                    # print('xpath', xpath)
                    data = xpath_obj.xpath(xpath)
                except Exception as e:
                    print('xpath[%s] 提取时[%s]' % (xpath, e))
                # print(3, 'datax', data, type(data), len(data))
                if len(data) > 0:
                    print('xpath', xpath)
                    result = data
                    # print(result, 5)
                    return result
            time2 = time.time()
            times = '%2f' % (time2 - time1)
            # print(4, 'times: ', times)
            return result

        if type(html_code) is not str:
            html_code = str(html_code)
        if html_code and pattern_list:
            # print(1, 'datar', type(html_code), len(html_code))
            i = 0
            if type(html_code) is str:
                i += 1
                # print(2, 'datar', pattern_list, i)
                for pattern in pattern_list:
                    i += 1
                    # print(2.1, 'datar pattern:', pattern, i)
                    data = pattern.findall(html_code)
                    # print(3, 'datar', data)
                    if len(data) > 0:
                        print(2.1, 'datar pattern:', pattern, i)
                        # print(4, 'datar', data, i)
                        result = data
                        time2 = time.time()
                        times = '%2f' % (time2 - time1)
                        # print(4, 'times: ', times)
                        return result
            time2 = time.time()
            times = '%2f' % (time2 - time1)
            # print(4, 'times: ', times)
            return result
        if html_code and xpath_list:
            html_code = etree.HTML(html_code)
            # print(1, 'datax', html_code)
            # print(2, 'datax', type(html_code))
            # print('xpath_list', xpath_list)
            for xpath in xpath_list:
                data = []
                try:
                    # print('xpath', xpath)
                    data = html_code.xpath(xpath)
                except Exception as e:
                    print('xpath[%s] 提取时[%s]' % (xpath, e))
                # print(3, 'datax', data, type(data), len(data))
                if len(data) > 0:
                    print('xpath', xpath)
                    result = data
                    # print(result, 5)
                    return result
            time2 = time.time()
            times = '%2f' % (time2 - time1)
            # print(4, 'times: ', times)
            return result
        time2 = time.time()
        times = '%2f' % (time2 - time1)
        # print(4, 'times: ', times)
        return result

    # 合成跟卖url
    @staticmethod
    def make_tosell_url(the_asin):
        result = ''
        # referer = ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(the_asin)
        if not k:
            return result
        result = ''
        if the_asin:
            result = 'https://www.amazon.com/gp/offer-listing/%s/ref=dp_olp_new_mbc?ie=UTF8&condition=new' % (the_asin)
        return result

    # 合成跟卖分页url
    @staticmethod
    def make_tosell_page_url(the_asin, page):
        result = ''
        referer = ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(the_asin)
        if not k:
            return result, referer
        result = ''
        if the_asin and type(page) is int:
            result = 'https://www.amazon.com/gp/offer-listing/%s/ref=olp_page_%s?ie=UTF8&f_new=true&startIndex=%s' % (the_asin, page, ((page - 1) * 10))
        return result


    @staticmethod
    def filter_str(content):
        '''清洗文本'''
        if not (isinstance(content, str) or isinstance(content, bytes)):
            return content
        sublist = ['<p.*?>', '</p.*?>', '<b.*?>', '</b.*?>', '<div.*?>', '</div.*?>',
                   '</br>', '<br />', '<ul>', '</ul>', '<li>', '</li>', '<strong>',
                   '</strong>', '<table.*?>', '<tr.*?>', '</tr>', '<td.*?>', '</td>',
                   '\r', '\n', '&.*?;', '&', '#.*?;', '<em>', '</em>']
        try:
            for substring in [re.compile(string, re.S) for string in sublist]:
                content = str(re.sub(substring, "", content)).strip()
        except:
            raise Exception('Error ' + str(substring.pattern))
        return content

    # 合成评论url
    @staticmethod
    def make_reviews_url(the_asin, urltitle=''):
        result = ''
        referer = ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(the_asin)
        if not k:
            return result
        result = ''
        if the_asin:
            result = 'https://www.amazon.com/product-reviews/%s/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent' % (the_asin)
            if urltitle:
                result = 'https://www.amazon.com/%s/product-reviews/%s/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent' % (urltitle, the_asin)
        return result

    # 合成评论分页url
    @staticmethod
    def make_reviews_page_url(the_asin, page):
        result = ''
        referer = ''
        r = re.compile('^[A-Za-z0-9]{10,10}$')
        k = r.match(the_asin)
        if not k:
            return result, referer
        result = ''
        if the_asin and page:
            result = 'https://www.amazon.com/product-reviews/%s/ref=cm_cr_othr_d_paging_btm_%s?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=%s' % (the_asin, page, page)
        return result

    @staticmethod
    def make_search_url(keyword, search_type=0):
        '''keyword is string. search_type all = aps'''
        result = ''
        if '’' in keyword:
            keyword = "'".join(keyword.split('’'))

        r = re.compile('[\u4e00-\u9fa5]+')
        k = r.search(keyword)
        if k:
            return result
        sea = 'aps'
        if search_type == 0:
            sea = 'aps'
        keyword = keyword.strip().lstrip()
        #keyword = keyword.split(' ')
        #qid = int(time.time())
        #if type(keyword) is list:
        #    keyword = '+'.join(keyword)
        #search_url = 'https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%%3D%s&field-keywords=%s&rh=i%%3A%s%%2Ck%%3A%s&qid=%s' % \
        #                  (sea, keyword, sea, keyword, qid)
        search_url = 'https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%%3D%s&field-keywords=%s' % \
                          (sea, keyword)
        return search_url

    @staticmethod
    def get_redis_time():
        #debug_log = Logger()
        #myRedis = GetRedis().return_redis(debug_log)
        #time_tuple = myRedis.time()
        #print(time_tuple)
        #timestr = '%s.%s' % (time_tuple[0], time_tuple[1])
        #print(timestr)
        times = int(time.time() * 1000)
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(times/1000)))
        return times


if __name__ == '__main__':
    print(BaseParser.get_redis_time())
