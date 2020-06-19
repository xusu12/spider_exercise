#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# logger.py
# @Author : YingzhiPeng
# @Date   : 2018-4-3 13:48:05

import os
import logging
from functools import partial
from logging.handlers import WatchedFileHandler


class SpiderLogging(object):
    def __init__(self, logger_name):
        # 创建一个logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        # 项目存放log的路径
        project_log_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'log/')

        # 每个爬虫创建一个文件夹存放对应的日志
        spider_log_path = os.path.join(project_log_path, logger_name)
        # 如果没有这个文件夹  就创建
        if not os.path.exists(spider_log_path):
            os.mkdir(spider_log_path)

        # 创建一个handler，用于写入日志文件
        logname = spider_log_path + '/' + logger_name + '.log'  # 指定输出的日志文件名
        fh = logging.FileHandler(logname, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
        fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s-%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_logger(self):
        """定义一个函数，回调logger实例"""
        return self.logger


def get_stream_logger(name, level=logging.INFO):
    """
    返回stream的logger

    Params:
        * name:           (string) - 日志名称
        * level:          (int) - 日志级别

    Returns:
        * logger:         (Logger) - 日志对象

    """

    logger = logging.getLogger(name)

    handler = logging.StreamHandler()
    formater = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s')
    handler.setFormatter(formater)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    logger = SpiderLogging("auto_login").get_logger()
    logger.debug("User %s is loging" % 'jeck')

