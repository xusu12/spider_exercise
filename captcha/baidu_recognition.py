import base64

import requests
import json

# 获取Access Token
# url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=gAmAvK14lnIy4kEaR9b6XXdY&client_secret=41WOXMMZYGZo1Enj1CjQGF1DVGOIk2B5'
#
# headers = {'Content-Type': 'application/json; charset=UTF-8'}
# res = json.loads(requests.get(url, headers=headers).text)
# access_token = res['access_token']
# print(access_token)

access_token = '24.b3c1f83e40c1c2211ac27ff704504029.2592000.1559474441.282335-16161582'
request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token={}"
# request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={}"
request_url = request_url.format(access_token)

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# 二进制方式打开图片文件
f = open('./9.png', 'rb')
img = base64.b64encode(f.read())
data = {"image": img}

res = requests.post(url=request_url, headers=headers, data=data)
print(res.text)