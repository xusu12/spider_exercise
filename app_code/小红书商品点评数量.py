# !/usr/bin/env python
# -*- coding:utf-8 -*-


import time
import json
import requests
import datetime
import warnings

warnings.filterwarnings("ignore")

url = "https://www.xiaohongshu.com/api/store/review/5d9c5f830cf9a140b3f5d499/product_review"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': 'xhsTrackerId=3b7da09f-7f7e-4f0f-cf13-2169b185d1f3; smidV2=20201024003449d11db11da0c4034f3d92183d5a37d1c5007c8e0cd8ff5bb50; xhsTracker=url=question&searchengine=baidu; Hm_lvt_d0ae755ac51e3c5ff9b1596b0c09c826=1603278962,1603474400; xhs_spid.5dde=ba25c1eb681ff31c.1603278962.3.1603474450.1603471173.5f82df1a-9e9d-41e8-acdb-43378f0fdba7',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
}

params = {
    'page': '0',
    'per_page': '3',
    'tab': '1',
    'sid': 'session.1603471684063966683668',
}

response = requests.get(url, headers=headers, params=params, verify=False)
# print(response.text)

print(json.dumps(json.loads(response.text), indent=4, ensure_ascii=False))








