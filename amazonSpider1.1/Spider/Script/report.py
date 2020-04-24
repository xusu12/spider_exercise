#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
sys.path.append("../../")
import os
import time
import pickle

from conf.setting import REPORT_DIR
from utils.util import Logger, GetRedis, IpQueue, DataQueue, UrlQueue, return_PST


def report(ipQ, urlQ, dataQ, debug_log):
    '''定时器, 每2小时启动一次'''
    urlSet = urlQ.retrieve_asinAndKwSet()
    urlSum = len(urlSet)
    successSet = urlQ.retrieve_successAsinKwSet()
    successNum = len(successSet)
    defeatedSet = urlQ.retrieve_defeated_urlSet()
    defeatedNum = len(defeatedSet)
    defeatedRatio = 0
    successRatio = 0
    if urlSum > 0:
        successRatio = (successNum / urlSum) * 100
        defeatedRatio = (defeatedNum / urlSum) * 100

    if urlSum - successNum - defeatedNum > 0:
        DisabledDict = {}
        RobotChekDict = {}
        useDict = {}
        ipSetDisabled = ipQ.return_disabled_IP()
        if ipSetDisabled:
            for ip in ipSetDisabled:
                DisabledDict[str(ip[0]).split("'")[1]] = ip[1]
        print('\nDisabledDict', DisabledDict)

        ipSetRobotChek = ipQ.return_RobotChek_IP()
        if ipSetRobotChek:
            for ip in ipSetRobotChek:
                RobotChekDict[str(ip[0]).split("'")[1]] = ip[1]
        print('\nRobotChekDict', RobotChekDict)

        ipUseTimes = ipQ.return_use_times()
        if ipUseTimes:
            for ip in ipUseTimes:
                useDict[str(ip[0]).split("'")[1]] = ip[1]
        print('\nuseDict', useDict)
        urlNum = urlQ.get_html_ok_times()
        goodsNum = urlQ.get_goodsHtml_ok_times()
        keywordNum = urlQ.get_keywordHtml_ok_times()
        tosellNum = urlQ.get_tosellHtml_ok_times()
        reviewsNum = urlQ.get_reviewsHtml_ok_times()
        print('\nurlNum', urlNum)
        if not urlNum:
            urlNum = 0
        dataNum = dataQ.get_data_ok_times()
        dbSumNum = dataQ.get_dbSum_times()
        dbOkNum = dataQ.get_db_ok_times()
        goodsOkNum = dataQ.get_goods_ok_times()
        reviewsOkNum = dataQ.get_reviews_ok_times()
        tosellOkNum = dataQ.get_tosell_ok_times()
        tosellNotFoundNum = urlQ.get_tosell_notFound_times()
        keywordOkNum = dataQ.get_keyword_ok_times()
        keywordNotFoundNum = dataQ.get_keyword_not_fund_times()
        dataRatio = dbRatio = goodsRatio = reviewsRatio = tosellRatio = keywordRatio = 0
        if urlNum > 0:
            dataRatio = dataNum / urlNum
        if dbSumNum > 0:
            dbRatio = dbOkNum / dbSumNum
        if goodsNum > 0:
            goodsRatio = goodsOkNum / goodsNum
        if reviewsNum > 0:
            reviewsRatio = reviewsOkNum / reviewsNum
        if tosellNum > 0:
            tosellRatio = tosellOkNum / (tosellNum - tosellNotFoundNum)
        if keywordNum > 0:
            keywordRatio = keywordOkNum / (keywordNum - keywordNotFoundNum)
        print('\ndataNum', dataNum)
        if not dataNum:
            dataNum = 0
        pstNow = return_PST()
        timeNow = pstNow.strftime("%Y-%m-%d %H:%M:%S")
        dateNow = pstNow.strftime("%Y_%m_%d")
        statFile = os.path.join(REPORT_DIR, 'statistics_%s.csv' % (dateNow))
        try:
            with open(statFile, 'a') as f:
                f.write('\r\n[%s] 分时报告,' % (timeNow))
                f.write('[任务总数: ,%s,], [已完成: ,%s,], [完成度: ,%.2f%%,], [已丢弃(无法访问的次数超过20): ,%s,], [丢弃率: ,%.2f%%,],' %
                        (urlSum, successNum, successRatio, defeatedNum, defeatedRatio))
                f.write('[网络请求成功总次数: %s], [数据解析成功总次数: ,%s,], [总成功率: ,%.2f%%,], \n' %
                        (urlNum, dataNum, dataRatio * 100))
                f.write('[数据入库总次数: %s], [入库成功总次数: ,%s,], [成功率: ,%.2f%%,], \n' %
                        (dbSumNum, dbOkNum, dbRatio * 100))
                f.write('[goods 网络请求成功次数: ,%s,], [goods 数据解析成功次数: ,%s,], [goods 成功率: ,%.2f%%,], \n' %
                        (goodsNum, goodsOkNum, goodsRatio * 100))
                f.write('[reviews 网络请求成功次数: ,%s,], [reviews 数据解析成功次数: ,%s,], [reviews 成功率: ,%.2f%%,], \n' %
                        (reviewsNum, reviewsOkNum, reviewsRatio * 100))
                f.write('[tosell 网络请求成功次数: ,%s,], [tosell 不存在次数: ,%s,], [tosell 数据解析成功次数: ,%s,], [tosell 成功率(排除跟卖不存在的情况): ,%.2f%%,], \n' %
                        (tosellNum, tosellNotFoundNum, tosellOkNum, tosellRatio * 100))
                f.write('[keyword 网络请求成功次数: ,%s,], [keyword 不存在次数: ,%s,], [keyword 数据解析成功次数: ,%s,], [keyword 成功率(排除关键字不存在的情况): ,%.2f%%,], \n' %
                    (keywordNum, keywordNotFoundNum, keywordOkNum, keywordRatio * 100))
                urlQ.pop_html_ok_times()
                urlQ.pop_goodsHtml_ok_times()
                urlQ.pop_reviewsHtml_ok_times()
                urlQ.pop_tosellHtml_ok_times()
                urlQ.pop_keywordHtml_ok_times()
                urlQ.pop_tosell_notFound_times()
                dataQ.pop_data_ok_times()
                dataQ.pop_dbSum_times()
                dataQ.pop_db_ok_times()
                dataQ.pop_goods_ok_times()
                dataQ.pop_reviews_ok_times()
                dataQ.pop_tosell_ok_times()
                dataQ.pop_keyword_ok_times()
                dataQ.pop_keyword_not_fund_times()
                if useDict and type(useDict) is dict:
                    for item in useDict:
                        ip = item
                        useNum = useDict[item]
                        disabledNum = 0
                        RobotChekNum = 0
                        if item in DisabledDict:
                            disabledNum = DisabledDict[item]
                        if item in RobotChekDict:
                            RobotChekNum = RobotChekDict[item]
                        if useNum > 0:
                            RobotRatio = RobotChekNum / useNum
                            disabledRatio = disabledNum / useNum
                        else:
                            RobotRatio = disabledRatio = 0
                        f.write('Ip [,%s,] 总使用次数 ,%s, 遭遇验证码次数 ,%s, 验证码几率: ,%.2f%%, 请求失败次数 ,%s, 失败几率: ,%.2f%%, \n' %
                                (ip, useNum, RobotChekNum, RobotRatio * 100, disabledNum, disabledRatio * 100))
                        ipQ.pop_use_times(item)
                        if disabledNum > 0:
                            ipQ.pop_disabled_IP(item)
                        if RobotChekNum > 0:
                            ipQ.pop_RobotChek_IP(item)
            debug_log.war('%s 报告生成成功 %s, \n' % (statFile, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        except Exception as e:
            debug_log.error('生成报告时 [%s], \n' % (e))
    else:
        key = 'isStatistics'
        key_type = 'statistics'
        statistics = urlQ._get_value_from_string(key, key_type)
        if statistics:
            isStatistics = pickle.loads(statistics)
        else:
            isStatistics = False
        # 如果未下载商品为零， 且未出过报告， 则出一份结束报告。
        if not isStatistics:
            pstNow = return_PST()
            endtime = pstNow.strftime("%Y-%m-%d %H:%M:%S")
            dateNow = pstNow.strftime("%Y_%m_%d")
            statFile = os.path.join(REPORT_DIR, 'statistics_%s.csv' % (dateNow))
            msg = '[%s] [结束报告] 任务总数 %s, 成功总数 %s, 完成度 %.2f%%, 丢弃总数 %s, 丢弃率 %.2f%%, 任务结束！' %\
                  (endtime, urlSum, successNum, successRatio, defeatedNum, defeatedRatio)
            with open(statFile, 'a') as f:
                f.write(msg)
            # 将结束报告设置为True
            value = pickle.dumps(True)
            urlQ._set_key_value_to_string(key, value, key_type, overtime=86400)


if __name__ == '__main__':
    debug_log = Logger()
    myRedis = GetRedis().return_redis(debug_log)
    ipQ = IpQueue(myRedis, debug_log)
    dataQ = DataQueue(myRedis, debug_log)
    urlQ = UrlQueue(myRedis, debug_log)
    report(ipQ=ipQ, urlQ=urlQ, dataQ=dataQ, debug_log=debug_log)
