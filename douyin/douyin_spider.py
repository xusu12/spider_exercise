import requests
from lxml import etree

headers = {
    'Accept': 'text/*, application/xml',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Mobile Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Host": "www.douyin.com",
    "Upgrade-Insecure-Requests": "1"
}

url = 'https://www.douyin.com/share/user/102148029874'
res = requests.get(url, headers=headers)

html = etree.HTML(res.content.decode('utf8'))

ret_list = html.xpath('//div[@class="personal-card"]/div[2]/p[3]/span')
for ret in ret_list:
    print(etree.tostring(ret).decode())
    res = ret.xpath('//i/text()')
    print(res)
    break


