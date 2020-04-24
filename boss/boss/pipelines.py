# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class BossPipeline(object):
    def open_spider(self, spider):
        # print(11)
        # 每次爬虫打开时调用，只会执行一次
        if spider.name == 'zhiwei':
            self.file = open('boss.csv', 'w', encoding='utf8')

    def process_item(self, item, spider):
        # print(item)
        # 引擎每次遍历到item数据都会调用这个方法  写入文件
        if spider.name == 'zhiwei':
            json.dump(dict(item), self.file, ensure_ascii=False)
            self.file.write('\n')

        # 返回item  可以被下一个解析函数处理
        return item

    def close_spider(self, spider):
        # 当前爬虫关闭的时候执行, 只执行一次
        self.file.close()
