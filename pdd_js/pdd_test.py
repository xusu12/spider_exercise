import requests

url = 'http://mobile.yangkeduo.com/search_result.html'

headers = {
    'AccessToken': 'V4SI2LKDRASXIDTLI3HR3OHBAVJVFLHRDCHA42I23X5NRFXZTLNA1102222',
    'Cookie': 'api_uid=CiU0B13k6g0ZewBBRlwmAg==; _nano_fp=Xpd8npPJXqPal0d8X9_SuHun_flFeCbZIbgfFSqQ; ua=Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_3)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F80.0.3987.149%20Safari%2F537.36; webp=1; Hm_lvt_1370d93b7ce0e6f1d870cef43042d966=1587740537; PDDAccessToken=V4SI2LKDRASXIDTLI3HR3OHBAVJVFLHRDCHA42I23X5NRFXZTLNA1102222; pdd_user_id=8089136722978; pdd_user_uin=3K366JOTYWYGQN6BS3S2TAD2FU_GEXDA; JSESSIONID=E0437E8872CD3765EB1425FD2D976889; Hm_lpvt_1370d93b7ce0e6f1d870cef43042d966=1588651148',
    'Referer': 'http://mobile.yangkeduo.com/search_result.html?search_key=%E9%9E%8B%E5%AD%90',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'VerifyAuthToken': '02EATn_It1SS5g9XPLoQLQ'
}

params = {
    'pdduid': '8089136722978',
    'item_ver': 'lzqq',
    'source': 'index',
    'search_met': 'history',
    'track_data': 'refer_page_id,10002_1588575110055_lhrff5ajmo;refer_search_met_pos,0',
    'list_id': 'SPm2npeCWh',
    'sort': 'default',
    'filter': '',
    'q': '鞋子',
    'page': 2,
    'size': 50,
    'flip': '20;4;0;0;f68edba4-a3d5-4835-8337-acc511e98db8',
    'anti_content': '0aoAfxvYdyIgYgmaRsReFSn_2sh6UT6m_6suMWjE7eMF_2fpByOS3jKn2TYLBJ-jzvM6bGHgVQYbOXIYfhJ4IqbpCwh8MY7IO2G3dvQ6R5xiql61ud9Y6AJZyE2VFHRXDoLaU01FkntvFFzh1ar7R-jrVnmwEH4ozrXOpKCzgH9SjTtQCKzB6ShXt9Q49fdCq7JN1lJ-Q3cWKyQ6xi-qaZAh03WhFTQ57oJTh6JP4xtRf3-feUW_kgch7T_ZyBe1dBzk6QVqEfol2QqdVe1z4pxov-taDtKus8sL_1rI7_eYM1Sc2pC4KPV2IxnEWYI8gkwctFDFn1zaeVOXnQTjDDllGuOYqBKepKoBEdiV5I96ewPo-5CAISOc4FmGZqGX5a-3nTf8X2ZCMco51e2GkyEAwz7YtHKCCyJCo1aLBzI_gKQExSF5eJ7wB-wqmQLe4rOV4wvPgRLeg2YlOpeYnoUIpx7JUpJiyBVXunwpeHYNMAQAouDwgkaPPNggBADK2QlHUwSMtKdnv8c1GIFUIJ8N-DwjwFHSAzrXmV6QXYQ6oi-Vb3UPqboVRyxOYx6ELU5lhLKM5reLR_MwNz3GQbNDk0ezQjRQJfIt4r8llzcDO1lEDClVahPt3N8ScAYIecaQkBMEOscQblGK0vKnhr9N1-8V9'
}

res = requests.get(url, headers=headers, params=params)
print(res.url)
print(res.text)
with open('./1.html', 'w') as f:
    f.write(res.text)
# print(res.text)
