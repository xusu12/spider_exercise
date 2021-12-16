# !/usr/bin/env python
# -*- coding:utf-8 -*-


import time
import requests
import datetime
from xiaohongshu_shangpin_zhongcaoshuliang import stub_hook_prepare
import warnings

warnings.filterwarnings("ignore")

script = stub_hook_prepare()
search_id = script.getsig()


class XhsShopNum(object):

    def __init__(self, keyword, page, page_pos):
        self.keyword = keyword
        self.page = page
        self.page_pos = page_pos
        self.all_num = []

    def get_fav_count(self):
        t = str(int(time.time()))
        url = "https://www.xiaohongshu.com/api/store/ps/products/v3"

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            # 'cookie': 'xhsTrackerId=3b7da09f-7f7e-4f0f-cf13-2169b185d1f3; smidV2=20201024003449d11db11da0c4034f3d92183d5a37d1c5007c8e0cd8ff5bb50; xhs_spses.5dde=*; xhsTracker=url=question&searchengine=baidu; Hm_lvt_d0ae755ac51e3c5ff9b1596b0c09c826=1603278962,1603474400; Hm_lpvt_d0ae755ac51e3c5ff9b1596b0c09c826=1603474400; xhs_spid.5dde=ba25c1eb681ff31c.1603278962.3.1603474450.1603471173.5f82df1a-9e9d-41e8-acdb-43378f0fdba7',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Pixel Build/OPM1.171019.011) Resolution/1080*1920 Version/6.66.0 Build/6660088 Device/(Google;Pixel) discover/6.66.0 NetType/WiFi',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        }
        print("self.all_num : ", self.all_num)
        pp = 0
        if self.page > 1:
            pp = sum(self.all_num) + 1
        self.page_pos = pp
        print("pp : ", self.page_pos)
        params = {
            'keyword': self.keyword,
            'filters': '[]',  # 非自营 种草数量
            # 'filters': '[{"tags":["self_conduct"],"type":"self_conduct"}]',  # 自营 销量 种草数
            'page': str(self.page),
            'size': '20',

            # 'sort': 'fav_count',  # 种草数量
            'sort': 'sales_qty',  # 销量 种草数
            # 'sort': 'default',  # 默认 种草数
            # 'sort': 'price_desc',  # 价格降序 种草数
            # 'sort': 'price_asc',  # 价格升序 种草数
            # 'sort': 'new_arrival',  # 新品优先 种草数

            'source': 'store_feed',
            'search_id': search_id,
            # 'search_id': '5F984F1D79CE3DD8680D8EA317ECA3A4',
            'page_pos': str(self.page_pos),
            # 'store_id': '',
            # 'geo': 'eyJsYXRpdHVkZSI6MC4wMDAwMDAsImxvbmdpdHVkZSI6MC4wMDAwMDB9',
            # 'fid': '160346800710cc5135fee74076a4fc529237cd0b1db2',
            # 'device_fingerprint': '20200930234755c974816086d953ec14b52cb6740970ab012a7a13c6155e83',
            # 'device_fingerprint1': '20200930234755c974816086d953ec14b52cb6740970ab012a7a13c6155e83',
            # 'launch_id': '1603468995',
            # 'tz': 'Asia/Shanghai',
            # 'channel': 'YingYongBao',
            # 'versionName': '6.66.0',
            # 'deviceId': '6324f43c-c2f3-37b3-b89a-30e84297faa1',
            'platform': 'android',
            'sid': 'session.1603471684063966683668',
            'identifier_flag': '0',
            't': t,
            # 't': '1603474511',
            'x_trace_page_current': 'search_result_goods',
            'lang': 'zh-Hans',
        }

        response = requests.get(url, headers=headers, params=params, verify=False)
        # print(response.text)
        response_data = response.json().get("data")
        total_count = response_data.get("total_count")
        print("total_count : ", total_count)
        items = response_data.get("items")
        self.all_num.append(len(items))

        if len(items) > 0:
            for item in items:
                fav_info = item.get("fav_info")
                # if fav_info.get("show_fav") is True:
                result = {
                    "_id": item.get("id"),
                    "title": item.get("title"),
                    # "desc": item.get("desc"),
                    "count": fav_info.get("fav_count"),
                    "update_at": datetime.datetime.now(),
                }
                print(result)
        if self.page == 1:
            if total_count > 20:
                time.sleep(5)
                for page in range(2, (total_count // 20) + 1 + 1):
                    self.page = page
                    self.get_fav_count()
                    if self.page == 2:
                        break


if __name__ == '__main__':
    keyword = "面膜"
    page = 1
    page_pos = 0
    xhs = XhsShopNum(keyword, page, page_pos)
    xhs.get_fav_count()
