import re
import cv2
import json
import time
import execjs
import random
import base64
import requests
from pprint import pprint


class JdLogin(object):
    def __init__(self):
        self.session = requests.Session()
        self.trace = []
        self.encrypt_d = ''
        self.distance = 0
        # self.distance_y = 0
        self.challenge = ''
        self.session_id = ''
        self.headers = {
            'Host': 'iv.jd.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
            'Cookie': 'shshshfpa=cfa756b7-20ea-f30a-d9b1-d617ba99e3ac-1540911734; shshshfpb=13e825e14ca2d447c98f39df441469a5504ee6a6636ba4dbf5bd87276f; __jdv=122270672%7Cdirect%7C-%7Cnone%7C-%7C1591447196957; areaId=0; ipLoc-djd=0-0-0-0; pinId=ovuzPrLExwq4eZbbaemKSQ; pin=Molnlycke-%E9%BA%A6; unick=Molnlycke-%E9%BA%A6; _tp=orAmBXv9kmSM9q4dhDx4jPiN0p1fgrfuRBdKzF%2BXAMs%3D; _pst=Molnlycke-%E9%BA%A6; user-key=5a3014fb-517f-4816-8694-81ee477be5db; cn=0; __jdu=1584086773397456384491; TrackID=11HxnKdfqyCP2OjxSWWCp-leHlEHnkQsiJlRyFf0gzWWZPt07IBeyMMS8foV5aXAE3SBWW1dST-3zko1f9MkKtEVZ3ce8Nk_dBqSq8tCmU7mCfgwmQ-8j_yTUqQ0XJpp9; shshshfp=3dc641b2b5d6f7f2bcdb4cdedd9354c6; __jda=122270672.1584086773397456384491.1584086773.1592112454.1592131238.11; __jdc=122270672; 3AB9D23F7A4B3C9B=U6HBJ4BTP3BIR3TY637P2ON5OFQEO234TGZXCWROSRFBHPKMWGEQGHX52DAWJMULDN5NOWXPATJ4EF6YOJA66CMHJM; wlfstk_smdl=tt864l20t71c1yqgkbnfqfyfux9jw0iq'
        }

    def get_session_id(self):
        get_session_id_url = 'https://seq.jd.com/jseqf.html?bizId=passport_jd_com_login_pc&platform=js&version=1'
        self.headers.update({
            'Referer': 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F'
        })
        res = self.session.get(get_session_id_url, headers=self.headers)
        self.session_id = re.findall(r'sessionId="(\d+)";', res.text)[0]
        print(self.session_id)

    def get_captcha(self):
        # 获取图片验证码
        get_captcha_url = 'https://iv.jd.com/slide/g.html'
        params = {
            'appId': '1604ebb2287',
            'scene': 'login',
            'product': 'click - bind - suspend',
            'e': 'U6HBJ4BTP3BIR3TY637P2ON5OFQEO234TGZXCWROSRFBHPKMWGEQGHX52DAWJMULDN5NOWXPATJ4EF6YOJA66CMHJM',
            'lang': 'zh_CN',
            'callback': 'jsonp_06508952276433504',
        }
        self.headers.update({
            'Referer': 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F'
        })
        res = self.session.get(get_captcha_url, params=params, headers=self.headers)

        captcha_data = json.loads(res.text.split('jsonp_06508952276433504(')[1].split(')')[0])
        bg_pic = captcha_data['bg']  # 返回的滑块验证码的背景图
        patch_pic = captcha_data['patch']  # 返回的滑块验证码的缺口图片
        self.challenge = captcha_data['challenge']  # challenge后面会用到

        patch_img = base64.b64decode(patch_pic)
        with open('./jd_login_for_request/patch.jpg', 'wb') as f:
            f.write(patch_img)

        bg_img = base64.b64decode(bg_pic)
        with open('./jd_login_for_request/bg.jpg', 'wb') as f:
            f.write(bg_img)

        self.get_distance()

    # 滑块的缺口距离识别
    def get_distance(self):
        """
            使用opencv识别验证码位置
        """
        bg_img = cv2.imread('./jd_login_for_request/bg.jpg', 0)
        patch_img = cv2.imread('./jd_login_for_request/patch.jpg', 0)
        # 使用openCV识别验证码缺口位置
        res = cv2.matchTemplate(bg_img, patch_img, cv2.TM_CCORR_NORMED)
        value1 = cv2.minMaxLoc(res)[2][0]
        value2 = cv2.minMaxLoc(res)[2][1]
        # 真实的图片比页面上显示的图片要大一点  按比例缩小距离
        self.distance = int(value1 * 28 / 36)
        # self.distance_y = value2 * 28 / 36
        print(self.distance)

    def varify_captcha(self):
        jseq_url = 'https://seq.jd.com/jseq.html?d=7TJI7tFPWdZpzlDd7TZ37B%3CuwIWPw4wdiQPmSg6d7TZ37t3bWtZ*zt7jhlp4hlZXzf9szlJpzP9*ieWPw4wdFgxPzgfuJ%3CP47eAB6SW*7eAe6eJBFh%3Cd7TZ37lFXitfB7eAe6eJBFhZByg9uSg6d7TZ37BiDZH4xwL4EwLAlwB6kZL6*ZLwd7T7L7tZ*7eAB6T4e7T7L7lfpFIWPwj%3CdfTFc64oj6PR6wj77AHZAgTiBZk2eTjDkTjFRRA8ewBRARkpi6kJSTkZSR47cA%3CCZfjJNAAJcgLAeR%3CNhS4kfT%3CROZAE5fkb66fRKZ%3Cf0ZPP5S4%3ClZ4ZZS%3CpZ7eAe6eJlig*d7TZ37B%3Cd7T7L7lZjygkP7eAB6T%3CkOTcDwBWjOLwxZLWPZj6/&p=&loc=https://passport.jd.com/new/login.aspx?ReturnUrl=https%253A%252F%252Fwww.jd.com%252F&callback=jsonp_024043174570774073'
        self.session.get(jseq_url, headers=self.headers)
        time.sleep(0.5)

        self.get_tracks()  # 生成轨迹信息
        self.encrypt_tracks()  # 加密轨迹信息

        varify_captcha_url = 'https://iv.jd.com/slide/s.html'
        params = {
            'd': self.encrypt_d,
            'c': self.challenge,
            'w': '278',
            'appId': '1604ebb2287',
            'scene': 'login',
            'product': 'click-bind-suspend',
            'e': 'U6HBJ4BTP3BIR3TY637P2ON5OFQEO234TGZXCWROSRFBHPKMWGEQGHX52DAWJMULDN5NOWXPATJ4EF6YOJA66CMHJM',
            's': self.session_id,
            'o': 'lk lk',
            'lang': 'zh_CN',
            'callback': 'jsonp_0840538308038782'
        }
        self.headers.update({
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout'
        })
        res = self.session.get(varify_captcha_url, params=params, headers=self.headers)
        return res

    def get_tracks(self):
        trace = []
        timestamp = int(time.time() * 1000)
        trace.append(['897', '195', timestamp])

        # 设置初始位置、初始速度、时间间隔
        random_distance = random.randint(5, 10)
        start = 905 + random_distance
        end_ponit = start + self.distance
        faster_distance = start + self.distance * 0.8

        # 当尚未移动到终点时
        while start < end_ponit:
            item = []
            item.append(str(int(start)))
            if start < 950:
                item.append('225')
            else:
                item.append('226')
            item.append(int(time.time() * 1000))

            # 将移动的距离加入轨迹列表
            trace.append(item)
            time.sleep(random.uniform(0.005, 0.008))

            # 如果处于加速阶段
            if start < faster_distance:
                v = random.uniform(0.8, 3.5)
            # 如果处于减速阶段
            else:
                v = random.uniform(0.5, 0.8)

            # 移动的距离公式
            t = random.uniform(0.8, 1.0)
            move = v * t
            start += move
        # 轨迹信息
        self.trace = trace
        # print(trace)
        # print(len(trace))

    def encrypt_tracks(self):
        with open('jd_login_for_request/jd_01.js') as f:
            js = f.read()

        js_ctx = execjs.compile(js)
        self.encrypt_d = js_ctx.call('gc', self.trace)


def main():
    jd_login = JdLogin()
    while True:
        jd_login.get_session_id()
        jd_login.get_captcha()
        login_res = jd_login.varify_captcha()
        print(login_res.text)
        if 'validate' in login_res.text:
            print('成功')
            break

        time.sleep(3)


if __name__ == '__main__':
    main()