# !/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import hashlib
from urllib import parse
import time
from app_code.get_gorgon import gorgon_hook_prepare
import warnings

warnings.filterwarnings("ignore")

ghp = gorgon_hook_prepare()

url = "https://aweme.snssdk.com/aweme/v1/search/item/"

data = {
    'keyword': '口红',
    'offset': '20',
    'count': '10',
    'source': 'video_search',
    'from_user': '',
    'search_source': 'switch_tab',
    'is_pull_refresh': '1',
    'hot_search': '0',
    'search_id': '',
    'query_correct_type': '1',
    'is_filter_search': '0',
    'sort_type': '0',
    'publish_time': '0',
    'enter_from': 'homepage_hot',
    'backtrace': '',
    'user_avatar_shrink': '64_64',
    'video_cover_shrink': '372_496',
}

data_new_s = ''.join(['{}={}&'.format(parse.quote(k), parse.quote(v)) for k, v in data.items()])[:-1]
print(data_new_s)
STUB = hashlib.md5(data_new_s.encode("utf-8")).hexdigest().upper()
print("STUB : ", STUB)

_rticket = int(time.time() * 1000)
# print(str(_rticket)[:10])
# print(str(_rticket))

params = {
    'os_api': '25',
    'device_type': 'VOG-AL00',
    'ssmix': 'a',
    'manifest_version_code': '130201',
    'dpi': '240',
    'uuid': '840887694567161',
    'app_name': 'aweme',
    'version_name': '13.2.0',
    'ts': str(int(time.time() * 1000))[:10],
    'cpu_support64': 'false',
    'app_type': 'normal',
    'ac': 'wifi',
    'appTheme': 'dark',
    'host_abi': 'armeabi-v7a',
    'channel': 'wandoujia_1128_1022',
    'update_version_code': '13209900',
    '_rticket': str(int(time.time() * 1000)),
    'device_platform': 'android',
    'iid': '3060668478796920',
    'version_code': '130200',
    'mac_address': '74:34:46:12:76:17',
    'cdid': '0c2f6f02-1fde-4187-958d-613d1889d351',
    'openudid': 'i3ldg8li2l88f5k6',
    'device_id': '1125528013119789',
    'resolution': '720*1280',
    'device_brand': 'HUAWEI',
    'language': 'zh',
    'os_version': '7.1.2',
    'aid': '1128',
    'mcc_mnc': '46000',
}

params_new_s = ''.join(['{}={}&'.format(parse.quote(k), parse.quote(v)) for k, v in params.items()])[:-1]
a2 = hashlib.md5(params_new_s.encode("utf-8")).hexdigest()
# print("a2 : ", a2)

headers = {
    'X-SS-STUB': STUB,
    'Accept-Encoding': 'gzip',
    'passport-sdk-version': '18',
    'sdk-version': '2',
    'X-SS-REQ-TICKET': str(int(time.time() * 1000)),
    'Cookie': 'install_id=3060668478796920; ttreq=1$2df8fc1fde5a8bc399bdb026fa12d0628f7a4ba0; odin_tt=c6276c2392d037b60514831f03f662c08fb69c8b1191c88f07b0661eb372e8427dbd3b3f711754f917560cf62a9796f85366ed307a38d609bafb897fecbe77ae; MONITOR_WEB_ID=9f72789b-bf5d-4a73-b32d-d66f6ee43e95',
    # 'X-Gorgon': '0408c04a40119c26f25bcf16be902f1251949bc94d90d8069b5c',
    'X-Khronos': str(int(time.time() * 1000))[:10],
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Content-Length': '296',
    'Host': 'aweme.snssdk.com',
    'Connection': 'Keep-Alive',
    'User-Agent': 'okhttp/3.10.0.1',
    'Accept': None
}
str7 = hashlib.md5(headers.get("Cookie").encode("utf-8")).hexdigest()
# print("str7 : ", str7)

str8 = "00000000000000000000000000000000"  # 未登录状态的值
# str8 = hashlib.md5(headers.get("Cookie").split("sessionid=")[1].encode("utf-8")).hexdigest()
# print("str8 : ", str8)

str_res = a2 + STUB + str7 + str8

gorgon = ghp.getsig(int(str(_rticket)[:10]), str_res)
print("gorgon : ", gorgon)
headers['X-Gorgon'] = gorgon

response = requests.post(url, headers=headers, params=params, data=data, verify=False)
print(response.text)

# %E9%B8%A1%E8%9B%8B%E9%A5%BC%E5%81%9A%E6%B3%95
# print(parse.quote('鸡蛋饼做法'))
