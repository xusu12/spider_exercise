#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")

from Crawler.DataOutput import GetDbObj, DataOutput, SqlConfig
from utils.util import return_PST
from utils.util import Logger
from utils.util import GetRedis
from utils.util import DataQueue


def goods_data_save(dataQ, debug_log, db_log):
    print('\ngoods_save init\n')
    data_type = 'goods'
    if dataQ.RedisQ.llen('goodsData') > 0:
        dbObj = GetDbObj().get_db_obj()
        cur = dbObj.cursor()
        dataOutput = DataOutput(dbObj, cur, db_log, debug_log, dataQ)
        db_name = SqlConfig.goods_db_name
        update_sql = SqlConfig.goods_update_sql
        insert_sql = SqlConfig.goods_insert_sql
        while True:
            datas = dataQ.get_new_goods_data()
            the_hour = return_PST().hour
            if not datas:
                if dataQ.RedisQ.llen('goodsData') > 0:
                    datas = dataQ.get_new_goods_data()
                else:
                    break
            tm = DataOutput.get_redis_time()
            for k, v in datas.items():
                asin = k
                data = v
                # print('data', data)
                # 如果库存下载失败, 先不入历史库
                print(data['getinfo_tm'], 1)
                data['getinfo_tm'] = tm
                print(data['getinfo_tm'], 2)
                print('rc1: ', data['rc'])
                print('quantity1', data['quantity'])
                sql = "select rc, quantity, price, title, bsr from public.amazon_product_data where asin=%(asin)s and getinfo_tm>%(the_tm)s ;"
                select_dict = {'asin': data['asin'], 'the_tm': (tm / 1000 - 3600 * 24 * 3) * 1000}
                cur.execute(sql, select_dict)
                select_rows = cur.fetchall()
                if len(select_rows) > 0:
                    print(select_rows, type(select_rows), type(select_rows[0]), type(select_rows[0][0]))
                    the_old_rc, the_old_qty, the_old_price, the_old_title, the_old_bsr = select_rows[0]
                    print(the_old_rc, the_old_qty, the_old_price, the_old_title, the_old_bsr)
                    the_new_qty = data['quantity']
                    print('price1', data['price'], the_old_price)
                    # 如果没有price 则用前一天的数据
                    if data['price'] <= 0 and the_old_price > 0 and data['asin_state'] == 3:
                        data['price'] = the_old_price
                    # 如果没有title, 则用前一天的数据
                    if not data['title'] and the_old_title:
                        data['title'] = the_old_title
                    # 如果没有bsr, 则用前一天的数据
                    #if data['bsr'] < 1 and the_old_bsr > 0:
                    #    data['bsr'] = the_old_bsr
                    print('the_old_rc', the_old_rc, type(the_old_rc))
                    print('old quantity', the_old_qty, type(the_old_qty))
                    print('new quantity', the_new_qty, type(the_new_qty))
                    # 如果评论小于前一天的评论, 则用前一天的评论
                    print("data['rc']", data['rc'], type(data['rc']))
                    if data.get('rc', 0) < the_old_rc:
                        data['rc'] = the_old_rc
                    # 如果库存爬取失败, 则用前一天的库存
                    if the_new_qty == -1 and the_old_qty >= 0 and data['asin_state'] == 3:
                        data['quantity'] = the_old_qty
                        data['qtydt'] = 4
                        with open('quantity_fail.csv', 'a', encoding='utf-8') as f:
                            f.write('asin, %s, old qty, %s, new qty, %s\n' % (data['asin'], the_old_qty, the_new_qty))

                    if data['asin_state'] == 2:
                        data['quantity'] = 0
                        data['qtydt'] = 5   # 不可售


                # 如果没有dpre, 则用price
                if data['dpre'] <= 0 and data['price'] > 0:
                    data['dpre'] = data['price']
                # 如果没有cart_price, 则用price
                if data['cart_price'] <= 0 and data['price'] > 0:
                    data['cart_price'] = data['price']
                print('price2', data['price'])
                print('quantity2', data['quantity'])
                print('rc2: ', data['rc'])

                if the_hour < 9 and data['quantity'] < 0 and data['asin_state'] == 3:
                    # 先不更新
                    pass
                    # # 弹出更新库不需要的字段
                    # data.pop('dpre')
                    # data.pop('bs1')
                    # data.pop('qc')
                    # data.pop('qtydt')
                    # data.pop('aday')
                    # # 再传给更新库
                    # dataOutput.save_data_to_db(update_sql, insert_sql, asin, data, db_name=db_name)
                else:
                    # 先传一份给历史库
                    druidData_to_db(asin, data, dataOutput)

                    # 弹出更新库不需要的字段
                    data.pop('dpre')
                    data.pop('bs1')
                    data.pop('qc')
                    data.pop('qtydt')
                    data.pop('aday')
                    # 再传给更新库
                    dataOutput.save_data_to_db(update_sql, insert_sql, asin, data, db_name=db_name)
                    # 记录更新时间
                    dataOutput.crawler_tm(asin, data_type)

        cur.close()
        dbObj.close()
        db_log.war('%s, %s线程任务已完成\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type))
    else:
        db_log.war('%s, %s数据队列为空\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type))

def druidData_to_db(the_asin, data_dict, dataOutput):
    # print('\ndruidData_to_db init\n')
    db_name = SqlConfig.druid_goods_db_name
    update_sql = SqlConfig.druid_goods_update_sql
    insert_sql = SqlConfig.druid_goods_insert_sql
    druid_dict = dict(
        tm='getinfo_tm',
        asin='asin',
        pasin='pasin',
        sn='sname',
        pre='dpre',
        dpre='price',
        bs1='bs1',
        qc='qc',
        rc='rc',
        rrg='rrg',
        qty='quantity',
        ts='to_sell',
        byb='byb',
        r5p='r5p',
        r4p='r4p',
        r3p='r3p',
        r2p='r2p',
        r1p='r1p',
        tpre='ts_min_price',
        bsr='bsr',
        qtydt='qtydt',
        aday='aday'
        # special='',
    )
    for item in druid_dict:
        druid_dict[item] = data_dict[druid_dict[item]]
    # print('druid', druid_dict)
    dataOutput.save_data_to_db(update_sql, insert_sql, the_asin, druid_dict, db_name=db_name)


if __name__ == '__main__':
    log_name = sys.argv[0].split('/')[-1].split('.')[0]
    print(log_name)
    debug_log = Logger(log_name=log_name)
    db_log = Logger(log_level='DB', log_name=log_name)
    myRedis = GetRedis().return_redis(debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    goods_data_save(dataQ, debug_log, db_log)
