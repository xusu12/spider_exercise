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
driver.get('http://wenshu.court.gov.cn/')
time.sleep(2)




time.sleep(100000)
driver.quit()