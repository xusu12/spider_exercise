import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions


def decode_cookies_to_dict(cookies_string):
    """
        将字符串类型的cookies转成字典

        Params:
        * cookies_string:    (string) - cookies字符串

        Returns:
        * cookies:           (string) - cookies字典
    """
    cookies = {}
    for item in cookies_string.split(';'):
        value = item.replace(
            item.split('=')[0] + '=', ''
        )
        cookies[item.split('=')[0].strip()] = value
    return cookies


options = ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome('C:\\chromedriver.exe', chrome_options=options)
url = 'https://ticket.urbtix.hk/internet/'
browser.get(url)


cookie_dict = {"isg": "BB0dKN79IQwGgsU-XS-vo8ptLPkXOlGMQpBbrN_iWXSjlj3Ip4phXOuGxIqQTWlE", "rurl": "aHR0cDovL2FkLmFsaW1hbWEuY29tL3poYW9zaGFuZy9jcGV2ZW50L2luZGV4Lmh0bQ%3D%3D", "cna": "uwg1GVdJVBoCAd5dad63lP8X", "t": "2eda01317d04e2a305d8b6baf02918d2", "taokeisb2c": "", "_ga": "GA1.1.831164865.1622020798", "l": "eBTTxOurjk-CcxA2BOfanurza77OSIRYYuPzaNbMiOCPO01B5MmJX6_YRxT6C3GVhsNvR3rRQjtHBeYBq7NSnxvtWoBgDoHmn", "v": "0", "xlly_s": "1", "tfstk": "cW_FBPiN-yUUVKT7DeTrOI2N-V5dwm5hZVRXxGuQ5x3WiBf0qYdiBLRwN0UJx", "alimamapwag": "TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzkwLjAuNDQwNi4wIFNhZmFyaS81MzcuMzY%3D", "cp_home_page": "true", "alimamapw": "WRVSCllSQ1pbXVhSXQEVdgARelYSIwcSdA4RcgEQdicVd3EReVMSJAUSdHg9AQJRB1JRAgIEWlQA%0AXwJUVwlXAgAGAAYBAgRSDFBTA1I%3D", "cookie32": "76d39db4f1e823c7d27f5a4144fd4876", "cookie31": "Mjc5NjkwMDc4LGF0ZWxpZXJjb2xvZ25lJUU2JUFDJUE3JUU3JThGJTkxJUU2JTk3JTk3JUU4JTg4JUIwJUU1JUJBJTk3LGxvcmVhbDAxNUBidXljb29yLmNvbSxUQg%3D%3D", "login": "UtASsssmOIJ0bQ%3D%3D", "_ga_Q39CBKW296": "GS1.1.1622184712.15.0.1622184719.0", "taokeIsBoutiqueSeller": "eQ%3D%3D", "cookie2": "1e5c282b4cea0aae6d9af4035424dc8b", "_tb_token_": "574eb77703185"}

cookie_str = 'TS4242922a027=0828494788ab20002c6307ef5e1ab3c36a031a792d0ee042f2c9488fd43194a38b7ee1e5e086ae18080b04285d113000b87da758d68d804374dbb4d9d70ede36e4422f0a3bf209be50ed5af57d455226578a6fcbc5d7692235954fa5e48013e5; Auth_Token=202111272226-3163328929-8b4ded4e98f4a398ccd798350bcd3450db4243ea'
cookie_dict = decode_cookies_to_dict(cookie_str)

for cookie_item in cookie_dict:
    browser.add_cookie(
                    {
                        'domain': '.urbtix.hk',
                        'name': str(cookie_item).replace(' ', ''),
                        'value': cookie_dict[cookie_item]
                    })
browser.get('https://ticket.urbtix.hk/internet/zh_TW')
time.sleep(10)