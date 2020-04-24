#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
from datetime import timedelta

from Crawler.DataOutput import GetDbObj, DataOutput, SqlConfig
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import DataQueue


def reviews_save(dataQ, debug_log, db_log):
    print('\nreviews_save init\n')
    data_type = 'reviews'
    if dataQ.RedisQ.llen('reviewsData') > 0:
        dbObj = GetDbObj().get_db_obj()
        cur = dbObj.cursor()
        dataOutput = DataOutput(dbObj, cur, db_log, debug_log, dataQ)
        reviews_db_name = SqlConfig.reivews_db_name
        reviews_update_sql = SqlConfig.reivews_update_sql
        reviews_insert_sql = SqlConfig.reivews_insert_sql

        datetime = return_PST()
        oldDate = datetime - timedelta(days=90)
        yesterdate = datetime - timedelta(days=1)
        yesterday = yesterdate.strftime('%Y%m%d')
        theYesterDete = int(yesterday)
        theMon = oldDate.strftime('%Y%m%d')
        three_mon_date = int(theMon)

        while True:
            datas = dataQ.get_new_reviewsData()
            if not datas:
                if dataQ.RedisQ.llen('reviewsData') > 0:
                    datas = dataQ.get_new_reviewsData()
                else:
                    break

            for item in datas:
                asin = item
                dict_list = datas[item]
                # print('tuple_list: ', dict_list)
                md5value = asin + 'reviewsFirst'
                md5key = DataOutput.get_md5_key(md5value)
                first = dataQ.is_first_download(md5key)
                i = 0
                for item in dict_list:
                    i += 1
                    # md5key只传3次, 避免无畏的重复写入, 以及前两次写入失败的情况.
                    if i < 3:
                        theMd5key = md5key
                    else:
                        theMd5key = None

                    # 如果是第一次下载, 则写入三个月内的评论.　
                    if first:
                        if item['date'] >= three_mon_date:
                            # print('reviews item: ', item)
                            data0 = dataOutput.save_data_to_db(reviews_update_sql, reviews_insert_sql,
                                                               asin, item, db_name=reviews_db_name, md5key=theMd5key)
                    # 否则只写入当天评论
                    else:
                        if item['date'] >= theYesterDete:
                            # print('reviews item: ', item)
                            data1 = dataOutput.save_data_to_db(reviews_update_sql, reviews_insert_sql,
                                                               asin, item, db_name=reviews_db_name)
                # 记录更新时间
                dataOutput.crawler_tm(asin, data_type)
        cur.close()
        dbObj.close()
        db_log.war('%s, %s线程任务已完成\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type))
    else:
        db_log.war('%s, %s数据队列为空\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type))



if __name__ == '__main__':
    log_name = sys.argv[0].split('/')[-1].split('.')[0]
    print(log_name)
    debug_log = Logger(log_name=log_name)
    db_log = Logger(log_level='DB', log_name=log_name)
    myRedis = GetRedis().return_redis(debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    reviews_save(dataQ, debug_log, db_log)

    # datetime = return_PST()
    # oldDate = datetime - timedelta(days=92)
    # dateNow = datetime.strftime('%Y%m%d')
    # theDeteNow = int(dateNow)
    # theMon = oldDate.strftime('%Y%m%d')
    # three_mon_date = int(theMon)
    # print(three_mon_date, theDeteNow)
