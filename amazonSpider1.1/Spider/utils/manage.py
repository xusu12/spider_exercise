#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
import os
import time


def func():
    while True:
        plist = [
            '1 设置休眠间隔',
            '2 查看剩余任务数',
            '3 查看成功任务数',
            '4 导入新ip',
            '5 删除旧ip'
        ]
        print(

        )
        input('%s\n请输入相应数字: ' % ('\n'.join(plist)))

if __name__ == '__main__':
    func()