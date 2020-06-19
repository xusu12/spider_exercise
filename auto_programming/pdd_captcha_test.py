#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pdd_manage_login.py
# @Author : xusu

"""
    拼多多商家后台自动登录程序  使用pyppeteer框架
"""

import os
import sys
sys.path.insert(0, os.getcwd())

import cv2
import time
import json
import random
import asyncio
import requests
import traceback

from hashlib import md5
from pyppeteer import launch
from urllib import request
from pprint import pprint
from PIL import ImageFont, ImageDraw, Image
import numpy as np

from auto_programming.redis_conf import get_redis_conn
from auto_programming.logger import get_stream_logger


class Auto_Login(object):
    def __init__(self):
        self.ip = 'http://172.16.100.110/'
        self.username = 'xusu12'
        password = 'xs1104963601'
        self.password = md5(password.encode('utf8')).hexdigest()
        self.soft_id = '905935'

        self.logger = get_stream_logger('pdd_manage_login')
        self.redis_conn = get_redis_conn()
        self.shop_cookies = []
        self.shop_info = {}

    async def strat(self):
        """
            自动登录操作
        """
        interval = 10 + random.randint(5, 10)
        await self.browser_operate()

    # 登录功能浏览器操作
    async def browser_operate(self):

        try:
            browser = await launch({
                'headless': False,
                'args': ['--no-sandbox', '--window-size=1920,1040'],
            })
            page = await browser.newPage()

            # 移除 Pyppeteer 中的window.navigator.webdriver
            await page.evaluateOnNewDocument('''() => {
                    Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                    })
                    }
                ''')
            await page.setViewport({'width': 1920, 'height': 1040})

            cookies_string = 'api_uid=CiU8c13kzc1niwA8RgSJAg==; _nano_fp=Xpd8npP8npUJlpTjX9_E6yoJLoW_UUJbCPFDazTc; msec=1800000; rec_list_orders=rec_list_orders_vQc81T; undefined=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F80.0.3987.163%20Safari%2F537.36; chat_list_rec_list=chat_list_rec_list_kvo9Br; mlp-fresher-mix=mlp-fresher-mix_iwULKM; ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F83.0.4103.106%20Safari%2F537.36; webp=1; Hm_lvt_1370d93b7ce0e6f1d870cef43042d966=1590391632,1591324063,1591951035,1592366029; PDDAccessToken=SU7TH5N64ZTP5AGDKXUQ43ESOHGP2KT352CRMC6UMDLI5OGX7QSQ1119ca0; pdd_user_uin=Z5QFTRWNWMRXEUVHCGOCM4MEXA_GEXDA; pdd_user_id=5842365062556; rec_list_personal=rec_list_personal_conai6; JSESSIONID=33CB30F9CE3FBF18747F8A8A926D0A09; Hm_lpvt_1370d93b7ce0e6f1d870cef43042d966=1592464934'

            cookies = []
            for item in cookies_string.split(';'):
                cookie_item = {}
                value = item.replace(
                    item.split('=')[0] + '=', ''
                )
                cookie_item['name'] = item.split('=')[0].strip()
                cookie_item['value'] = value
                cookie_item['domain'] = '.yangkeduo.com'
                cookies.append(cookie_item)
            await page.setCookie(*cookies)
            await page.goto('http://mobile.yangkeduo.com/')
            await page.waitFor(2000)

            await page.goto('http://yangkeduo.com/personal.html')
            await page.waitFor(2000)

            # 获取背景图和验证码文字
            captcha_img_src = await page.Jeval('#captchaClickImg', 'el => el.src')
            request.urlretrieve(captcha_img_src, './captcha_img.png')
            captcha_text = await page.Jeval('.picture-text', 'el => el.textContent')

            # 将文字添加到图片中去
            bk_img = cv2.imread("./captcha_img.png")
            # 设置需要显示的字体
            fontpath = "/usr/local/sunlogin/res/font/wqy-zenhei.ttc"
            font = ImageFont.truetype(fontpath, 18)
            img_pil = Image.fromarray(bk_img)
            draw = ImageDraw.Draw(img_pil)
            # 绘制文字信息
            draw.text((0, 0), captcha_text, font=font, fill=(0, 0, 0))
            bk_img = np.array(img_pil)
            cv2.imwrite("./captcha_img1.png", bk_img)

            # 定位验证码图片
            el = await page.J('#captchaClickImg')
            border = await el.boundingBox()  # 获取元素的边界框

            # 通过超级鹰识别验证码  获取要点击的位置坐标
            point_list = await self.chaojiying_captcha()
            if point_list:
                for point in point_list:
                    x = int(point.split(',')[0]) * 514 / 327
                    y = int(point.split(',')[1]) * 514 / 327

                    # 点击坐标点
                    await page.hover('#captchaClickImg')
                    await page.mouse.move(border['x'] + x, border['y'] + y)
                    await page.mouse.down()
                    await page.mouse.up()
                    await page.waitFor(1000)

            await page.waitFor(300000)

        except Exception as e:
            traceback.print_exc()
            self.logger.error('登录失败： {}'.format(e))

        # 关闭浏览器
        await browser.close()

    async def chaojiying_captcha(self):
        base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

        im = open('./captcha_img1.png', 'rb').read()
        params = {
            'codetype': 9004,
        }
        params.update(base_params)
        files = {'userfile': ('ccc.jpg', im)}
        res = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                            headers=headers)
        pic_str = res.json().get('pic_str')
        return pic_str.split('|')


def main():
    auto_login = Auto_Login()
    asyncio.get_event_loop().run_until_complete(auto_login.strat())


if __name__ == '__main__':
    main()
