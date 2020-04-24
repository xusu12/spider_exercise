#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import os
import time
import hashlib

import psycopg2
import psycopg2.pool

# from conf.setting import BASE_DIR
from conf.setting import DATA_DIR
from conf.setting import DATADB_CONFIG
from conf.setting import BASE_TYPE
from utils.util import Logger
from utils.util import GetRedis
# from utils.util import DataQueue
from utils.util import return_PST


class GetDbObj:
    def get_db_obj(self):
        dbObj = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        return dbObj


class SqlConfig:
    goods_db_name = 'public.amazon_product_data'
    goods_update_sql = "update public.amazon_product_data set \
pasin=%(pasin)s, title=%(title)s, image=%(image)s, brand=%(brand)s, price=%(price)s, sale_price=%(sale_price)s,\
sname=%(sname)s, ts_min_price=%(ts_min_price)s, to_sell=%(to_sell)s, byb=%(byb)s, bsr=%(bsr)s, rc=%(rc)s, rrg=%(rrg)s,\
r5p=%(r5p)s, r4p=%(r4p)s, r3p=%(r3p)s, r2p=%(r2p)s, r1p=%(r1p)s,feature=%(feature)s, refresh_tm=%(refresh_tm)s,\
collect_tm=%(collect_tm)s, getinfo_tm=%(getinfo_tm)s, image_more=%(image_more)s, variant=%(variant)s,\
asin_type=%(asin_type)s, is_monitor=%(is_monitor)s, cart_price=%(cart_price)s, asin_state=%(asin_state)s,\
monitor_type=%(monitor_type)s, quantity=%(quantity)s, release_date=%(release_date)s, seller_id=%(seller_id)s, is_sync=0, crawler_state=1\
where asin=%(asin)s;"
    goods_insert_sql = "INSERT INTO public.amazon_product_data(asin, pasin, title, image, brand,\
price, sale_price, sname, ts_min_price, to_sell, byb, bsr, rc, rrg, r5p, r4p, r3p, r2p, r1p, feature, refresh_tm,\
collect_tm, getinfo_tm, image_more, variant, asin_type, is_monitor, cart_price, asin_state, monitor_type, quantity,\
release_date, seller_id, crawler_state) VALUES (%(asin)s,%(pasin)s,%(title)s,%(image)s,%(brand)s,%(price)s,%(sale_price)s,%(sname)s,\
%(ts_min_price)s,%(to_sell)s,%(byb)s,%(bsr)s,%(rc)s,%(rrg)s,%(r5p)s,%(r4p)s,%(r3p)s,%(r2p)s,%(r1p)s,%(feature)s,\
%(refresh_tm)s, %(collect_tm)s, %(getinfo_tm)s, %(image_more)s, %(variant)s, %(asin_type)s, %(is_monitor)s, \
%(cart_price)s, %(asin_state)s, %(monitor_type)s, %(quantity)s, %(release_date)s, %(seller_id)s, 1);"

    druid_goods_db_name = 'public.amazon_druid_product_data'
    druid_goods_update_sql  = "update public.amazon_druid_product_data set tm=%(tm)s, pasin=%(pasin)s, sn=%(sn)s,\
pre=%(pre)s, dpre=%(dpre)s, rc=%(rc)s, rrg=%(rrg)s, ts=%(ts)s, byb=%(byb)s, r5p=%(r5p)s, r4p=%(r4p)s, r3p=%(r3p)s,\
r2p=%(r2p)s, r1p=%(r1p)s, bsr=%(bsr)s, bs1=%(bs1)s, qc=%(qc)s, qty=%(qty)s, qtydt=%(qtydt)s, tpre=%(tpre)s\
where asin=%(asin)s and aday=%(aday)s;"
    druid_goods_insert_sql = "INSERT INTO public.amazon_druid_product_data(tm, asin, pasin, sn, pre, dpre, rc, rrg,\
ts, byb, r5p, r4p, r3p, r2p, r1p, bsr, aday, bs1, qc, qty, qtydt, tpre) VALUES (%(tm)s, %(asin)s, %(pasin)s, %(sn)s,\
%(pre)s, %(dpre)s, %(rc)s, %(rrg)s, %(ts)s, %(byb)s, %(r5p)s, %(r4p)s, %(r3p)s, %(r2p)s, %(r1p)s, %(bsr)s, %(aday)s,\
%(bs1)s, %(qc)s, %(qty)s, %(qtydt)s, %(tpre)s);"

    bsrData_db_name = 'public.amazon_druid_product_data_bsr'
    bsrData_update_sql = "update public.amazon_druid_product_data_bsr set tm=%(tm)s \
where asin=%(asin)s and aday=%(aday)s and bsrc=%(bsrc)s and bsr=%(bsr)s;"
    bsrData_insert_sql = "INSERT INTO public.amazon_druid_product_data_bsr(tm, asin, bsrc, bsr, aday) \
VALUES (%(tm)s, %(asin)s, %(bsrc)s, %(bsr)s, %(aday)s);"

    data_tosell_db_name = 'public.amazon_product_data_tosell'
    data_tosell_update_sql = "update public.amazon_product_data_tosell set sn=%(sn)s, fba_sn=%(fba_sn)s,\
plow=%(plow)s, plows=%(plows)s, plows_id=%(plows_id)s, getinfo_tm=%(getinfo_tm)s, sname=%(sname)s,\
seller_id=%(seller_id)s, is_sync=0, crawler_state=1 where asin=%(asin)s;"
    data_tosell_insert_sql = "INSERT INTO public.amazon_product_data_tosell(asin, sn, fba_sn, plow, plows,\
plows_id, getinfo_tm, sname, seller_id, crawler_state) VALUES (%(asin)s, %(sn)s, %(fba_sn)s, %(plow)s, %(plows)s,\
%(plows_id)s, %(getinfo_tm)s, %(sname)s, %(seller_id)s, 1);"

    druid_tosell_db_name = 'public.amazon_product_tosell'
    druid_tosell_update_sql = "update public.amazon_product_tosell set stype=%(stype)s, price=%(price)s,\
demo=%(demo)s, positive=%(positive)s, total_ratings=%(total_ratings)s, tm=%(tm)s, fba=%(fba)s,\
reivew_count=%(reivew_count)s, delivery=%(delivery)s where seller_id=%(seller_id)s and condition=%(condition)s \
and sname=%(sname)s and aday=%(aday)s and asin=%(asin)s;"
    druid_tosell_insert_sql = "INSERT INTO public.amazon_product_tosell(asin, condition, sname, stype, price,\
demo, positive, total_ratings, tm, fba, seller_id, reivew_count, delivery, aday) VALUES (%(asin)s, %(condition)s,\
%(sname)s, %(stype)s, %(price)s, %(demo)s, %(positive)s, %(total_ratings)s, %(tm)s, %(fba)s, %(seller_id)s,\
%(reivew_count)s, %(delivery)s, %(aday)s);"

    reivews_db_name = 'public.amazon_product_comment'
    reivews_update_sql = "update public.amazon_product_comment set rrg=%(rrg)s, body=%(body)s, helpful=%(helpful)s  \
where asin=%(asin)s and date=%(date)s and buyer=%(buyer)s and theme=%(theme)s;"
    reivews_insert_sql = "INSERT INTO public.amazon_product_comment(asin, date, rrg, theme, body, buyer, helpful) \
VALUES (%(asin)s, %(date)s, %(rrg)s, %(theme)s, %(body)s, %(buyer)s, %(helpful)s);"

    keyword_data_db_name = 'public.amazon_keyword_data'
    keyword_data_update_sql = "update public.amazon_keyword_data set cid=%(cid)s, mon_search=%(mon_search)s,\
search_num=%(search_num)s, price_max=%(price_max)s, price_min=%(price_min)s, price_ave=%(price_ave)s,\
rrg_max=%(rrg_max)s, rrg_min=%(rrg_min)s, rrg_ave=%(rrg_ave)s, rc_max=%(rc_max)s, rc_min=%(rc_min)s,\
rc_ave=%(rc_ave)s, date=%(date)s, mon_search_state=%(mon_search_state)s, other_state=%(other_state)s,\
getinfo_tm=%(getinfo_tm)s, is_sync=0, crawler_state=1 where kw=%(kw)s;"
    keyword_data_insert_sql = "INSERT INTO public.amazon_keyword_data (kw, cid, mon_search, search_num, price_max,\
price_min, price_ave, rrg_max, rrg_min, rrg_ave, rc_max, rc_min, rc_ave, date, mon_search_state, other_state,\
getinfo_tm, crawler_state) VALUES (%(kw)s, %(cid)s, %(mon_search)s, %(search_num)s, %(price_max)s, %(price_min)s, %(price_ave)s,\
%(rrg_max)s, %(rrg_min)s, %(rrg_ave)s, %(rc_max)s, %(rc_min)s, %(rc_ave)s, %(date)s,\
%(mon_search_state)s, %(other_state)s, %(getinfo_tm)s, 1);"

    druid_keyword_db_name = 'public.amazon_druid_keyword_data'
    druid_keyword_update_sql = "update public.amazon_druid_keyword_data set asin=%(asin)s, cid=%(cid)s, \
title=%(title)s, img=%(img)s, brand=%(brand)s, msn=%(msn)s, srn=%(srn)s, price=%(price)s, rrg=%(rrg)s, \
rc=%(rc)s, special=%(special)s, tm=%(tm)s, issp=%(issp)s where kw=%(kw)s and aday=%(aday)s and pr=%(pr)s;"
    druid_keyword_insert_sql = "INSERT INTO public.amazon_druid_keyword_data(kw, cid, pr, asin, title, img, brand, \
msn, srn, price, rrg, rc, special, tm, aday, issp) VALUES (%(kw)s, %(cid)s, %(pr)s, %(asin)s, %(title)s, %(img)s, \
%(brand)s, %(msn)s, %(srn)s, %(price)s, %(rrg)s, %(rc)s, %(special)s, %(tm)s, %(aday)s, %(issp)s);"


