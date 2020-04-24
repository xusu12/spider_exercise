import time

from selenium import webdriver
import json
import js2py


class PlaySpider(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        # - 请求租房首页
        self.driver.get('https://play.google.com/store/apps/collection/topselling_free?hl=zh-CN')

    def get_data(self):
        divs = self.driver.find_elements_by_xpath('//*[@id="body-content"]/div/div/div[1]/div/div/div/div[2]/div')

        for div in divs:
            item = {}
            item['app_name'] = div.find_element_by_xpath('.//div[@class="details"]/a[@class="title"]').text
            print(item)

    def run(self):

        # while True:
        # 需要找到停止循环的条件  页面全部加载完成  不能再滚动的时候
        # 思路： 当上一次滚动的页面的y坐标和本次滚动的y坐标相同  说明已经到最底部了
        for i in range(5):
            print(self.driver.execute_script('document.body.scrollHeight'))
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
        self.get_data()

        # 退出浏览器
        self.driver.quit()


if __name__ == '__main__':
    ps = PlaySpider()
    ps.run()
