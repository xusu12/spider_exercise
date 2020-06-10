import os
import sys
sys.path.insert(0, os.getcwd())

import requests
import execjs
import json
from pprint import pprint
from wenshu import get_wenshu_params


# 获取pageid
def get_pageid():
    js = """function happy() {
                    var guid = "";
                    for (var i = 1; i <= 32; i++) {
                        var n = Math.floor(Math.random() * 16.0).toString(16);
                        guid += n;
                        // if ((i == 8) || (i == 12) || (i == 16) || (i == 20)) guid +=
                        // "-";
                    }
                    return guid;
                }"""
    ctx = execjs.compile(js)
    pageid = ctx.call("happy")
    return pageid


# 获取__RequestVerificationToken参数
def get_token():
    js = """ function random(size){
            	var str = "",
            	arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
            	for(var i=0; i<size; i++){
            		str += arr[Math.round(Math.random() * (arr.length-1))];
            	}
            	return str;
            }
    """
    ctx = execjs.compile(js)
    result = ctx.call("random", "24")
    return result


def spider():
    ip_port = 'secondtransfer.moguproxy.com:9001'
    proxy = {"http": "http://" + ip_port,
             "https": "https://" + ip_port}
    appKey = 'b21jU2FUempOdWJic0FIRDpKcE9XQ3JxT2Nrb2NOUnE5'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://wenshu.court.gov.cn',
        'Cookie': 'HM4hUBT0dDOn80S=lLGQN9yCwJr0ASIWXP.EN37r6D36UgZTMtBC57uA7Xwmp3a.qe.odywlfVQzu8fd; SESSION=8b9121cf-beff-43b1-843f-b42d31114f40; HM4hUBT0dDOn80T=4XzYe1aZr50hUZv6rFbD8CJwTcmL3cDOmpMnKY86WJ9Ncdh6tkfY33IWk4llcfbOSuID_la_7ivfsUuGWuDUh8U5w5zloEHR27vzmRRcsrfQeF2esctJ6BuTy2hd2HlVnEBoLyONU2tqa4kUGdOujfUyiIO_ovV1AAK9BUXZ5sewyouJQO.lTg56myKYX.rz89K3cL9lZp1a_tRc9r0MIG.DF2Hzbk15tsKSu0XGCDCSdQmQSfDWf6eLdfh76UDs3Dm12WTF54IDx8mRYTSitHMuh7kpgc11MjF1m9y5YZuVA44Z15zp40UAwS.ctu4G3SQ7OSRZqfe2tkmCA3X9TcXNL',
        "Proxy-Authorization": 'Basic ' + appKey,
    }

    data = {
        'pageId': get_pageid(),
        's8': '02',
        'sortFields': 's50:desc',
        'ciphertext': get_wenshu_params.get_ciphertext(),
        'pageNum': '1',
        'pageSize': '5',
        'cfg': 'com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc',
        '__RequestVerificationToken': get_token()
    }

    response = requests.post('http://wenshu.court.gov.cn/website/parse/rest.q4w',
                             headers=headers,
                             data=data,
                             verify=False,
                             proxies=proxy
                             )
    print(response.status_code)
    print(response.text)
    res = json.loads(response.text)
    if res['code'] == 1:
        secretKey = res['secretKey']
        result = res['result']
        res_data = get_wenshu_params.decrypt_res(result, secretKey)
        pprint(json.loads(res_data)['queryResult'])


def main():
    spider()


if __name__ == '__main__':
    main()
