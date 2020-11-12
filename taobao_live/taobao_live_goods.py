import requests
import json
from pprint import pprint


url = 'https://guide-acs.m.taobao.com/gw/mtop.tblive.live.item.getvideodetailitemlistwithpagination/1.0/?type=originaljson&data=%7B%22groupNum%22%3A%22100%22%2C%22liveId%22%3A%22285647850128%22%2C%22n%22%3A%2210%22%2C%22type%22%3A%220%22%7D'
# headers = {
#     'x-extdata': 'openappkey%3DDEFAULT_AUTH',
#     'x-features': '27',
#     # 'c-launch-info': '1,0,1604383747123,1604375278975,2',
#     'x-sgext': 'JAF5dM4VmEJkGyMK0E1hA3RIRElASFdMRUBFWkZPRkk%3D',
#     'x-page-name': 'https%3A%2F%2Fmarket.m.taobao.com%2Fapp%2Fmtb%2Flive-commodity%2Fpages%2Findex',
#     'x-location': '113.39743%2C23.152607',
#     'user-agent': 'MTOPSDK%2F3.1.1.7+%28Android%3B7.1.2%3BHUAWEI%3BVOG-AL00%29',
#     'x-ttid': '1582098846071%40taobao_android_9.15.0',
#     # 'x-region-channel': 'CN',
#     'x-appkey': '21646297',
#     'x-mini-wua': 'HHnB_ZLk6shvu8aADyvi3Kjkp3k0ZSdm4cYTTtt85ufxpqEE4IJaPIQnLu7WmpVtkrTnTWLULy0uaO3UaqT8jrQIOUz%2FHB8uEZRsUMjyv7MNAD%2BktjedLN6%2Bmsw9sunN%2B%2F%2FoS',
#     # 'x-nq': 'WIFI',
#     # 'x-c-traceid': 'X5hDK%2FaeEbgDAEk44a1CzWWL1604382512714395015191',
#     # 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
#     # 'x-app-conf-v': '0',
#     # 'A-SLIDER-Q': 'appKey%3D21646297%26ver%3D1604387261544',
#     # 'x-bx-version': '6.5.19',
#     'x-pv': '6.3',
#     'x-t': '1604387646',
#     'x-app-ver': '9.15.0',
#     # 'f-refer': 'mtop',
#     'x-ua': 'VOG-AL00(Android/7.1.2) AliApp(TB/9.15.0) Weex/0.26.4.57 720x1280',
#     'Cookie': 'unb=1044202336; sn=; uc3=lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UoH7L2AeE%2Bfbzw%3D%3D&nk2=UoCJjDYqviR3b08%3D&vt3=F8dCufJKmBu%2FrTTKhGY%3D; uc1=cookie21=WqG3DMC9FxUx&cookie15=VT5L2FSpMGV7TQ%3D%3D&cookie14=Uoe0abEEdpuToA%3D%3D&existShop=false; csg=95bdddb8; lgc=1104963431x; t=980b781b97ec48d99b5f6d1db8c32f1d; cookie17=UoH7L2AeE%2Bfbzw%3D%3D; sgcookie=W100Wfql%2BLHUCRJJIihD0UAewkwr8J2Rwz2zvRbxuX5JXrS8W2HJ4YEp6KJG%2B0r3%2FWJFUZZEG3XHkzZ864cHBw7cjCbiKA7mc4v2Zg3rWbCHDMA%3D; dnk=1104963431x; skt=a9893618ab7fd51a; munb=1044202336; cookie2=26e77a84c079617c3ba3dc64771d5a70; uc4=id4=0%40UOnkSwt2BfeO7JRtJLuEUn9bIDdx&nk4=0%40UOg1xL7BSvYTTMZUNyL3x5JEES670w%3D%3D; tracknick=1104963431x; _cc_=V32FPkk%2Fhw%3D%3D; ti=; sg=x6d; _l_g_=Ug%3D%3D; _nk_=1104963431x; cookie1=B0aoPs7cgCCsQ3uQx4uBv9PSw9xLSbXzlgDSMvw9TTA%3D; _tb_token_=5e0339b687176; imewweoriw=3HLhRXbqghfe0FkB9aRCxBcjv20ste0H6NvMuNghnVY%3D; WAPFDFDTGFG=%2B4cMKKP%2B8PI%2Bbcs4tUVJz2SjqWgSAg%3D%3D; _w_tb_nick=1104963431x; ockeqeudmj=rBu1WPk%3D; cna=AsInGEUJCSECAXeBS0tg48Iw; xlly_s=2; tfstk=ctbNBiXFI-MsVMTb2FTqfU8Xp6fOZ8xWmJR6jillYnpxHCxGMbXAIU37OWaxD; l=eBa1CQ5gO2T8nTiDBOfahurza77OSCOYYuPzaNbMiOCPOL1B5f9cWZSYGEY6C3GRhsOBR3oUzeSHBeYBY3tSnxvTRpu3pJHmn; isg=BAYG7MgGpbGvW3HV9JbJA0YDXPWIZ0oh-X62HfAv8ikE86YNWPeaMeyhzyk_wEI5',
#     'x-sid': '26e77a84c079617c3ba3dc64771d5a70',
#     # 'x-nettype': 'WIFI',
#     # 'x-social-attr': '0',
#     'x-utdid': 'X5hDK%2FaeEbgDAEk44a1CzWWL',
#     # 'x-umt': 'gABLUf9LOmVKMDV1jDxmC%2BrPOEPwvuqv',
#     # 'a-orange-dq': 'appKey=21646297&appVersion=9.15.0&clientAppIndexVersion=1120201103143700186',
#     'x-devid': 'ApAZRKAmBCpn64yXhCCQkVBjTr-GTl58zfHziPRMMUON',
#     'x-sign': 'azYBCM003xAAJ1LrzufLrHIPVZLBJ%2FLnXdp44qV5nc4OWfZQvAPhSVxTgbAKJzJam54BZkRefPjprUbrAtYWU%2FOj83OSV1LnUldS51',
#     'x-page-url': 'https%3A%2F%2Fmarket.m.taobao.com%2Fapp%2Fmtb%2Flive-commodity%2Fpages%2Findex',
#     'x-uid': '1044202336',
#     # 'Host': 'guide-acs.m.taobao.com',
# }

