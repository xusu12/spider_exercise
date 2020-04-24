"""
    IP反爬-2
"""
import requests
import xml
import pymongo
import time
import redis
import random
from lxml import etree


mongodb_conn = pymongo.MongoClient('127.0.0.1', 27017)
proxy_col = mongodb_conn.pdd.mogu_proxy_pool
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)
sum = 0

for i in range(1, 1001):
    # 每页的数据如果请求不成功  不断重试
    while True:
        try:
            print('当前页面是{}'.format(i))

            data_list = proxy_col.find()
            ip_list = []
            for ip_item in data_list:
                ip_list.append(ip_item['prxoy_ip'])
            key = random.randint(0, len(ip_list))
            ip_port = ip_list[key]
            proxy = {
                "http": "http://" + ip_port,
                "https": "https://" + ip_port
            }

            url = 'http://glidedsky.com/level/web/crawler-ip-block-2?page={}'
            headers = {
                'Cookie': '_ga=GA1.2.1060843941.1569561676; footprints=eyJpdiI6ImFOK296SGVxYUY5dm44VjdWOUNybnc9PSIsInZhbHVlIjoieFBhZjB5R09KT1lOc3BmUnc0MDhOYVF5eCtCN3MxTEFRYUZ3Y2F6SklCK1NzbTF0TzFrcXg1WEdUOFhORzJ4ViIsIm1hYyI6ImNhMTI0NTdmNGJkN2QyNjc5MzA1MDE0YTQ1ZWFjZGZmNTM4NDQ1M2FhYTEzMGZiMzU1ZGJmYzY2ZWQ5MWFmMGIifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IkNYNDhCdzZvejNvQ0xRUzJhUk1EdUE9PSIsInZhbHVlIjoiWk1CVGFqa015VXlvVEFqdUZWTDB5c2ZxNTZNcktOVVdpYzhrdTFCcUVZcmxuYnZpWmJrN3RpN2RRd3oxV3BjQWRiMDFzSXV5bHM1a3lZYnNrZ3JhU3czVW5HRnllV1JBc2s3bCtFd1M5R2VZVWRJSXJWYTJaaTFzTURnUzg0NThKVW0rVFVJYWdGZkd1bkNubjBQWXJINHY3QkF0TmhyejAwSndPOUJtQXY0PSIsIm1hYyI6ImQzNGU5ZjQyZmEzMTJiZjBlMGM3NWYyOTk5NWFhMjAyNzBkODBhMWZiMzJiM2I1N2U2YzQzNjYxOWQ3OTFiODUifQ%3D%3D; Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1582534860; _gid=GA1.2.1591365143.1584543712; XSRF-TOKEN=eyJpdiI6IklmQ1VuM0hWaXphUEZKQnFJNzBMekE9PSIsInZhbHVlIjoiUm9sOXN0R2d5UExDOEd4anZEbUZ3dXhMUEwwNVNXMHNvUXFZOVdvM2R5XC9oek9UMkRuNDRDMHhaSnVNdG5TcDMiLCJtYWMiOiJiN2Q0ZTQxYjM3OTRjNmZkY2UxZGM1ZDJlZjZkYzIxZDQxOGU1Mjc5YjM1ZTMzMDRiNTM2Mzc0NjAxN2RjOGIwIn0%3D; glidedsky_session=eyJpdiI6IlQxN3VLU1F5SzBRcUdlbUpabFpLS1E9PSIsInZhbHVlIjoiTHhXaFNqK0VHeXU1bW5jM1E2ajBsSnU5bitwdVFOTUtBSWpRZUVcL2NCK01ZeVdndmxUK21cL21mcGtLSCtBSm5XIiwibWFjIjoiOTFmOGIxNzAzODg1ZTFiMTllZGYyYTQwZWUwMTNhMWY3ZmQ4ODk4ZGI2Yjk2MTFjMzgzN2FmODkyMTllZDQ0YyJ9; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1584544996',
                'Host': 'glidedsky.com',
                'Pragma': 'no-cache',
                'Referer': 'http://glidedsky.com/level/web/crawler-ip-block-2?page={}'.format(i-1),
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            }
            url = url.format(i)
            res = requests.get(url, headers=headers, proxies=proxy, verify=False, timeout=3)
            if res.status_code != 200:
                continue
            html = etree.HTML(res.text)
            num_list = html.xpath('//*[@id="app"]/main/div/div/div/div/div/text()')
            for num in num_list:
                sum = sum + int(num.strip())
            print(sum)
            break
        except Exception as e:
            print(e)


