import random
import requests
# 1. 准备代理列表
proxies = [
    # {'http': '121.8.98.198:80'},
    # {'http': '39.108.234.144:80'},
    # {'http': '125.120.201.68:808'},
    # {'http': '120.24.216.39:60443'},
    # {'http': '121.8.98.198:80'},
    {'https': '59.55.103.56:8888'}
]

# 2. 随机选出一个代理
for i in range(0, 10):
    proxy = random.choice(proxies)
    print(proxy)
    try:
        response = requests.get("http://www.baidu.com", proxies=proxy, timeout=3)
        print(response.status_code)
    except Exception as ex:
        print("代理有问题: %s" % proxy)