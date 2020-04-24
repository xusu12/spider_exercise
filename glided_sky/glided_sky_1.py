"""
    基础1
"""
import requests
import xml
from lxml import etree

url = 'http://glidedsky.com/level/web/crawler-basic-1'
headers = {
'Cookie': 'Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1569561675; _ga=GA1.2.1060843941.1569561676; _gid=GA1.2.640917502.1569561677; _gat_gtag_UA_75859356_3=1; footprints=eyJpdiI6ImxiMCtwUTVqcnhNckcwdnU1dU1sNEE9PSIsInZhbHVlIjoic2ozMzNac0tmcEJreHd0ZEI2bkk2U1BHanBkUGVTZ012VGl5QmdHMkVIWHJZZEw2c28rdGlaZ3lST0ZWY2V5UiIsIm1hYyI6IjBjOTZiNjBkYWExOTViMjg1MWU5NzUxOWI5MWVhY2E0N2Y3M2Q4YjEyODJhNGM4ZDg4NTQ5MzgwNmE3ODFiMjEifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6Ik1HWVJKaHBoanBObitmUXRFYmFEY2c9PSIsInZhbHVlIjoic0YxYjFjTUtyM28yK0RBN05Jc3Nna0ZiWnJuanlsWUJDUXJrNkd4UElsNWJaQkxHSjhtRVE4SGN5Nm55VXI5TFg1OGRJbDFDdk1zSEJwbzY5OWxBd3EyXC9XeWFjWmFWRWxiWUNJeWFcL0grd1p5QVo3ZVZUZ005TU1RZXVzSTFKR29hMUVydlRxV3FyY0Rub3N2NTNDXC95SHN1QzFwRlZJd2tDMTdVVFNEYmJ3PSIsIm1hYyI6IjE3NWM4MDg1MmViNzZmMWI0Y2UyMDI0ODdlYzhlYWU2MjBmNGQ1MmUzODNjOTcwNWMwMjVkZDFjZWZlZDE5MzQifQ%3D%3D; XSRF-TOKEN=eyJpdiI6ImpmNDBVWkZSQkl4QTc4XC92T2lYRnVnPT0iLCJ2YWx1ZSI6ImNUOTJLR2F2UVFadTlJQWxucHorQTZhSEJ3bWJRQTIrYUwrVG4wTUdkS0VUZ3lxb1JmMnIxS1dNZElWXC8zYnlJIiwibWFjIjoiMDE4ZWQ3ZTlkYzA1MzcxM2E0MGQyZjMzNWI1NzAwNjNlNjFlMzNmMTU5N2VhNWU4YTk0ZjljMjllM2I4ZmQwYiJ9; glidedsky_session=eyJpdiI6Ik5uVWNROHJ0YUcwNFl3VHJ5WWExS3c9PSIsInZhbHVlIjoiSDFEYVVzdStXXC9GVzlTdjFMNUM3d010VUg4d1ZyNTErRjRQUmJoTVlXSkVKSkV0d2tRNU9oR1NISzZoczZKMlYiLCJtYWMiOiI4NWM5YzdmZmI5NjAxYzk5OTIxMzM3NGQxMTNlMzdlZmNlYzhmMzU0MjYwMjQxMWVlNzE5ZWE5MTcxYzA5Yjk2In0%3D; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1569573045',
'Host': 'glidedsky.com',
'Pragma': 'no-cache',
'Referer': 'http://glidedsky.com/level/crawler-basic-1',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}
res = requests.get(url, headers=headers)
html = etree.HTML(res.text)

num_list = html.xpath('//*[@id="app"]/main/div/div/div/div/div/text()')

sum = 0
for num in num_list:
    sum = sum + int(num.strip())

print(sum)

