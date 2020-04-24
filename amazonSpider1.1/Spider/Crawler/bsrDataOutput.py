#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import time
from Crawler.DataOutput import GetDbObj, DataOutput, SqlConfig
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import DataQueue


def bsrData_save(dataQ, debug_log, db_log):
    print('\nbsrData_save init\n')
    data_type = 'bsr'
    if dataQ.RedisQ.llen('bsrData') > 0:
        dbObj = GetDbObj().get_db_obj()
        cur = dbObj.cursor()
        dataOutput = DataOutput(dbObj, cur, db_log, debug_log, dataQ)
        db_name = SqlConfig.bsrData_db_name
        update_sql = None    #SqlConfig.bsrData_update_sql
        insert_sql = SqlConfig.bsrData_insert_sql
        while True:
            datas = dataQ.get_new_bsrData()
            if not datas:
                if dataQ.RedisQ.llen('bsrData') > 0:
                    datas = dataQ.get_new_bsrData()
                else:
                    break
            for item in datas:
                asin = item
                tuple_list = datas[item]
                tm = int(DataOutput.get_redis_time())
                # print('asin tuple_list: ', asin, tuple_list)
                for item in tuple_list:
                    if item and type(item) is tuple:
                        # print('bsr item: ', item)
                        itemLen = len(item)
                        bsr = item[0]
                        bsrc = item[1]
                        aday = item[2]
                        # if itemLen == 4:
                        #     tm = item[3]
                        # else:
                        #     tm = int(time.time() * 1000)
                        data_dict = dict(
                            asin=asin,
                            bsr=bsr,
                            bsrc=bsrc,
                            tm=tm,
                            aday=aday
                        )
                        data = dataOutput.save_data_to_db(update_sql, insert_sql, asin, data_dict, db_name=db_name)
                        # print('bsrData: ',data)

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
    bsrData_save(dataQ, debug_log, db_log)
