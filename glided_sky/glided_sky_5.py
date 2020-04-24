"""
    字体反爬-1
"""
import re
import base64
import requests
import xml
import time
from lxml import etree
from fontTools.ttLib import TTFont


def get_html():
    sum = 0
    for i in range(1, 1001):
        print('当前页面是{}'.format(i))
        url = 'http://glidedsky.com/level/web/crawler-font-puzzle-1?page={}'.format(i)
        headers = {
            'Cookie': '_ga=GA1.2.1060843941.1569561676; footprints=eyJpdiI6ImFOK296SGVxYUY5dm44VjdWOUNybnc9PSIsInZhbHVlIjoieFBhZjB5R09KT1lOc3BmUnc0MDhOYVF5eCtCN3MxTEFRYUZ3Y2F6SklCK1NzbTF0TzFrcXg1WEdUOFhORzJ4ViIsIm1hYyI6ImNhMTI0NTdmNGJkN2QyNjc5MzA1MDE0YTQ1ZWFjZGZmNTM4NDQ1M2FhYTEzMGZiMzU1ZGJmYzY2ZWQ5MWFmMGIifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IkNYNDhCdzZvejNvQ0xRUzJhUk1EdUE9PSIsInZhbHVlIjoiWk1CVGFqa015VXlvVEFqdUZWTDB5c2ZxNTZNcktOVVdpYzhrdTFCcUVZcmxuYnZpWmJrN3RpN2RRd3oxV3BjQWRiMDFzSXV5bHM1a3lZYnNrZ3JhU3czVW5HRnllV1JBc2s3bCtFd1M5R2VZVWRJSXJWYTJaaTFzTURnUzg0NThKVW0rVFVJYWdGZkd1bkNubjBQWXJINHY3QkF0TmhyejAwSndPOUJtQXY0PSIsIm1hYyI6ImQzNGU5ZjQyZmEzMTJiZjBlMGM3NWYyOTk5NWFhMjAyNzBkODBhMWZiMzJiM2I1N2U2YzQzNjYxOWQ3OTFiODUifQ%3D%3D; Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1582534860; _gid=GA1.2.1591365143.1584543712; XSRF-TOKEN=eyJpdiI6IklmQ1VuM0hWaXphUEZKQnFJNzBMekE9PSIsInZhbHVlIjoiUm9sOXN0R2d5UExDOEd4anZEbUZ3dXhMUEwwNVNXMHNvUXFZOVdvM2R5XC9oek9UMkRuNDRDMHhaSnVNdG5TcDMiLCJtYWMiOiJiN2Q0ZTQxYjM3OTRjNmZkY2UxZGM1ZDJlZjZkYzIxZDQxOGU1Mjc5YjM1ZTMzMDRiNTM2Mzc0NjAxN2RjOGIwIn0%3D; glidedsky_session=eyJpdiI6IlQxN3VLU1F5SzBRcUdlbUpabFpLS1E9PSIsInZhbHVlIjoiTHhXaFNqK0VHeXU1bW5jM1E2ajBsSnU5bitwdVFOTUtBSWpRZUVcL2NCK01ZeVdndmxUK21cL21mcGtLSCtBSm5XIiwibWFjIjoiOTFmOGIxNzAzODg1ZTFiMTllZGYyYTQwZWUwMTNhMWY3ZmQ4ODk4ZGI2Yjk2MTFjMzgzN2FmODkyMTllZDQ0YyJ9; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1584544996',
            'Host': 'glidedsky.com',
            'Pragma': 'no-cache',
            'Referer': 'http://glidedsky.com/level/crawler-font-puzzle-1?page={}'.format(i - 1),
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        res = requests.get(url, headers=headers)

        # 获取字体对应表
        font_dict = get_font_dict(res)

        html = etree.HTML(res.text)
        data_list = html.xpath('//*[@class="row"]/div/text()')
        for data_li in data_list:
            data_num = data_li.strip()
            true_data = ''
            for item in data_num:
                true_data += str(font_dict[int(item)])
            sum += int(true_data)
        print(sum)
        # time.sleep(1)


def get_font_dict(res):
    data = re.findall(r'base64,(.*)\) ', res.text)[0]
    res_data = base64.b64decode(data)

    with open('font.woff', 'wb') as f:
        f.write(res_data)
    # # 加载woff字体
    font = TTFont('font.woff')
     # 将woff字体保存成xml格式
    font.saveXML('font.xml')

    number_dict = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
    }
    uniList = font['cmap'].tables[0].ttFont.getGlyphOrder()
    font_dict = {}
    for i in range(0, 10):
        key = number_dict[uniList[i + 1]]  # 混淆后的数值
        font_dict[key] = i  # i是对应的真实数值
    return font_dict


def main():
    get_html()


if __name__ == '__main__':
    main()