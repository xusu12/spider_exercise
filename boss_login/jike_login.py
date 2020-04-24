import base64
import time
import random
import requests

import yudama
from selenium import webdriver
from selenium.webdriver import ActionChains


driver = webdriver.Chrome()

# 请求目标网站的网址
driver.get('https://passport.jikexueyuan.com/sso/login')
time.sleep(0.1)


# 输入用户名和密码
ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
driver.find_element_by_xpath('//*[@id="login-form"]/div[1]/div/input').send_keys('1104963431x')
time.sleep(0.2)
ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
driver.find_element_by_xpath('//*[@id="login-form"]/div[2]/div/input').send_keys('xs1104963601')
time.sleep(0.2)

# # 滑动验证码
action = ActionChains(driver)
source = driver.find_element_by_xpath("//*[@id='nc_1_n1z']")  # 找到滑动的按钮

action.click_and_hold(source).perform()  # 鼠标左键按下不放
time.sleep(0.2)

# 计算要滑动的距离
distance = 230

while distance > 0:
    if distance > 10:
        # 如果距离大于10，就让他移动快一点
        span = random.randint(50, 60)
        action.move_by_offset(span, 1).perform()
    else:
        # 快到缺口了，就移动慢一点
        span = random.randint(1, 2)
        action.move_by_offset(span, 1).perform()
    distance -= span
    time.sleep(random.randint(10, 50) / 100)

# action.move_by_offset(distance, 1).perform()  # 需要滑动的坐标

action.release(on_element=source).perform()  # 释放鼠标
# 获取图片验证码的url
image = driver.find_element_by_xpath('//*[@id="nc_1__imgCaptcha_img"]/img')
if image:
    # 获取图片验证码
    image_data = image.get_attribute('src').split(',')[1]
    print(image_data)
    # 获取图片数据
    imgdata = base64.b64decode(image_data)
    # 通过云打码获取验证码的内容
    code = yudama.indetify(imgdata)
    # 再将验证码的内容填写进输入框
    driver.find_element_by_id('nc_1_captcha_input').send_keys(code)
time.sleep(10)

driver.find_element_by_xpath('//*[@id="nc_1_scale_submit"]/span').click()

time.sleep(5)

