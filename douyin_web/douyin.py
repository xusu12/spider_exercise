import requests

headers = {
    'authority': 'www.douyin.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'accept': 'application/json, text/plain, */*',
    'dnt': '1',
    'withcredentials': 'true',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.douyin.com/user/MS4wLjABAAAAYsGlaAlC63EwxXFJX-DkIdIcMNr5PxZy3h3PvIGobBFp8S11I-0xQMQ2i-Z182vk',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'ttwid=1%7C1RDyVXroUAMHgtWbR4bLHrwNLq1DQQMUWnb10oNXooA%7C1624806332%7C8518123d131e3109e3154f5b3abe181f5a792fe5fc8a3a14a89382b1d1e008d3; MONITOR_WEB_ID=f8f2286d-5ab4-4f86-bf86-e67585df4cd2; s_v_web_id=verify_kqfbqs3q_WALBQuwz_uC07_4gMQ_B36T_Lr96OnWQZhVZ',
}

response = requests.get(
    'https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAAYsGlaAlC63EwxXFJX-DkIdIcMNr5PxZy3h3PvIGobBFp8S11I-0xQMQ2i-Z182vk&max_cursor=1615597200000&count=10&publish_video_strategy_type=2&version_code=160100&version_name=16.1.0&_signature=_02B4Z6wo00f012tbZjAAAIDDZ6rogYU-hctrWWKAALoZ00', headers=headers)

print(response.status_code, response.text)
