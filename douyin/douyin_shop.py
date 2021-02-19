import requests
import json


user_id = '53304917615'
sec_user_id = 'MS4wLjABAAAA6lwGsdvKaZe5PJVHH9ocMI_PMkfyVx9poNHWndDH7p4'
headers = {
    'authority': 'aweme.snssdk.com',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cookie': 'odin_tt=e49ea6a1c343ff87ed08ce966d3cdc75848a0e2c82dde3278ddd71242a5ed3128b814b2194f7ef7df3520b498128222e',
}

params = (
    ('user_id', user_id),
    ('sec_user_id', sec_user_id),
    # ('user_id', '73439410307'),
    # ('sec_user_id', 'MS4wLjABAAAA27jzx3xP8Iyg3s16QadbnMCnpX_Q_ByfzBXIUab6p_s'),
    ('count', '20'),
    ('column_id', '0'),
    ('goods_type', '0'),
    ('shop_version', '1'),
    ('os_api', '25'),
    ('uuid', '862612348413351'),
    ('app_name', 'aweme'),
    ('version_name', '11.0.0'),
    ('ts', '1603981435'),
    ('cpu_support64', 'false'),
    ('app_type', 'normal'),
    ('channel', '360_aweme'),
    ('update_version_code', '11009900'),
    ('_rticket', '1603981436880'),
    ('device_platform', 'android'),
    ('iid', '34812927426136'),
    ('version_code', '110000'),
    ('cdid', '3b9a9504-6278-43ef-a340-dec120cd3fc3'),
    ('openudid', 'fb2ea2867b0b616a'),
    ('device_id', '1055159716166280'),
    ('aid', '1128'),
)

response = requests.get('https://aweme.snssdk.com/aweme/v1/promotion/user/promotion/list/', headers=headers, params=params)

res_data = json.loads(response.text)
for li in res_data.get('promotions'):
    try:
        item = {}
        item['title'] = li['title']
        item['sales'] = li['sales']
        item['price'] = int(li['price'])/100

        print(item)
    except Exception:
        pass
