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
        'Cookie': 'HM4hUBT0dDOn80S=lLGQN9yCwJr0ASIWXP.EN37r6D36UgZTMtBC57uA7Xwmp3a.qe.odywlfVQzu8fd; HM4hUBT0dDOnenable=true; SESSION=61afe227-77af-43de-b12e-aa2e205e5b8f; HM4hUBT0dDOn80T=4_33XDmS1jrDlL1_1ishJPgAbKa2hKuXKmXdmr._IRp9p.5_RUV3hWjrABSxpTsXPvjhNAm6dF17qkDzIvuF3tPuiwquEWdGRHZOzdqMcK0uivlWNISJzNh80.CPi2VI4i0ingwucpB2WoJgTuYw1CSXJj0cpX62knq6edu_zoMl_eSnTRrF4iGUKJCVbenZM5fo9iXh00gCHDFo3s2FPYtGUUOMHIlJXTpbWve5e5q36S0sbis_gu5ZkV0X.HgAHHQqM9AGk9KDJTtAL2haWNzpIkSJibrIseZIQ1Ue8hrukB5FpcQhQT3i923a4ADM.csg',
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
