from selenium import webdriver
import time
import requests
import yudama
from lxml import etree

driver = webdriver.Chrome()

driver.get('https://www.douban.com/')

driver.find_element_by_id('form_email').send_keys('15555081413')
driver.find_element_by_id('form_password').send_keys('xs1104963601')

# 识别验证码
# 获取图片验证码的url
image_url = driver.find_elements_by_id('captcha_image')
if len(image_url) != 0:
    # 获取图片验证码
    image_url = image_url[0].get_attribute('src')
    # 发送请求获取图片验证码
    response = requests.get(image_url)
    # 通过云打码获取验证码的内容
    code = yudama.indetify(response.content)
    # 再将验证码的内容填写进输入框
    driver.find_element_by_id('captcha_field').send_keys(code)

driver.find_element_by_class_name('bn-submit').click()
time.sleep(10)
driver.quit()