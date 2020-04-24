# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import json
import csv
import pprint
class YouzuPipeline(object):
    def open_spider(self,spider):
        date = datetime.date.today()
        if spider.name =='YouzuSpider':
            self.file = open('.Youzu_{0}.csv'.format(date), 'w',newline='')
            self.csv_writer = csv.writer(self.file)
            self.csv_writer.writerow(['日期', '分包名称', '活跃玩家数', '新增玩家数', '付费人数', 'ARPU', 'LTV7','LTV14','付费金额','可分成金额'])

    def process_item(self, item, spider):
        date = datetime.date.today()
        content = item['data']
        print('======')
        pprint.pprint(content)
        if spider.name =='YouzuSpider':
            for key in content:
                line = []
                line.append(key['tt'])
                line.append(key['cps_name'])
                line.append(key['total'])
                line.append(key['roles'])
                line.append(key['new_pay_count'])
                line.append(key['ARPU'])
                line.append(key['LTV7'])
                line.append(key['LTV14'])
                line.append(key['amount'])
                line.append(key['income'])
                self.csv_writer.writerow(line)
        return item



    def close_spider(self,spider):
        if spider.name == 'YouzuSpider':
            self.file.close()