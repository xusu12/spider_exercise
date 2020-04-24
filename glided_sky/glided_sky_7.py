"""
    验证码1  2446737
"""

import redis
import asyncio
import random
import cv2
from pyppeteer import launch
from urllib import request


redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# 滑块的缺口距离识别
async def get_distance():
    big_img = cv2.imread('big_img.png', 0)
    small_img = cv2.imread('small_img.png', 0)
    res = cv2.matchTemplate(big_img, small_img, cv2.TM_CCORR_NORMED)
    value = cv2.minMaxLoc(res)[2][0]
    distance = value * 0.5 - 20
    return distance


async def main():
    browser = await launch({
        'headless': False,
        'args': ['--no-sandbox', '--window-size=1366,768'],
    })
    page = await browser.newPage()
    await page.setViewport({'width': 1366, 'height': 768})
    await page.goto('http://glidedsky.com/level/web/crawler-captcha-1')
    await page.waitFor(2000)

    # 模拟人工输入用户名、密码
    await page.type('#email', '1104963431@qq.com',
                    {'delay': random.randint(60, 121)})
    await page.waitFor(1000)
    await page.type('#password', 'xs1104963601',
                    {'delay': random.randint(100, 151)})
    await page.waitFor(1000)
    # 点击登录按钮
    await page.click('.btn-primary')
    await page.waitFor(3000)

    sum = 0
    for i in range(1, 1001):
        # 模拟人工拖动滑块、失败则重试
        while True:
            try:
                print('正在获取第{}页的数据'.format(i))
                url = 'http://glidedsky.com/level/web/crawler-captcha-1?page={}'.format(i)
                await page.goto(url)
                await page.waitFor(2000)
                iframes = page.frames
                for iframe in iframes:
                    if iframe.name == 'tcaptcha_iframe':
                        frame = iframe

                small_img_url = await frame.Jeval('#slideBlockWrap > img', 'el => el.src')
                request.urlretrieve(small_img_url, 'small_img.png')
                big_img_url = await frame.Jeval('#slideBg', 'el => el.src')
                request.urlretrieve(big_img_url, 'big_img.png')
                await page.waitFor(1000)

                el = await frame.J('#tcaptcha_drag_thumb')
                box = await el.boundingBox()
                await frame.hover('#tcaptcha_drag_thumb')

                distance = await get_distance()
                await page.mouse.down()
                await page.mouse.move(box['x'] + distance + random.uniform(30, 33), box['y'], {'steps': 30})
                await page.waitFor(random.randint(300, 700))
                await page.mouse.move(box['x'] + distance + 29, box['y'], {'steps': 30})
                await page.mouse.up()
                await page.waitFor(2000)

                # 提取页面中的数据
                data_list = await page.querySelectorAll('#app > main > div.container > div > div > div > div')
                page_sum = 0
                for data_li in data_list:
                    # await data_li.Jeval('', 'el => el.value')
                    data = await page.evaluate('(el) => el.textContent', data_li)
                    data_num = data.strip()
                    page_sum += int(data_num)
                if page_sum == 0:
                    continue
                    # redis_conn.lpush('fail_key', i)
                sum += page_sum
                print(sum)
                break
            except Exception as e:
                print(i, e)
                await page.waitFor(1000)


asyncio.get_event_loop().run_until_complete(main())