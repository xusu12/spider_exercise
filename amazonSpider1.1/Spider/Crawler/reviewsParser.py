#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append("../")
import re
from datetime import datetime
from lxml.html import tostring


from Crawler.BaseParser import BaseParser
# from tests.reviews_html1 import reviews_html1
from utils.decorator import timer


class ReviewsParser(BaseParser):
    def __init__(self):
        self.url = None
        self.html_code = None

    # 解析评论详情
    @timer
    def reviews_parser(self, html_code, the_asin, ip='', download_url=''):
        if not html_code:
            return
        if download_url:
            self.url = download_url
        reviews_datas = {}
        reviews_list = []
        self.html_code = html_code
        buyer_id_tuple_list = ReviewsParser.get_buyer_id(html_code)
        if len(buyer_id_tuple_list) > 0:
            for item in buyer_id_tuple_list:
                buyer = self._get_buyer(item)
                theme = self._get_theme(item)
                body = self._get_body(item)
                date = self._get_date(item)
                rrg = self._get_rrg(item)
                helpful = self._get_helpful(item)
                reviews_dict = dict(
                    asin=the_asin,
                    date=date,
                    rrg=rrg,  # 评星
                    theme=theme,  # 主题
                    body=body,  # 评论内容
                    buyer=buyer,  # 买家
                    helpful=helpful,  # 多少人觉得有帮助
                )
                reviews_list.append(reviews_dict)
        if len(reviews_list) > 0:
            reviews_datas[the_asin] = reviews_list
        return reviews_datas

        # 抓取评论页链接


    # 获得评论日期列表
    @staticmethod
    def get_reviews_date_list(html_code, the_asin=''):
        reviews_date_list = []
        buyer_id_tuple_list = ReviewsParser.get_buyer_id(html_code)
        if len(buyer_id_tuple_list) > 0:
            for item in buyer_id_tuple_list:
                date = ReviewsParser.get_date(html_code, item)
                reviews_date_list.append(date)
        return reviews_date_list

    # 获取评论数
    @staticmethod
    def get_review_count(html_code=None):
        review_xpath = [
            '//div[@id="cm_cr-product_info"]//span[@data-hook="total-review-count"]/text()',
            '//*[@id="cm_cr-product_info"]//span[@data-hook="total-review-count"]/text()',
            '//div[@id="cm_cr-product_info"]/div/div/div/div/div/div/div/span[@data-hook="total-review-count"]/text()',
            '//*[@id="cm_cr-product_info"]/div/div/div/div/div/div/div/span[@data-hook="total-review-count"]/text()',
        ]
        review = ReviewsParser.get_new_data(xpath_list=review_xpath, html_code=html_code)
        # print('review: ', review)
        if len(review) > 0:
            review = review[0]
            review = ''.join(review.split(','))
            if review.isdigit():
                return int(review)
            else:
                return 0
        else:
            return 0

    # 抓取评论人ID
    @staticmethod
    def get_buyer_id(html_code):
        id_xpath = [
            '//div[@data-hook="review"]/@id',
        ]
        id_list = ReviewsParser.get_new_data(xpath_list=id_xpath, html_code=html_code)
        result_list = []
        if len(id_list) > 0:
            i = 0
            for id in id_list:
                i += 1
                id_tuple = (i, id)
                result_list.append(id_tuple)
        return result_list

    # 获取评论人
    def _get_buyer(self, buyer_id_tuple, html_code=None):
        '''评论人可以直接用'''
        if html_code is None:
            html_code = self.html_code
        # print('buyer_id_tuple', buyer_id_tuple)
        buyer_xpath = [
            '//div[@id="%s"]/div/div/span/a[@data-hook="review-author"]/text()' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//a[@data-hook="review-author"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]/div/div/span/a[@data-hook="review-author"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//a[@data-hook="review-author"]/text()' % (buyer_id_tuple[1]),
        ]
        # print('buyer_xpath', buyer_xpath)
        buyer = self.get_new_data(xpath_list=buyer_xpath, html_code=html_code)
        if len(buyer) > 0:
            buyer = buyer[0]
            buyer = self.filter_str(buyer)
            return buyer
        else:
            return ''

    # 获取评论标题
    def _get_theme(self, buyer_id_tuple, html_code=None):
        '''评论标题可以直接用'''
        if html_code is None:
            html_code = self.html_code
        title_xpath = [
            '//div[@id="%s"]/div/div/a[@data-hook="review-title"]/text()' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//a[@data-hook="review-title"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]/div/div/a[@data-hook="review-title"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//a[@data-hook="review-title"]/text()' % (buyer_id_tuple[1]),
        ]
        title = self.get_new_data(xpath_list=title_xpath, html_code=html_code)
        if len(title) > 0:
            title = title[0]
            title = self.filter_str(title)
            if len(title) > 255:
                title = title[0: 247] + '...'
            return title
        else:
            return ''

    # 获取评论内容
    def _get_body(self, buyer_id_tuple, html_code=None):
        ''''''
        if html_code is None:
            html_code = self.html_code
        body_xpath = [
            '//div[@id="%s"]/div/div/span[@data-hook="review-body"]/text()' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//span[@data-hook="review-body"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]/div/div/span[@data-hook="review-body"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//span[@data-hook="review-body"]/text()' % (buyer_id_tuple[1]),
        ]
        body = self.get_new_data(xpath_list=body_xpath, html_code=html_code)
        # print('body', body)
        if len(body) > 0:
            body_list = []
            for item in body:
                body = self.filter_str(item)
                body_list.append(body)
            if len(body_list) > 1:
                result = '\n'.join(body_list)
            else:
                result = body_list[0]

            return result
        else:
            return ''

    # 获取评星
    def _get_rrg(self, buyer_id_tuple, html_code=None):
        '''5.0 out of 5 stars 要进行数字提取， int型转换'''
        rrgint = 0
        if html_code is None:
            html_code = self.html_code
        rrg_xpath = [
            '//div[@id="%s"]//a[@class="a-link-normal"]/i[@data-hook="review-star-rating"]/span/text()' % (
                buyer_id_tuple[1]),
            '//div[@id="%s"]//i[@data-hook="review-star-rating"]/span/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//a[@class="a-link-normal"]/i[@data-hook="review-star-rating"]/span/text()' % (
                buyer_id_tuple[1]),
            '//*[@id="%s"]//i[@data-hook="review-star-rating"]/span/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//a[@class="a-link-normal"]/@title' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//a[@class="a-link-normal"]/@title' % (buyer_id_tuple[1]),

        ]
        rrg = self.get_new_data(xpath_list=rrg_xpath, html_code=html_code)
        if len(rrg) > 0:
            rrg = rrg[0]
            rrg = self.filter_str(rrg)
            rrgnum = rrg.split('.')[0]
            if rrgnum.isdigit():
                rrgint = int(rrgnum)
            return rrgint
        return rrgint

    @staticmethod
    def get_date(html_code, buyer_id_tuple):
        result = 0
        date_xpath = [
            '//div[@id="%s"]/div/div/span[@data-hook="review-date"]' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//span[@data-hook="review-date"]' % (buyer_id_tuple[1]),
            '//*[@id="%s"]/div/div/span[@data-hook="review-date"]' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//span[@data-hook="review-date"]' % (buyer_id_tuple[1]),
        ]
        date = ReviewsParser.get_new_data(xpath_list=date_xpath, html_code=html_code)
        if len(date) > 0:
            date_html = tostring(date[0])
            pattern_list = [
                re.compile('[A-Za-z]+ \d+, \d{4}', re.S),
                re.compile('on ([A-Za-z]+ \d+, \d{4})', re.S),
            ]
            date = ReviewsParser.get_new_data(pattern_list=pattern_list, html_code=date_html)
            if len(date) > 0:
                date_str = date[0].strip().lstrip()
                print(date_str)
                date_format = datetime.strptime(date_str, "%B %d, %Y")
                if not date_format:
                    date_format = datetime.strptime(date_str, "%b %d, %Y")
                result = int(date_format.strftime('%Y%m%d'))
            # print('date', type(date), date)
        return result

    # 获取评论日期
    def _get_date(self, buyer_id_tuple, html_code=None):
        '''June 20, 2017 日期要进行换算，并转换成int型'''
        if html_code is None:
            html_code = self.html_code
        return ReviewsParser.get_date(html_code, buyer_id_tuple)


    # 获取多少人觉得有帮助
    def _get_helpful(self, buyer_id_tuple, html_code=None):
        '''2 people found this helpful. 要进行数字提取， int型转换'''
        helpfulint = 0
        if html_code is None:
            html_code = self.html_code
        helpful_xpath = [
            '//div[@id="%s"]/div/span/span/span/span[@data-hook="helpful-vote-statement"]/text()' % (buyer_id_tuple[1]),
            '//div[@id="%s"]//span[@data-hook="helpful-vote-statement"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]/div/span/span/span/span[@data-hook="helpful-vote-statement"]/text()' % (buyer_id_tuple[1]),
            '//*[@id="%s"]//span[@data-hook="helpful-vote-statement"]/text()' % (buyer_id_tuple[1]),
        ]
        helpful = self.get_new_data(xpath_list=helpful_xpath, html_code=html_code)
        if len(helpful) > 0:
            helpful = helpful[0]
            helpful = self.filter_str(helpful)
            helpful_num = helpful.split(' ')[0]
            if helpful_num.isdigit():
                helpfulint = int(helpful_num)
            if 'One' in helpful_num or 'one' in helpful_num:
                helpfulint = 1
            return helpfulint
        return helpfulint


if __name__ == '__main__':
    html = reviews_html1
    self = ReviewsParser()
    print(self.reviews_parser(html, 'the_asin'))