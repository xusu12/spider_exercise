#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import time


def func(fileName):
    flist = []
    with open(fileName, 'r') as f:
        flist = f.readlines()

    if flist:
        rList = []
        # print(flist)
        for f in flist:
            r = f.split('，') or f.split(',')
            rList.append(r)

            # print(r)
        if rList:
            amount = []
            succeed = []
            for i in rList:
                c = i[0].split('数')[1].split('.')[0]
                amount.append(int(c))
                d = i[1].split('数')[2].split('.')[0]
                succeed.append(int(d))
                # print('c', c)
                # print('d', d)
            # print('amount', amount)
            # print('succeed', succeed)
            print('网络请求成功次数： %s' % (sum(amount)))
            print('获取数据成功次数： %s' % (sum(succeed)))
            print('遇到验证码次数： %s' % (sum(amount) - sum(succeed)))

            successRate = sum(succeed) / sum(amount) * 100
            print('总成功率： %.2f%%' % (successRate))

if __name__ == '__main__':
    func('成功率汇总.txt')