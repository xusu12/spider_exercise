"""
    css反爬   3508533
"""

import redis
import asyncio
import random
import cv2
import traceback
from pyppeteer import launch
from urllib import request


async def main():
    browser = await launch({
        'headless': False,
        'args': ['--no-sandbox', '--window-size=1366,768'],
    })
    page = await browser.newPage()
    await page.setViewport({'width': 1366, 'height': 768})
    await page.goto('http://glidedsky.com/level/web/crawler-css-puzzle-1')
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
    for r in range(1, 1001):
        while True:
            # 模拟人工拖动滑块、失败则重试
            try:
                print('正在获取第{}页的数据'.format(r))
                url = 'http://glidedsky.com/level/web/crawler-css-puzzle-1?page={}'.format(r)
                await page.goto(url)
                await page.waitFor(5000)

                rows = await page.xpath('//*[@class="row"]')
                col_mds = await rows[0].xpath('./div')
                j = 0
                page_sum = 0
                for col_md in col_mds:
                    j += 1
                    item_divs = await col_md.xpath('./div')
                    i = 0

                    # 获取一个数的每位的数值
                    full_num = 'none'
                    num_dict = {}

                    # 提取before内的数据
                    for item_div in item_divs:
                        i += 1
                        left = await page.evaluate("() => getComputedStyle(document.querySelector('.row > div:nth-child({}) > div:nth-child({})')).left".format(j, i))
                        left = left.replace('px', '')

                        if left == 'auto':
                            num = await page.evaluate(
                                "() => getComputedStyle(document.querySelector('.row > div:nth-child({}) > div:nth-child({})'), ':before').content".format(j, i))
                            if num:
                                full_num = num

                    # 提取不在before的数据  在三个或者四个子标签里面 需要进行偏移量计算
                    if full_num == 'none':
                        k = 0
                        for item_div in item_divs:
                            # 获取子标签的值
                            num = await (await item_div.getProperty('textContent')).jsonValue()  # 标签数值

                            # 提取偏移量
                            left = await page.evaluate("() => getComputedStyle(document.querySelector('.row > div:nth-child({}) > div:nth-child({})')).left".format(j, k+1))
                            left = left.replace('px', '')

                            if len(item_divs) == 4:
                                # 如果有四个子标签  第一个没用 后面的子标签按照偏移量排序
                                if k == 0:
                                    k += 1
                                    continue
                                # 如果子标签没有偏移
                                if left == 'auto':
                                    num_dict[k-1] = num
                                else:
                                    flag = int(float(left) / 14.4 + k - 1)
                                    num_dict[flag] = num

                            else:
                                if left == 'auto':
                                    num_dict[k] = num
                                else:
                                    flag = int(float(left) / 14.4 + k)
                                    num_dict[flag] = num
                            k += 1

                    if full_num != 'none':
                        num_item = int(full_num.replace('"', ''))
                    else:
                        num_item = int(num_dict[0] + num_dict[1] + num_dict[2])
                    page_sum += num_item

                # await page.evaluate("() => {rows = document.querySelectorAll('div.row > div')}")
                await page.waitFor(1000)
                break
            except Exception:
                traceback.print_exc()
                await page.waitFor(1000)
        sum += page_sum
        print(sum)


asyncio.get_event_loop().run_until_complete(main())