"""
    字体反爬2  2656466
"""

import re
import base64
import requests
import xml
import time
import traceback
from lxml import etree
from fontTools.ttLib import TTFont


def get_html():
    sum = 0
    for i in range(1, 1001):
        while True:
            try:
                print('当前页面是{}'.format(i))
                url = 'http://glidedsky.com/level/web/crawler-font-puzzle-2?page={}'.format(i)
                headers = {
                    'Cookie': '_ga=GA1.2.1060843941.1569561676; Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1585196663; footprints=eyJpdiI6Ilhjb2FNc1NFS3FscTNsN3NxWmYzY3c9PSIsInZhbHVlIjoiM0hyOUdicEg2cHd1elJEc0lTeUhiUDJFQjF6cytzNVI2Vkc3Q1hqWVJWQ1l0YmdRc1Nnak9jY0dEU29xREtzUiIsIm1hYyI6IjgxMjFlYTBjZTljNWE2N2I0YmM4ZDA2NTk2MDM4MDRjM2U3OTA5MTkyNmRlMDNiMzMxYTI4ZjUzN2MxN2FlZDUifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IktEMFwveGZCWVRTVjlEQ1RWSlZUODdnPT0iLCJ2YWx1ZSI6IlBteFB2WnVENVBadTF1XC9OU056ZU5nWWdVaElhTHpsa3p6bHZQdExnb2JSRkxkT2JKeUIyMmhSNks0MkZQd3hVVFlPenAwZVNkd3hFMG1hZFNoOHZWeWVmSVVzXC9XTkZ1M29ZOGwwa3pEQjVLdVFUcXMzRjBkU0dDMSs3T3h0U1Z5T2NRT2lXS3l5c3lhYzFadGlMRjNmN2xJT3dpYkJSY3pHNmdsMUlMb0FjPSIsIm1hYyI6ImI2YjYwOGU3YmExMjJkNTI2NDIyMTlkMTY2ZGQ4YzgwZTlkZjBiNDdmZTAzYmUyNTZjNDQ5MzI1MjlkYjQwYWYifQ%3D%3D; _gid=GA1.2.1974645774.1586530554; XSRF-TOKEN=eyJpdiI6IkRFeHpCOFNYQnRRRklxcXhlS1wvbUNRPT0iLCJ2YWx1ZSI6IlVROFlSQUptNFl0QlkycHdjSlgzejI3a3h6YXFcL3poYmFNeTQrQmFaUEdkSFhKSXRveFFKMmgycDBhMmtUcVorIiwibWFjIjoiNmVjYmNlMDZhZmQ1MWU2MWUzZjY0NGNhOWEwZjIxNWVlODcwYzhiZWUyNDE4ZWIyYjhhODcyMDdjZGI1ODcyYyJ9; glidedsky_session=eyJpdiI6ImJUSW4wd3UyQTZJcmpJcEJHWFpTREE9PSIsInZhbHVlIjoiNUsycURiM3hYb0IxZ3FcL0ZqckJiSEpiR3BpaUYxcVhGbGUzN1NFWEtLRXBENytDMDNmTWwyZVNzaWdPUFUyXC9pIiwibWFjIjoiYmI4ODdiN2Q0YTgyNDdkNzQ3ZTgxNzAzMTZmNjY3ZjMxM2EyNDhjMDkxMjg4MjY5ODhlYWY4YmY5NWE1MmYwZSJ9; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1586530606',
                    'Host': 'glidedsky.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://glidedsky.com/level/crawler-font-puzzle-2?page={}'.format(i - 1),
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                }
                res = requests.get(url, headers=headers)

                # 获取字体对应表
                font_dict, cmap_dict = get_font_dict(res)

                html = etree.HTML(res.text)
                data_list = html.xpath('//*[@class="row"]/div/text()')
                page_sum = 0
                for data_li in data_list:
                    data_num = data_li.strip()
                    num = ''
                    for item in data_num:
                        name = re.findall(r'u(.*)\'', str(item.encode('unicode_escape')))[0]
                        if not font_dict.get(name.upper()):
                            cmap_key = int(f'0x{name}', 16)  # 将16进制数据转换成十进制的数据
                            cmap_name = cmap_dict.get(cmap_key).split('uni')[1]
                            item_num = font_dict.get(cmap_name)
                        else:
                            item_num = font_dict.get(name.upper())
                        num += str(item_num)
                    page_sum += int(num)
                sum += page_sum
                print(sum)
                break
            except Exception:
                traceback.print_exc()


def get_font_dict(res):
    data = re.findall(r'base64,(.*)\) ', res.text)[0]
    res_data = base64.b64decode(data)

    with open('font2.woff', 'wb') as f:
        f.write(res_data)
    # # 加载woff字体
    font = TTFont('font2.woff')
     # 将woff字体保存成xml格式
    font.saveXML('font2.xml')

    uniList = font.getGlyphOrder()  # 获取GlyphOrder的name
    cmap_dict = font.getBestCmap()  # 获取cmap的cmap_format_4
    font_dict = {}
    for i in range(0, 10):
        uni_name = uniList[i+1]
        key = uni_name.replace('uni', '')
        font_dict[key] = i

    return font_dict, cmap_dict


def main():
    get_html()


if __name__ == '__main__':
    main()