class DataOutput:
    def __init__(self, dbObj, cur, db_log, debug_log, dataQ):
        self.dbObj = dbObj
        self.cur = cur
        self.db_log = db_log
        self.debug_log = debug_log
        self.dataQ = dataQ

    @staticmethod
    def get_redis_time():
        debug_log = Logger()
        myRedis = GetRedis().return_redis(debug_log)
        time_tuple = myRedis.time()
        print(time_tuple)
        timestr = '%s.%s' % (time_tuple[0], time_tuple[1])
        print(timestr)
        times = int(float(timestr) * 1000)
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(times/1000)))
        return times

    def save_data_to_db(self, update_sql, insert_sql, the_asin_or_kw, data_dict, db_name='', md5key=''):
        self.dataQ.record_dbSum_times()
        # print(the_asin_or_kw, data_dict)
        try:
            if update_sql and insert_sql:
                self.cur.execute(update_sql, data_dict)
                row = self.cur.rowcount
                if row > 0:
                    self.dbObj.commit()
                    self.dataQ.record_db_ok_times()
                    self.db_log.info('%s,%s,%s,%s行,更新成功' %
                                     (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                    # 评论进程标记第一次
                    if md5key:
                        self.dataQ.the_reviews_first_download(md5key)
                else:
                    self.dbObj.rollback()
                    self.cur.execute(insert_sql, data_dict)
                    row = self.cur.rowcount
                    if row > 0:
                        self.dbObj.commit()
                        self.dataQ.record_db_ok_times()
                        self.db_log.info('%s,%s,%s,%s行,插入成功' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                        # 评论进程标记第一次
                        if md5key:
                            self.dataQ.the_reviews_first_download(md5key)
                    else:
                        self.dbObj.rollback()
            else:
                if update_sql and not insert_sql:
                    self.cur.execute(update_sql, data_dict)
                    row = self.cur.rowcount
                    if row > 0:
                        self.dbObj.commit()
                        self.dataQ.record_db_ok_times()
                        self.db_log.info('%s,%s,%s,%s行,更新成功\n' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                    else:
                        self.dbObj.rollback()
                if insert_sql and not update_sql:
                    self.cur.execute(insert_sql, data_dict)
                    row = self.cur.rowcount
                    if row > 0:
                        self.dbObj.commit()
                        self.dataQ.record_db_ok_times()
                        self.db_log.info('%s,%s,%s,%s行,插入成功' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                    else:
                        self.dbObj.rollback()
        except Exception as e:
            self.dbObj.rollback()
            datas = {the_asin_or_kw: data_dict}
            self.debug_log.error('%s,%s,%s,入库失败,原因%s,失败数据[%s];' % (
            return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, e, datas))
            self.db_log.error('%s,%s,%s,入库失败,原因%s,失败数据[%s];' % (
            return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, e, datas))
            return datas

    @staticmethod
    def save_data_to_db_pool(dbObj, cur, db_log, debug_log, dataQ, update_sql, insert_sql, the_asin_or_kw, data_dict, db_name='', md5key=''):
        dataQ.record_dbSum_times()
        # print(the_asin_or_kw, data_dict)
        try:
            if update_sql and insert_sql:
                cur.execute(update_sql, data_dict)
                row = cur.rowcount
                if row > 0:
                    dataQ.record_db_ok_times()
                    db_log.info('%s,%s,%s,%s行,更新成功' %
                                     (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                    # 评论进程标记第一次
                    if md5key:
                        dataQ.the_reviews_first_download(md5key)
                else:
                    cur.execute(insert_sql, data_dict)
                    row = cur.rowcount
                    if row > 0:
                        dataQ.record_db_ok_times()
                        db_log.info('%s,%s,%s,%s行,插入成功' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                        # 评论进程标记第一次
                        if md5key:
                            dataQ.the_reviews_first_download(md5key)
            else:
                if update_sql and not insert_sql:
                    cur.execute(update_sql, data_dict)
                    row = cur.rowcount
                    if row > 0:
                        dataQ.record_db_ok_times()
                        db_log.info('%s,%s,%s,%s行,更新成功\n' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
                elif insert_sql and not update_sql:
                    cur.execute(insert_sql, data_dict)
                    row = cur.rowcount
                    if row > 0:
                        dataQ.record_db_ok_times()
                        db_log.info('%s,%s,%s,%s行,插入成功' %
                                         (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, row))
        except Exception as e:
            datas = {the_asin_or_kw: data_dict}
            debug_log.error('%s,%s,%s,入库失败,原因%s,失败数据[%s];' % (
            return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, e, datas))
            db_log.error('%s,%s,%s,入库失败,原因%s,失败数据[%s];' % (
            return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin_or_kw, e, datas))
            return datas

    # 标记爬取时间
    def crawler_tm(self, asin_or_kw, tm_type):
        tm = int(DataOutput.get_redis_time() / 1000)
        db_name = ''
        insert_sql = ''
        update_sql = ''
        data_dict = {}
        if tm_type == 'goods':
            data_dict = {'asin': asin_or_kw, 'info_tm_crawler': tm}
            db_name = 'public.amazon_product_monitor.info_tm_crawler'
            update_sql = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
        if tm_type == 'reviews':
            data_dict = {'asin': asin_or_kw, 'comment_tm_crawler': tm}
            db_name = 'public.amazon_product_monitor.comment_tm_crawler'
            update_sql = "update public.amazon_product_monitor set comment_tm_crawler=%(comment_tm_crawler)s where asin=%(asin)s;"
        if tm_type == 'tosell':
            data_dict = {'asin': asin_or_kw, 'tosell_tm_crawler': tm}
            db_name = 'public.amazon_product_monitor.tosell_tm_crawler'
            update_sql = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
        if tm_type == 'keyword':
            data_dict = {'kw': asin_or_kw, 'crawler_tm': tm}
            db_name = 'public.amazon_keyword_monitor.crawler_tm'
            update_sql = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
        if data_dict and update_sql:
            self.save_data_to_db(update_sql, insert_sql, asin_or_kw, data_dict, db_name=db_name)

    # 获取md5码
    @staticmethod
    def get_md5_key(value_str):
        '''value_str 必须是一个字符串, 只返回其中16位md5码, 节约内存'''
        return hashlib.md5(value_str.encode('utf-8')).hexdigest()[8: -8]

    @staticmethod
    def save_data_to_file(datas=None, filename='data.data'):
        DATA_FILE = os.path.join(DATA_DIR, filename)
        if datas:
            with open(DATA_FILE, 'a') as f:
                f.write(datas)

    @staticmethod
    def record_not_found_goods(the_asin, data_type=''):
        data_dict = {'asin': the_asin, 'asin_state': 0, 'getinfo_tm': int(DataOutput.get_redis_time())}
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            sql = "update public.amazon_product_data set \
price=0, sale_price=0, sname='', ts_min_price=0, to_sell=0, byb=0, bsr=0, rc=0, rrg=0,\
r5p=0, r4p=0, r3p=0, r2p=0, r1p=0, feature='', brand='', release_date=0,\
collect_tm=0, variant='', cart_price=0, quantity=0, seller_id='',\
asin_state=%(asin_state)s, getinfo_tm=%(getinfo_tm)s, is_sync=0, crawler_state=1  where asin=%(asin)s;"
            cur.execute(sql, data_dict)
            row = cur.rowcount
            if row > 0:
                conn.commit()
                print('\namazon_product_data,%s,%s,%s行,更新成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                sql1 = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
                data_dict1 = {'asin': the_asin, 'info_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                cur.execute(sql1, data_dict1)
                conn.commit()
                # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                # print(cur.fetchall())
            else:
                conn.rollback()
                sql = "INSERT INTO public.amazon_product_data(asin, asin_state, getinfo_tm, crawler_state) VALUES (%(asin)s, %(asin_state)s, %(getinfo_tm)s, 1);"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                if row > 0:
                    conn.commit()
                    sql1 = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
                    data_dict1 = {'asin':the_asin, 'info_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    print('\namazon_product_data,%s,%s,%s行,插入成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                else:
                    conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            datas = {the_asin: data_dict}
            # print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def record_disabled_goods(the_asin, data_type=''):
        if data_type == 'discrad':
            data_dict = {'asin': the_asin, 'asin_state': -1, }
            conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
            cur = conn.cursor()
            try:
                sql = "update public.amazon_product_data set asin_state=%(asin_state)s, is_sync=0, crawler_state=2  where asin=%(asin)s;"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                if row > 0:
                    print('\namazon_product_data,%s,%s,%s行,更新成功\n' % (
                    return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                    sql1 = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
                    data_dict1 = {'asin': the_asin, 'info_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                    # print(cur.fetchall())
                else:
                    data_dict['getinfo_tm'] = int(DataOutput.get_redis_time())
                    sql = "INSERT INTO public.amazon_product_data(asin, asin_state, getinfo_tm, crawler_state) VALUES (%(asin)s, %(asin_state)s, %(getinfo_tm)s, 2);"
                    cur.execute(sql, data_dict)
                    row = cur.rowcount
                    if row > 0:
                        sql1 = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
                        data_dict1 = {'asin': the_asin, 'info_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                        cur.execute(sql1, data_dict1)
                        conn.commit()
                        print('\namazon_product_data,%s,%s,%s行,插入成功\n' % (
                        return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                    else:
                        conn.rollback()
                cur.close()
                conn.close()
            except Exception as e:
                conn.rollback()
                cur.close()
                conn.close()
                datas = {the_asin: data_dict}
                # print('失败 amazon_product_data ', e, datas)
            cur.close()
            conn.close()

    @staticmethod
    def record_disabled_tosell(the_asin, data_type=''):
        data_dict = {'asin': the_asin, 'getinfo_tm': int(DataOutput.get_redis_time())}
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            sql = "update public.amazon_product_data_tosell set is_sync=0, crawler_state=2, getinfo_tm=%(getinfo_tm)s where asin=%(asin)s;"
            print(sql)
            cur.execute(sql, data_dict)
            row = cur.rowcount
            print(1, row)
            if row > 0:
                conn.commit()
                print('\namazon_product_data_tosell,%s,%s,%s行,更新成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                sql1 = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
                data_dict1 = {'asin': the_asin, 'tosell_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                cur.execute(sql1, data_dict1)
                conn.commit()
                # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                # print(cur.fetchall())
            else:
                conn.rollback()
                sql = "INSERT INTO public.amazon_product_data_tosell(asin, getinfo_tm, crawler_state) VALUES (%(asin)s, %(getinfo_tm)s, 2);"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                print(2, row)
                if row > 0:
                    conn.commit()
                    sql1 = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
                    data_dict1 = {'asin':the_asin, 'tosell_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    print('\namazon_product_data_tosell,%s,%s,%s行,插入成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                else:
                    conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            datas = {the_asin: data_dict}
            print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def record_not_found_tosell(the_asin, data_type=''):
        data_dict = {'asin': the_asin, 'getinfo_tm': int(DataOutput.get_redis_time())}
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            sql = "update public.amazon_product_data_tosell set sn=0, fba_sn=0, plow=0, plows='', plows_id='', \
sname='', seller_id='', is_sync=0, crawler_state=1, getinfo_tm=%(getinfo_tm)s where asin=%(asin)s;"
            print(sql)
            cur.execute(sql, data_dict)
            row = cur.rowcount
            print(1, row)
            if row > 0:
                conn.commit()
                print('\namazon_product_data_tosell,%s,%s,%s行,更新成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                sql1 = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
                data_dict1 = {'asin': the_asin, 'tosell_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                cur.execute(sql1, data_dict1)
                conn.commit()
                # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                # print(cur.fetchall())
            else:
                conn.rollback()
                sql = "INSERT INTO public.amazon_product_data_tosell(asin, getinfo_tm, crawler_state) VALUES (%(asin)s, %(getinfo_tm)s, 1);"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                print(2, row)
                if row > 0:
                    conn.commit()
                    sql1 = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
                    data_dict1 = {'asin':the_asin, 'tosell_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    print('\namazon_product_data_tosell,%s,%s,%s行,插入成功\n' % (return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_asin, row))
                else:
                    conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            datas = {the_asin: data_dict}
            print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def record_disabled_keyword(the_kw, data_type=''):
        data_dict = {'kw': the_kw, 'getinfo_tm': int(DataOutput.get_redis_time())}
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            sql = "update public.amazon_keyword_data set kw=%(kw)s, is_sync=0, crawler_state=2 where kw=%(kw)s;"
            cur.execute(sql, data_dict)
            row = cur.rowcount
            if row > 0:
                conn.commit()
                print('\namazon_keyword_data,%s,%s,%s行,更新成功\n' % (
                return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_kw, row))
                sql1 = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
                data_dict1 = {'asin': the_kw, 'crawler_tm': int(DataOutput.get_redis_time() / 1000)}
                cur.execute(sql1, data_dict1)
                conn.commit()
                # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                # print(cur.fetchall())
            else:
                conn.rollback()
                sql = "INSERT INTO public.amazon_keyword_data(kw, getinfo_tm, crawler_state) VALUES (%(kw)s, %(getinfo_tm)s, 2);"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                if row > 0:
                    conn.commit()
                    sql1 = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
                    data_dict1 = {'asin': the_kw, 'crawler_tm': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    print('\namazon_keyword_data,%s,%s,%s行,插入成功\n' % (
                    return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_kw, row))
                else:
                    conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            datas = {the_kw: data_dict}
            # print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def record_not_found_keyword(the_kw, data_type=''):
        data_dict = {'kw': the_kw, 'search_num': -2, 'getinfo_tm': int(DataOutput.get_redis_time())}
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            sql = "update public.amazon_keyword_data set kw=%(kw)s, search_num=%(search_num)s, getinfo_tm=%(getinfo_tm)s, is_sync=0, crawler_state=1 where kw=%(kw)s;"
            cur.execute(sql, data_dict)
            row = cur.rowcount
            if row > 0:
                conn.commit()
                print('\namazon_keyword_data,%s,%s,%s行,更新成功\n' % (
                return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_kw, row))
                sql1 = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
                data_dict1 = {'asin': the_kw, 'crawler_tm': int(DataOutput.get_redis_time() / 1000)}
                cur.execute(sql1, data_dict1)
                conn.commit()
                # cur.execute("select * from amazon_product_data where asin=%s;", (the_asin,))
                # print(cur.fetchall())
            else:
                conn.rollback()
                sql = "INSERT INTO public.amazon_keyword_data(kw, search_num, getinfo_tm, crawler_state) VALUES (%(kw)s, %(search_num)s, %(getinfo_tm)s, 1);"
                cur.execute(sql, data_dict)
                row = cur.rowcount
                if row > 0:
                    conn.commit()
                    sql1 = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"
                    data_dict1 = {'asin': the_kw, 'crawler_tm': int(DataOutput.get_redis_time() / 1000)}
                    cur.execute(sql1, data_dict1)
                    conn.commit()
                    print('\namazon_keyword_data,%s,%s,%s行,插入成功\n' % (
                    return_PST().strftime("%Y-%m-%d %H:%M:%S"), the_kw, row))
                else:
                    conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            datas = {the_kw: data_dict}
            # print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def record_not_found_reviews(the_asin, data_type=''):
        data_dict = {'asin': the_asin, 'comment_tm_crawler': int(DataOutput.get_redis_time() / 1000)}
        db_name = 'public.amazon_product_monitor.comment_tm_crawler'
        update_sql = "update public.amazon_product_monitor set comment_tm_crawler=%(comment_tm_crawler)s where asin=%(asin)s;"
        conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
        cur = conn.cursor()
        try:
            cur.execute(update_sql, data_dict)
            row = cur.rowcount
            if row > 0:
                conn.commit()
                print('%s,%s,%s,%s行,更新成功' %
                                 (return_PST().strftime("%Y-%m-%d %H:%M:%S"), db_name, the_asin, row))
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            # print('失败 amazon_product_data ', e, datas)
        cur.close()
        conn.close()

    @staticmethod
    def update_getdata_tm(data_dict, data_type, dataQ=None, db_log=None):
        sql = ''
        db_type = ''
        if data_type == 'goods':
            db_type = 'public.amazon_product_monitor.info_tm_crawler'
            sql = "update public.amazon_product_monitor set info_tm_crawler=%(info_tm_crawler)s where asin=%(asin)s;"
        if data_type == 'reviews':
            db_type = 'public.amazon_product_monitor.comment_tm_crawler'
            sql = "update public.amazon_product_monitor set comment_tm_crawler=%(comment_tm_crawler)s where asin=%(asin)s;"
        if data_type == 'tosell':
            db_type = 'public.amazon_product_monitor.tosell_tm_crawler'
            sql = "update public.amazon_product_monitor set tosell_tm_crawler=%(tosell_tm_crawler)s where asin=%(asin)s;"
        if data_type == 'keyword':
            db_type = 'public.amazon_keyword_monitor.crawler_tm'
            sql = "update public.amazon_keyword_monitor set crawler_tm=%(crawler_tm)s where kw=%(kw)s;"

        if sql:
            conn = psycopg2.connect(**DATADB_CONFIG[BASE_TYPE])
            cur = conn.cursor()
            cur.execute(sql, data_dict)
            row = cur.rowcount
            if row > 0:
                if db_log:
                    db_log.info('爬虫数据更新时间 %s,%s,%s,%s行,标记成功' %
                            (db_type, return_PST().strftime("%Y-%m-%d %H:%M:%S"), data_type, row))
                conn.commit()
            else:
                conn.rollback()
            cur.close()
            conn.close()


if __name__ == '__main__':
    print(DataOutput.get_redis_time())
    # DataOutput.record_disabled_goods('B07514SYF1')
    # DataOutput.record_not_found_goods('B07514SYF1')
    # DataOutput.record_not_found_tosell('B07514SYF1')
    # DataOutput.record_disabled_tosell('B001TKOHMM')
    # DataOutput.record_disabled_tosell('B07514SYF1')
    # DataOutput.record_disabled_keyword('blue opal jewelry')