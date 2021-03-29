import requests

url = 'http://www.python-spider.com/challenge/11'


headers = {
'Cookie': 'Hm_lvt_337e99a01a907a08d00bed4a1a52e35d=1602920353,1605280812; sessionid=hw9khcsnffuafqn7cda3g9nmwr4bctqe; Hm_lpvt_337e99a01a907a08d00bed4a1a52e35d=1605285731; no-alert=true; __jsl_clearance=1605286447.233|0|clD4VpfqhdaLBWywKWy%2FZyfi6d_e6940768c5518964a360d51b4d1baf4c3D',
'Host': 'www.python-spider.com',
'Referer': 'http://www.python-spider.com/challenge/11'
}

res = requests.get(url, headers=headers)
print(res.text)