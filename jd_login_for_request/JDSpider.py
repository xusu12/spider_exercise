# coding:utf-8
import base64
import json
import random
import re
import cv2
import numpy as np
import requests
import time

import execjs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_tracks(distance):
    # 构造滑动轨迹
    '''
    :param distance: (Int)缺口离滑块的距离
    :return: (List)移动轨迹
    '''
    # 创建存放轨迹信息的列表
    trace = []
    # 设置加速的距离
    faster_distance = distance * 3 / 5

    # 设置初始位置、初始速度、时间间隔
    start, v0, t = 0.0, 0.5, 0.2
    # 当尚未移动到终点时
    while start < distance:
        # 如果处于加速阶段
        if start < faster_distance:
            # 设置加速度为2
            a = round(random.uniform(0.5, 0.8), 2)
        # 如果处于减速阶段
        else:
            # 设置加速度为-3
            a = round(random.uniform(-0.7, -0.9), 2)
        # 移动的距离公式
        move = v0 * t + 1 / 2 * a * t * t
        move = int(move)
        # 此刻速度
        v = v0 + a * t
        # 重置初速度
        v0 = v
        # 重置起点
        start += move
        # 将移动的距离加入轨迹列表
        trace.append(round(move))
    # 返回轨迹信息
    return trace


