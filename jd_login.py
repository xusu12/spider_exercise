import random

from selenium import webdriver
import time
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import requests
from lxml import etree


option = ChromeOptions()
# Chrome开启实验性功能参数  新版Chrome已经失效
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
# driver = webdriver.Chrome(options=option)

driver = webdriver.Chrome()

# 隐藏window.navigator.webdriver值
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})


# 请求目标网站的网址
driver.get('https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F')
time.sleep(2)


# 点击账号登录
driver.find_element_by_xpath('//*[@class="login-form"]/div[3]/a').click()

# 输入账号密码
driver.find_element_by_xpath('//*[@id="loginname"]').send_keys('广州恒大淘宝官方旗舰店')
driver.find_element_by_xpath('//*[@id="nloginpwd"]').send_keys('itsales178')

# 点击登录
driver.find_element_by_xpath('//*[@id="loginsubmit"]').click()

distance = input('输入移动的距离：')

oo = driver.find_element_by_xpath('//*[@class="JDJRV-suspend-slide"]/div/div/div[2]/div[3]')
print(oo.get_attribute('innerHTML'))
ActionChains(driver).move_to_element(oo).perform()

# 滑动验证码
action = ActionChains(driver)
source = driver.find_element_by_xpath('//*[@class="JDJRV-suspend-slide"]/div/div/div[2]/div[3]')  # 找到滑动的按钮
action.click_and_hold(on_element=source).perform()  # 鼠标左键按下不放
# action.move_by_offset(distance, 0).perform()  # 需要滑动的坐标

distance = int(distance)
while distance > 0:
  if distance > 10:
    # 如果距离大于10，就让他移动快一点
    span = random.randint(15, 18)
  else:
    # 快到缺口了，就移动慢一点
    span = random.randint(1, 2)
    span = 1
  ActionChains(driver).move_by_offset(span, 0).perform()
  distance -= span
  time.sleep(random.randint(10, 50) / 100)
# ActionChains(driver).move_by_offset(1, 0).perform()
action.release(on_element=source).perform()  # 释放鼠标

time.sleep(100000)
driver.quit()