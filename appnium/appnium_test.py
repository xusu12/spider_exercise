import time
from appium import webdriver

caps = {}
caps["platformName"] = "Android"
caps["platformVersion"] = "7.1.2"
caps["deviceName"] = "127.0.0.1:21513"
caps["appPackage"] = "com.tmall.wireless"
caps["appActivity"] = ".maintab.module.TMMainTabActivity"
caps["ensureWebviewsHavePages"] = True
caps['resetKeyboard'] = True
caps['noReset'] = True

# 连接测试机所在服务器服务器
driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', caps)

time.sleep(5)
driver.tap([(627, 1210), (668, 1251)], 500)  # 点击我的页面
time.sleep(2)
driver.tap([(81, 947), (156, 983)], 500)  # 点击小黑盒按钮

time.sleep(50)

#断开连接
driver.quit()