def show(name):
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main(username, passworld):
    while True:

        session = requests.session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }

        url = 'https://passport.jd.com/new/login.aspx'
        res_login = session.get(url)
        con = res_login.text

        sa_token = re.findall('name="sa_token"[\s\S]*?value="([\s\S]*?)"', con)[0]
        # print("sa_token:", sa_token)
        uuid = re.findall('name="uuid"[\s\S]*?value="([\s\S]*?)"', con)[0]
        # print("uuid:", uuid)
        pubKey = re.findall('name="pubKey"[\s\S]*?value="([\s\S]*?)"', con)[0]
        # print("pubKey:", pubKey)
        slideAppId = re.findall('"slideAppId"[\s\S]*?value="([\s\S]*?)"', con)[0]
        # print("slideAppId:", slideAppId)
        sessionId = re.findall('"sessionId"[\s\S]*?value="([\s\S]*?)"', con)[0]
        # print("sessionId:", sessionId)

        url = 'https://seq.jd.com/jseqf.html?bizId=passport_jd_com_login_pc&platform=js&version=1'
        r = session.get(url, verify=False)
        seqSid = re.compile('sessionId="(.+?)"').findall(r.text)[0]
        # print("seqSid:", seqSid)
        eid = 'C5QSAXLJ5UUXFOPHW2LQCCHPMDK7PXNODEH3WDB4VPPF5FL3SUXEGVLUNTHWEKQP26V26DPGQ3KGU6D7JXBNIIODUU'
        url = 'https://iv.jd.com/slide/g.html'
        payload = {
            'appId': '1604ebb2287',
            'scene': 'login',
            'product': 'click-bind-suspend',
            'e': eid,
            'callback': '',
        }
        r = session.get(url, params=payload)
        image_info = r.json()
        challenge = image_info.get('challenge')
        # print("challenge:", challenge)
        y = image_info.get("y")
        print("-----y:", y)

        patch = image_info.get("patch")
        # print patch
        img = base64.b64decode(patch)
        file = open('./images/patch.jpg', 'wb')
        file.write(img)
        file.close()

        bg = image_info.get("bg")
        # print bg
        img = base64.b64decode(bg)
        file = open('./images/bg.jpg', 'wb')
        file.write(img)
        file.close()
        # =========================================================
        otemp = './images/patch.jpg'
        oblk = './images/bg.jpg'
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)
        # 图片的宽 高
        w, h = target.shape[::-1]
        temp = './images/temp.jpg'
        targ = './images/targ.jpg'
        # 重新保存图像
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)

        target = cv2.imread(targ)
        # 灰度图
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

        # abs绝对值   灰度转换一下，为了使大图的缺口跟小图灰度一样
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)

        # 归一化相关系数匹配CV_TM_CCOEFF_NORMED  大图里面找小图
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        print("x: %s" % y)
        print("y: %s" % x)

        array = [["897", "191", int(time.time() * 1000)]]
        start = random.randint(6, 11)
        time.sleep(0.01)
        x1 = random.randint(8, 25)
        sum_ = 897
        array.append([str(sum_ + x1), "205", int(time.time() * 1000)])
        tracks = get_tracks(y * 28 / 36)
        sum_ = sum_ + x1

        for tra in tracks[0:start]:
            # time.sleep(random.randint(1,100)*0.001)
            sum_ += int(tra)
            array.append([str(sum_), "225", int(time.time() * 1000)])

        for tra in tracks[start:]:
            sum_ += int(tra)
            # time.sleep(random.randint(1, 100) * 0.001)
            array.append([str(sum_), "223", int(time.time() * 1000)])

        print(len(array))
        js = """
        function gc(c) {
        var b = new Array();
        for (var e = 0; e < c.length; e++) {
            if (e == 0) {
                b.push(pm(c[e][0] < 262143 ? c[e][0] : 262143, 3, true));
                b.push(pm(c[e][1] < 16777215 ? c[e][1] : 16777215, 4, true));
                b.push(pm(c[e][2] < 4398046511103 ? c[e][2] : 4398046511103, 7, true))
            } else {
                var a = c[e][0] - c[e - 1][0];
                var f = c[e][1] - c[e - 1][1];
                var d = c[e][2] - c[e - 1][2];
                b.push(pm(a < 4095 ? a : 4095, 2, false));
                b.push(pm(f < 4095 ? f : 4095, 2, false));
                b.push(pm(d < 16777215 ? d : 16777215, 4, true))
            }
        }
        return b.join("")
    }

        function pm(d, c, b) {
        var e = st(Math.abs(d));
        var a = "";
        if (!b) {
            a += (d > 0 ? "1" : "0")
        }
        a += pi(e, c);
        return a
    }
        function st(d) {
        var c = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-~".split("")
          , b = c.length
          , e = +d
          , a = [];
        do {
            mod = e % b;
            e = (e - mod) / b;
            a.unshift(c[mod])
        } while (e);return a.join("")
    }
    function pi(a, b) {
            return (Array(b).join(0) + a).slice(-b)}

        """
        ctx = execjs.compile(js)
        d = ctx.call("gc", array)
        # print(d)

        c = challenge
        w = "278"
        appId = "1604ebb2287"
        scene = "login"
        product = "click-bind-suspend"
        o = username
        lang = "zh_CN"
        callback = "jsonp_0782177664387067"
        e = eid
        s = seqSid
        url = "https://iv.jd.com/slide/s.html?d=%s&c=%s&w=%s&appId=%s&scene=%s&product=%s&" \
              "o=%s&lang=%s&e=%s&s=%s&callback=%s" % (d, c, w, appId, scene, product, o, lang, e, s, callback)
        # print(url)
        headers = {
            "Referer": "https://passport.jd.com/new/login.aspx?ReturnUrl=http%3A%2F%2Fhome.jd.com%2F",
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"

        }
        session.get(
            "https://seq.jd.com/jseq.html?d=7TJI7tFPWdZpzlDd7TZ37B%3CuwIWPw4wdiQPmSg6d7TZ37t3bWtZ*zt7jhlp4hlZXzf9szlJpzP9*ieWPw4wdFgxPzgfuJ%3CP47eAB6SW*7eAe6eJBFh%3Cd7TZ37lFXitfB7eAe6eJBFhZByg9uSg6d7TZ37BwBZB%3CxwTw*OT2jwB6*wBwEwLcd7T7L7tZ*7eAB6Twx7T7L7lfpFIWPwj%3Cd6BfRAjNiT%3CokfffiR496SNWeTNNL6jb6TARvZk3iT49%3CRAaBfjRIZNF6A%3CikR4*BAkfiRAJgTNfOf%3CbhRACRALclfHclRN31ATZvRkAlRLJKg%3C7OSAP5RNff7eAe6eJlig*d7TZ37B%3Cd7T7L7lZjygkP7eAB6T%3CkOTcDwHw*wBAjwB2PZj6/&p=&loc=https://passport.jd.com/new/login.aspx?ReturnUrl=https%253A%252F%252Fwww.jd.com%252F%253Fcu%253Dtrue%2526utm_source%253Dbaidu-pinzhuan%2526utm_medium%253Dcpc%2526utm_campaign%253Dt_288551095_baidupinzhuan%2526utm_term%253D0f3d30c8dba7459bb52f2eb5eba8ac7d_0_d08a017c60244c48a88ef7d056cffd71&callback=jsonp_01906351749652606")
        response = session.get(url, headers=headers)
        content = response.text
        print(content)

        if "validate" in content:

            # validate = json.loads(content)["validate"]
            print(content)
            break

        else:
            print("重新滑")
            time.sleep(2)


if __name__ == '__main__':
    username = u""
    passworld = ""
    main(username, passworld)
