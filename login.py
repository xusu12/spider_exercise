import random

from selenium import webdriver
import time
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import requests


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
driver.get('https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9re7Pkb&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
time.sleep(2)


# 页面有iframe 需要切换至iframe  但是iframe没有id和name属性  需要先通过标签名找到iframe  然后再切换
iframe = driver.find_elements_by_tag_name("iframe")[0]

# 点击
# driver.find_element_by_id('J_Quick2Static').click()

# 输入用户名和密码
# ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
# driver.find_element_by_id('TPL_username_1').send_keys('广州恒大淘宝官方旗舰店:店长')
driver.find_element_by_id('TPL_username_1').send_keys('广州恒大淘宝官方旗舰店')
time.sleep(1)
# ActionChains(driver).move_by_offset(random.randint(10, 60), random.randint(10, 60)).perform()
driver.find_element_by_id('TPL_password_1').send_keys('itsales178')
time.sleep(1)

driver.find_element_by_id('J_SubmitStatic').click()
time.sleep(3)
#
# driver.find_element_by_id('TPL_password_1').send_keys('itsales178')
# time.sleep(1)
#
# # 滑动验证码
# action = ActionChains(driver)
# source = driver.find_element_by_xpath("//span[@id='nc_1_n1z']")  # 找到滑动的按钮
# action.click_and_hold(on_element=source).perform()  # 鼠标左键按下不放
# action.move_by_offset(200, 0).perform()  # 需要滑动的坐标
# action.release().perform()  # 释放鼠标

# driver.find_element_by_id('J_SubmitStatic').click()

driver.execute_script("""
console.log(111)
""")

time.sleep(100000)
driver.quit()