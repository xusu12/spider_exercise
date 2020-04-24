import random

from selenium import webdriver
import time
from selenium.webdriver import ActionChains
import requests

driver = webdriver.Chrome()

# 请求目标网站的网址
driver.get('https://login.zhipin.com/?ka=header-login')
time.sleep(0.1)


# # 页面有iframe 需要切换至iframe  但是iframe没有id和name属性  需要先通过标签名找到iframe  然后再切换
# iframe = driver.find_elements_by_tag_name("iframe")[0]
#
# # 切换至iframe
# driver.switch_to.frame(iframe)

# 输入用户名和密码
ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div[1]/form/div[1]/span[2]/input').send_keys('1104963431x')
ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div[1]/form/div[2]/span/input').send_keys('xs1104963601')

# # 滑动验证码
action = ActionChains(driver)
source = driver.find_element_by_xpath("//*[@id='nc_2_n1z']")  # 找到滑动的按钮

action.click_and_hold(source).perform()  # 鼠标左键按下不放
time.sleep(0.2)

# 计算要滑动的距离
distance = 270
# distance -= source.size.get('width') / 2
# distance += 15
while distance > 0:
    if distance > 10:
        # 如果距离大于10，就让他移动快一点
        span = random.randint(15, 18)
    else:
        # 快到缺口了，就移动慢一点
        span = random.randint(1, 2)
    action.move_by_offset(span, 1).perform()
    distance -= span
    time.sleep(random.randint(10, 50) / 100)

action.move_by_offset(distance, 1).perform()  # 需要滑动的坐标

action.release(on_element=source).perform()  # 释放鼠标

time.sleep(5)
#
# driver.find_element_by_id('J_SubmitStatic').click()
#
# time.sleep(10)
# driver.quit()
