# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import csv

class CityPipeline(object):
    def process_item(self, item, spider):
        return item


class CityCsvPipeline(object):
    def __init__(self):
        # csv文件的位置,无需事先创建
        store_file = os.path.dirname(__file__) + '/spiders/qtw.csv'

        # 打开(创建)文件
        self.file = open(store_file, 'wb')
        # csv写法
        self.writer = csv.writer(self.file)

    def process_item(self, item, spider):
        # 判断字段值不为空再写入文件
        if item['image_name']:
            self.writer.writerow((item["项目名称"],item["证明书号"],item["座落"],item["合同样本信息"],item["楼房信息"],item["楼盘url"],item['项目url'],item["楼盘分类"]))

        return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.file.close()