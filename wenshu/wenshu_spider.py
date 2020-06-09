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
        'Cookie': 'HM4hUBT0dDOn80S=jXU74X4_P_wKNHJRn_A3OWfD6FPPzuozoEyfKOwyub_ZAXasQ2q_KTcD3JMot7Ta; SESSION=e0ea12e4-18c3-4294-9320-7196815adae9; HM4hUBT0dDOn80T=4hCk9eVeGXkZ1opt7Zi_eaQyiSD_T4fyXb5zaBfVrVzNyJm93EtfFQLPT6oHuQ5B7K7bKcF3k_anwBRH9uG1.ITjRf..HGKT2ixO0ergek0vuhAT_D.QZnZ4RugdsURN_OUQfUY_HAkNroOB2PcdN4WPbKO2C0dEXN7m7aJzEqv.TJJ34ebHsMiWVc5S.6RNwWxLKxI3hVaRV1NOG9wKSdsTo6oM1Bw3E3ZYm0uXFr_9RkOfOPeB2JdyQsPASLy8FB8v0ALXD_JnvbJR1dDSjfvxlfcyZJh4qIDofU9.lPa0xNwTtV0Zfq.Z1fPSomkpw15asKFgg.TakACg3S3mRS8MEPHnK.KTLePPU_N6zBVrPdnmvzkBTnyICGQNZ0Q.2R8A',
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
