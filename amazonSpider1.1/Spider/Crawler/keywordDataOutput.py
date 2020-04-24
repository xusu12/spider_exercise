#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import psycopg2.pool

from Crawler.DataOutput import GetDbObj, DataOutput, SqlConfig
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import DataQueue
from conf.setting import DATADB_CONFIG
from conf.setting import BASE_TYPE


def keyword_data_save(dataQ, debug_log, db_log):
    print('\nkeyword_data_save init\n')
    data_type = 'keyword'
    if dataQ.RedisQ.llen('keywordData') > 0:

        pool = psycopg2.pool.SimpleConnectionPool(5, 51, **DATADB_CONFIG[BASE_TYPE])
        # dbObj1 = GetDbObj().get_db_obj()
        # cur1 = dbObj1.cursor()
        # dataOutput = DataOutput(dbObj1, cur1, db_log, debug_log, dataQ)
        keyword_data_db_name = SqlConfig.keyword_data_db_name
        keyword_data_update_sql = SqlConfig.keyword_data_update_sql
        keyword_data_insert_sql = SqlConfig.keyword_data_insert_sql

        druid_keyword_db_name = SqlConfig.druid_keyword_db_name
        #druid_keyword_update_sql = SqlConfig.druid_keyword_update_sql
        druid_keyword_update_sql = None 
        druid_keyword_insert_sql = SqlConfig.druid_keyword_insert_sql
        i = 0
        while True:
            i += 1
            dbObj = pool.getconn(i)
            cur = dbObj.cursor()
            datas = dataQ.get_new_keywordData()
            if not datas:
                if dataQ.RedisQ.llen('keywordData') > 0:
                    print(dataQ.RedisQ.llen('keywordData'), type(dataQ.RedisQ.llen('keywordData')))
                    datas = dataQ.get_new_keywordData()
                else:
                    break

            for k, v in datas.items():
                kw = k
                tm = DataOutput.get_redis_time()
                keyword_data_dict = v[0]
                keyword_druid_data_list = v[1]
                aday = keyword_druid_data_list[0]['aday'] if len(keyword_druid_data_list) > 0 else return_PST().strftime("%Y%m%d")
                if keyword_data_dict['search_num'] <= 50:
                    if keyword_data_dict['search_num'] != len(keyword_druid_data_list):
                        keyword_data_dict['search_num'] = len(keyword_druid_data_list)
                        for data in keyword_druid_data_list:
                            data['srn'] = len(keyword_druid_data_list)

                # print('keyword_data_dict: ', keyword_data_dict)
                #print(keyword_data_dict['getinfo_tm'], 1)
                keyword_data_dict['getinfo_tm'] = tm
                # print(keyword_data_dict['getinfo_tm'], 2)
                sql = "select kw from public.amazon_druid_keyword_data where kw=%(kw)s and aday=%(aday)s limit 1;"
                the_data = dict(kw=kw, aday=aday)
                cur.execute(sql, the_data)
                asin_rows = cur.fetchall()
                print('asin_rows: ', len(asin_rows))
                print('keyword_druid_data_list len: ', len(keyword_druid_data_list))
                if len(asin_rows) < 1:
                    data0 = DataOutput.save_data_to_db_pool(dbObj, cur, db_log, debug_log, dataQ,keyword_data_update_sql, keyword_data_insert_sql,
                                                   kw, keyword_data_dict, db_name=keyword_data_db_name)
                # print('keyword_druid_data_list: ', keyword_druid_data_list)
                    if len(keyword_druid_data_list) > 0:
                        for druid in keyword_druid_data_list:
                            # print(druid)
                            druid['tm'] = tm
                            data1 = DataOutput.save_data_to_db_pool(dbObj, cur, db_log, debug_log, dataQ,
                                                                    druid_keyword_update_sql, druid_keyword_insert_sql,
                                                                    kw, druid, db_name=druid_keyword_db_name)
                            # time.sleep(20)
                    # 记录更新时间
                    data_dict = {'kw': kw, 'crawler_tm': keyword_data_dict['getinfo_tm']/1000}
                    db_name = 'public.amazon_keyword_monitor.crawler_tm'
                    insert_sql = ''
                    update_sql = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
                    DataOutput.save_data_to_db_pool(dbObj, cur, db_log, debug_log, dataQ, update_sql, insert_sql, kw, data_dict, db_name=db_name)
            dbObj.commit()
            pool.putconn(dbObj, i)
            if i == 50:
                i = 0
        pool.closeall()
    db_log.war('%s, %s线程任务已完成\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type))


if __name__ == '__main__':
    db_log = Logger('DB')
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    keyword_data_save(dataQ, debug_log, db_log)
