#!/usr/bin/env python
# -*- coding: utf-8 -*-


import redis
from config.config import redis_conf


def get_redis_conn():
    """
        返回redis连接

        Returns:
        * conn:    (redis.Redis) - Redis连接
    """
    conn = redis.Redis(
        host=redis_conf.get('HOST', 'localhost'),
        port=redis_conf.get('PORT', 6379)
    )
    return conn
