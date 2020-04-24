"""
    基础2
"""
import requests
import xml
import time
from lxml import etree

sum = 0
for i in range(1, 1001):
    url = 'http://glidedsky.com/level/web/crawler-basic-2?page={}'
    headers = {
        'Cookie': '_ga=GA1.2.1060843941.1569561676; _gid=GA1.2.640917502.1569561677; footprints=eyJpdiI6ImxiMCtwUTVqcnhNckcwdnU1dU1sNEE9PSIsInZhbHVlIjoic2ozMzNac0tmcEJreHd0ZEI2bkk2U1BHanBkUGVTZ012VGl5QmdHMkVIWHJZZEw2c28rdGlaZ3lST0ZWY2V5UiIsIm1hYyI6IjBjOTZiNjBkYWExOTViMjg1MWU5NzUxOWI5MWVhY2E0N2Y3M2Q4YjEyODJhNGM4ZDg4NTQ5MzgwNmE3ODFiMjEifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6Ik1HWVJKaHBoanBObitmUXRFYmFEY2c9PSIsInZhbHVlIjoic0YxYjFjTUtyM28yK0RBN05Jc3Nna0ZiWnJuanlsWUJDUXJrNkd4UElsNWJaQkxHSjhtRVE4SGN5Nm55VXI5TFg1OGRJbDFDdk1zSEJwbzY5OWxBd3EyXC9XeWFjWmFWRWxiWUNJeWFcL0grd1p5QVo3ZVZUZ005TU1RZXVzSTFKR29hMUVydlRxV3FyY0Rub3N2NTNDXC95SHN1QzFwRlZJd2tDMTdVVFNEYmJ3PSIsIm1hYyI6IjE3NWM4MDg1MmViNzZmMWI0Y2UyMDI0ODdlYzhlYWU2MjBmNGQ1MmUzODNjOTcwNWMwMjVkZDFjZWZlZDE5MzQifQ%3D%3D; Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1569561675,1569573342; _gat_gtag_UA_75859356_3=1; XSRF-TOKEN=eyJpdiI6InF0elI3dzVZQ0FENFZ4d3p1b3pGWXc9PSIsInZhbHVlIjoicjI4QlwvYmVFNEtvellGbkt3ZXJDTExoZ2IzU3NodHhXZEIwa2NcLzBXMXUzWXAzWnVxMEoxKzRLeFpsS1RnYkh1IiwibWFjIjoiYTIwNGRmM2FlNTI2OTViMjFkYTIzZDM4N2UxMTczOTQ3NGE1OTFiYTdiOWE0ODMzZDM5MTg4MTI2OTg0ZWUwNCJ9; glidedsky_session=eyJpdiI6Im9NUFVZN2Z5QVZZeHNZTkhwaldxNXc9PSIsInZhbHVlIjoiZ3p5SkxQbHlacm8xUHhFQXJyYjlQalA2TzNqUGRXNU5TQnN3K3R1cnltd0NKakp5dnVhUUJYR1M4MEJOUjVuVCIsIm1hYyI6IjhlNTZkNTlmMDRiYTg1NGFjN2Q2N2U4OTk4NTg0OTgzZmExMmIyMDIwZGFjMDdjYmM2ZjE4MTZhMTlhYjQ1NmEifQ%3D%3D; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1569573374',
        'Host': 'glidedsky.com',
        'Pragma': 'no-cache',
        'Referer': 'Referer: http://glidedsky.com/level/web/crawler-basic-2?page={}'.format(i-1),
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    url = url.format(i)
    res = requests.get(url, headers=headers)
    html = etree.HTML(res.text)
    num_list = html.xpath('//*[@id="app"]/main/div/div/div/div/div/text()')
    for num in num_list:
        sum = sum + int(num.strip())
    print(sum)

