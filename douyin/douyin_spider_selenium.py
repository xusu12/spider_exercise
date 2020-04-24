import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# 创建Options对象
options = Options()
options.set_headless()

# 创建Chrome的驱动对象
driver = webdriver.Chrome()

url = 'https://www.douyin.com/share/user/102148029874'
driver.get(url)

