#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
from Crawler.DataOutput import GetDbObj, DataOutput, SqlConfig
from Crawler.BaseCrawler import BaseCrawler
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import DataQueue


def tosell_save(dataQ, debug_log, db_log):
    print('\ntosell_save init\n')
    data_type = 'tosell'
    if dataQ.RedisQ.llen('tosellData') > 0:
        dbObj = GetDbObj().get_db_obj()
        cur = dbObj.cursor()
        dataOutput = DataOutput(dbObj, cur, db_log, debug_log, dataQ)
        data_tosell_db_name = SqlConfig.data_tosell_db_name
        data_tosell_update_sql = SqlConfig.data_tosell_update_sql
        data_tosell_insert_sql = SqlConfig.data_tosell_insert_sql

        druid_tosell_db_name = SqlConfig.druid_tosell_db_name
        #druid_tosell_update_sql = SqlConfig.druid_tosell_update_sql
        druid_tosell_update_sql = None #SqlConfig.druid_tosell_update_sql
        druid_tosell_insert_sql = SqlConfig.druid_tosell_insert_sql
        while True:
            datas = dataQ.get_new_tosellData()
            if not datas:
                if dataQ.RedisQ.llen('tosellData') > 0:
                    datas = dataQ.get_new_tosellData()
                else:
                    break
            # print('\ntosell_save datas: [= %s =] \n' % (datas))
            tm = DataOutput.get_redis_time()
            for item in datas:
                asin = item
                tosell_datas = datas[item][0]
                tosell_list = datas[item][1]
                # print('tosell_datas: ', tosell_datas)
                print(tosell_datas['getinfo_tm'], 1)
                tosell_datas['getinfo_tm'] = tm
                print(tosell_datas['getinfo_tm'], 2)
                # sql = "select asin, getinfo_tm from public.amazon_product_data_tosell where asin=%(asin)s and getinfo_tm>%(the_tm)s;"
                # # select_dict = {'asin': asin, 'the_tm': (tm / 1000 - 120) * 1000}
                # the_tm = dataQ._get_value_from_string('initUpdateTm', 'initTime')
                # print('the_tm1', the_tm)
                # if not the_tm:
                #     _, the_tm = BaseCrawler.get_the_time()
                #     print('the_tm2', the_tm)
                # else:
                #     the_tm = str(the_tm, encoding='utf-8')
                # print('the_tm3', the_tm)
                # select_dict = {'asin': asin, 'the_tm': int(the_tm) * 1000}
                # cur.execute(sql, select_dict)
                # select_rows = cur.fetchall()
                sql = "select asin, aday from public.amazon_product_tosell where asin=%(asin)s and aday=%(aday)s limit 1;"
                aday = tosell_list[0]['aday'] if len(tosell_list) > 0 else return_PST().strftime('%Y%m%d')
                select_dict = {'asin': asin, 'aday': aday}
                cur.execute(sql, select_dict)
                select_rows = cur.fetchall()
                dbObj.commit()
                if len(select_rows) < 1:
                    print(tosell_datas)
                    if not tosell_datas.get('sname'):
                        sql1 = "select sname, seller_id from public.amazon_product_data where asin='%s' and getinfo_tm > %s" % (asin, tm - 24*3600*1000)
                        cur.execute(sql1)
                        select_rows = cur.fetchall()
                        dbObj.commit()
                        select_rows = select_rows[0] if len(select_rows) == 1 else ('', '')
                        sname, seller_id = select_rows
                        print('seller_id: ', seller_id)
                        print('sname ',sname)
                        tosell_datas['sname'] = sname
                        tosell_datas['seller_id'] = seller_id
                    data0 = dataOutput.save_data_to_db(data_tosell_update_sql, data_tosell_insert_sql,
                                                       asin, tosell_datas, db_name=data_tosell_db_name)
                    for item in tosell_list:
                        item['tm'] = int(tm / 1000)
                        data = dataOutput.save_data_to_db(druid_tosell_update_sql, druid_tosell_insert_sql,
                                                          asin, item, db_name=druid_tosell_db_name)

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
    tosell_save(dataQ, debug_log, db_log)
