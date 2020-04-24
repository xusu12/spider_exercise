import requests
from lxml import etree
#url = 'http://61.146.213.163:8011/User_lastmonth.aspx?lid={F96EA453-7C8F-488C-BEB4-A696849BBA06}'
url = 'http://61.146.213.163:8011/User_Presell_beian.aspx?PN=000183%cf%ee%c4%bf&kfsid=&LID=f96ea453-7c8f-488c-beb4-a696849bba06'

header = {
    "Cookie":"ASP.NET_SessionId=isp3tu45kse3sj3kh2cndr45; security_session_verify=e97c483845d397932aa0cd8cd5cecfac; security_session_mid_verify=6e50f0e3ce500fc304148959654093a0",
}

res = requests.get(url,headers = header)
print(res.text)
print(res.status_code)

page = etree.HTML(res.text)

c = page.xpath('//td/a[@target="_blank"]/@href')

print(c)
# .
# <a href="User_Presell_beian.aspx?PN=%a3%a810%23%a1%a211%23%a3%a9%b5%d8%cf%c2%ca%d2&amp;kfsid=0300255&amp;LID={F96EA453-7C8F-488C-BEB4-A696849BBA06}" style="color:#FF0000" target="_blank">（10#、11#）地下室</a>