headers = {
'x-sgext': 'JAHNB72h6%2FYXr1C%2Bo%2FkStwf8N%2F0z%2FCT4NvQ27jT%2BP%2Fs%3D',
'x-mini-wua': 'HHnB_WOdugr2hMzBVw3Af3jB3vNf1m2bze7ndKztTxF4SR9CAgsVYgr5IZgchEmODl8rkK08xBTxrNuGvVCtEFHFhOTFMvd0tkN8fSWQp2NN4e9yQvthMOWVxsdjtwVi9EJ0A',
'x-t': '1604390014',
'x-sign': 'azYBCM003xAALfVuiCYzcoFx5cgmzSVt%2BlDfaALzOkSp01HaG4lGw%2FvZJjqtrZXQPBSm7OPU23JOJ%2BFhpVyx2VQpVPrEbfVt9G31bf',


'x-extdata': 'openappkey%3DDEFAULT_AUTH',
'x-features': '27',
'x-page-name': 'https%3A%2F%2Fmarket.m.taobao.com%2Fapp%2Fmtb%2Flive-commodity%2Fpages%2Findex',
'x-location': '113.39743%2C23.152607',
'user-agent': 'MTOPSDK%2F3.1.1.7+%28Android%3B7.1.2%3BHUAWEI%3BVOG-AL00%29',
'x-ttid': '1582098846071%40taobao_android_9.15.0',
'x-appkey': '21646297',
'x-pv': '6.3',
'x-app-ver': '9.15.0',
'x-ua': 'VOG-AL00(Android/7.1.2) AliApp(TB/9.15.0) Weex/0.26.4.57 720x1280',
'Cookie': 'unb=1044202336; sn=; uc3=lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UoH7L2AeE%2Bfbzw%3D%3D&nk2=UoCJjDYqviR3b08%3D&vt3=F8dCufJKmBu%2FrTTKhGY%3D; uc1=cookie21=WqG3DMC9FxUx&cookie15=VT5L2FSpMGV7TQ%3D%3D&cookie14=Uoe0abEEdpuToA%3D%3D&existShop=false; csg=95bdddb8; lgc=1104963431x; t=980b781b97ec48d99b5f6d1db8c32f1d; cookie17=UoH7L2AeE%2Bfbzw%3D%3D; sgcookie=W100Wfql%2BLHUCRJJIihD0UAewkwr8J2Rwz2zvRbxuX5JXrS8W2HJ4YEp6KJG%2B0r3%2FWJFUZZEG3XHkzZ864cHBw7cjCbiKA7mc4v2Zg3rWbCHDMA%3D; dnk=1104963431x; skt=a9893618ab7fd51a; munb=1044202336; cookie2=26e77a84c079617c3ba3dc64771d5a70; uc4=id4=0%40UOnkSwt2BfeO7JRtJLuEUn9bIDdx&nk4=0%40UOg1xL7BSvYTTMZUNyL3x5JEES670w%3D%3D; tracknick=1104963431x; _cc_=V32FPkk%2Fhw%3D%3D; ti=; sg=x6d; _l_g_=Ug%3D%3D; _nk_=1104963431x; cookie1=B0aoPs7cgCCsQ3uQx4uBv9PSw9xLSbXzlgDSMvw9TTA%3D; _tb_token_=5e0339b687176; imewweoriw=3HLhRXbqghfe0FkB9aRCxBcjv20ste0H6NvMuNghnVY%3D; WAPFDFDTGFG=%2B4cMKKP%2B8PI%2Bbcs4tUVJz2SjqWgSAg%3D%3D; _w_tb_nick=1104963431x; ockeqeudmj=rBu1WPk%3D; cna=AsInGEUJCSECAXeBS0tg48Iw; xlly_s=2; tfstk=ctbNBiXFI-MsVMTb2FTqfU8Xp6fOZ8xWmJR6jillYnpxHCxGMbXAIU37OWaxD; l=eBa1CQ5gO2T8nTiDBOfahurza77OSCOYYuPzaNbMiOCPOL1B5f9cWZSYGEY6C3GRhsOBR3oUzeSHBeYBY3tSnxvTRpu3pJHmn; isg=BAYG7MgGpbGvW3HV9JbJA0YDXPWIZ0oh-X62HfAv8ikE86YNWPeaMeyhzyk_wEI5',
'x-sid': '26e77a84c079617c3ba3dc64771d5a70',
'x-utdid': 'X5hDK%2FaeEbgDAEk44a1CzWWL',
'x-devid': 'ApAZRKAmBCpn64yXhCCQkVBjTr-GTl58zfHziPRMMUON',
'x-page-url': 'https%3A%2F%2Fmarket.m.taobao.com%2Fapp%2Fmtb%2Flive-commodity%2Fpages%2Findex',
'x-uid': '1044202336',
}

res = requests.get(url, headers=headers)
print(json.loads(res.text))
data_list = json.loads(res.text).get('data').get('itemListv1')
for data in data_list:
    # pprint(data)
    item = {}
    item['title'] = data.get('liveItemDO').get('itemName')
    item['price'] = data.get('liveItemDO').get('itemPrice')
    # item['personalityData'] = data.get('liveItemDO').get('personalityData')
    pprint(item)
