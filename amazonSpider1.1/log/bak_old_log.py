#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import os
import re
import pytz
from datetime import datetime


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OLD_LOG_DIR = os.path.join(BASE_DIR, 'oldLog')
time_zone = pytz.timezone('America/Los_Angeles')
today = datetime.now(time_zone)


def bak_log():
    today_str = today.strftime("%Y%m%d")
    today_dir = os.path.join(OLD_LOG_DIR, '%slog' % (today_str))
    filenames = os.listdir(BASE_DIR)
    print(today_str, type(today_str))
    print(today_dir)
    print(filenames)

    if not os.path.exists(OLD_LOG_DIR):
        os.makedirs(OLD_LOG_DIR)
    if not os.path.exists(today_dir):
        os.makedirs(today_dir)
    logfiles = []
    for filename in filenames:
        if re.search('.*?\.[log|csv]+$', filename):
            logfiles.append(filename)
    for logfile in logfiles:
        log = os.path.join(BASE_DIR, '%s' % (logfile))
        print(log)
        cpshell = 'cp %s %s' % (log, today_dir)
        emshell = '"" > %s' % (log)
        print(cpshell)
        print(emshell)
        os.system(cpshell)
        os.system(emshell)


if __name__ == '__main__':
    print(BASE_DIR)
    if today.hour == 23:
        bak_log()
    else:
        print('当前太平洋时间为%s, 未到日志切割时间\n' % (today.strftime('%Y-%m-%d %H:%M:%S')))