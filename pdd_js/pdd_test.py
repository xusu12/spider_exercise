import requests
import json


headers = {
    "authority": "mms.pinduoduo.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": "\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
    "anti-content": "0apWtxUkM_VetaVTkjxNbOcUXnkUa0tQexEVGdVBDe3dnOEmBzFv9pxs5agOomunJ-Vfki_v-twmG7oS3cmHsWwMkApMVigWOS3hCKkRmM1RVa6WmHs62HbtJ2bqtFeM1VD71IeM-ODB1FDB3HHB1KkM3FkMkheM2VeBVvyQgpaT9KodIYnH4xFI4UqYDPGYn-tj0Cznj0w49WDSsiWHQ9EKM2KKBAVHw9vn0QxzIVanisvu4aKqgFldyJqY5Y_lYv8jYn8vi0aiVUxiAs_qnSnd-zadyJQYcAvunbK9HSfgM5VSKMkOe7WIe-4uBtDe-gMzsW0_F_2p-tWK7zFdKBYzj3ZpMGguJxGofsmzep3uJtDKsAqeBt8Ovcg_EK6ypKSa9QKnUnoopfYn_Nc-2kfQBABk25B7DwmZLw3zdKL2_SbRfvL1coDH1qLUmB7XJoBww20JbEoywPGq9P",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "etag": "MBZfl2UapIwCDfrrGSaa8Do095KpjQ9z",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "sec-ch-ua-platform": "\"Windows\"",
    "accept": "*/*",
    "origin": "https://mms.pinduoduo.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://mms.pinduoduo.com/goods/goods_list",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
}
cookies = {
    "api_uid": "CiXh1V8g3TfByABR0LNUAg==",
    "_nano_fp": "Xpdbnq9YlpCJnqdaXC_d_0FzX7CcfQJcQaksDXxg",
    "finger-FKGJ_0.1.2": "e6fc6cdbe0ec4971859ae01d29a00bc4",
    "finger-cookie_0.1.2": "1b2bf49ee6628386e8c5aed6c2bf551b",
    "_bee": "MBZfl2UapIwCDfrrGSaa8Do095KpjQ9z",
    "_f77": "2c519f37-ba28-4c15-852f-b04440aedf6e",
    "_a42": "e72500f1-1e95-4f90-aae3-adfa3caebc8b",
    "rckk": "MBZfl2UapIwCDfrrGSaa8Do095KpjQ9z",
    "ru1k": "2c519f37-ba28-4c15-852f-b04440aedf6e",
    "ru2k": "e72500f1-1e95-4f90-aae3-adfa3caebc8b",
    "mms_b84d1838": "3414,120,150,3397,3434,441,442,403,404,1202,1203,1204,1205,3417,1304",
    "PASS_ID": "1-Vw4mriMrnmKT7wO1NjrRsc/fxVIEQ2VYlw+EOeLsQB7nW2iWC4rUI1a+49s3oBAmyt+ZRUkAUlFP0C2d27h8HA_496181899_101167027",
    "x-visit-time": "1636624472608",
    "JSESSIONID": "23B5375357DF1D6C0CA506751A630FD6"
}
url = "https://mms.pinduoduo.com/vodka/v2/mms/query/display/mall/goodsList"
data = {
    "page": 1,
    "is_onsale": 1,
    "sold_out": 0,
    "size": 10
}
data = json.dumps(data)
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)