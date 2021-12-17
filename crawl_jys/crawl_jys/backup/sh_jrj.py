# -*- coding: utf-8 -*-
import datetime
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from selenium import webdriver
from selenium.webdriver import FirefoxProfile, DesiredCapabilities,Firefox

from crawl_jys.items import CrawlJysItem


class ShJrjSpider(scrapy.Spider):
    name = 'sh_jrj'
    start_urls = ['https://www.shanghai.gov.cn']
    keywords = ["农村产权", "产权交易所", "股权交易中心", "知识产权", "文化产权", "碳排放权", "要素交易场所", "交易市场建设"]
    date_limit = 60

    def get_sleeptime(self):
        return random.random() + 1

    def get_element_by_xpath(self, xp, *inv_xp):
        if inv_xp != ():
            for ixp in inv_xp:
                WebDriverWait(self.browser, 10).until(EC.invisibility_of_element((By.XPATH, ixp)))
        return WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        profile = FirefoxProfile()
        profile.set_preference('devtools.jsonview.enabled', False)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        options = webdriver.FirefoxOptions()
        # options.add_argument('-headless')     #取消注释则以无界面形式启动
        desired = DesiredCapabilities.FIREFOX
        self.browser = Firefox(firefox_profile=profile, desired_capabilities=desired,
                               executable_path='../geckodriver.exe',
                               options=options)
        self.items = []

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        input_xpath = "//input[@id='search-input']"
        search_xpath = "//button[@id='searchBtn']"
        self.default_handle = self.browser.current_window_handle

        for keyword in self.keywords[:]:
            input = self.browser.find_element_by_xpath(input_xpath)
            input.clear()
            input.send_keys(keyword)
            self.browser.find_element_by_xpath(search_xpath).click()
            time.sleep(self.get_sleeptime())
            handles = list(self.browser.window_handles)
            handles.remove(self.default_handle)
            self.browser.switch_to.window(handles[0])
            print(self.browser.current_url, "keyword = " + keyword)
            # 选择单位：金融局
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element((By.XPATH, "//div[@id='layui-layer-shade1']")))
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='results']")))
            time.sleep(1)
            self.browser.find_elements_by_xpath("//a[@tabindex='0']")[1].click()
            self.get_element_by_xpath("//a[@data-code='jrj.sh.gov.cn']").click()

            # 在《要闻动态》下搜索
            self.get_element_by_xpath("//li[@data-channel='xwzx']", "//div[@id='layui-layer-shade2']").click()
            self.get_data(keyword)

            # 在《政务公开》下搜索
            self.get_element_by_xpath("//li[@data-channel='xxgk']", "//div[@id='layui-layer-shade2']").click()
            self.get_data(keyword)

            self.browser.close()
            self.browser.switch_to.window(self.default_handle)

        self.browser.close()
        for item in self.items:
            yield item

    def get_data(self, keyword):
        time.sleep(1)
        # 时间范围选择一年内
        self.get_element_by_xpath("//a[@id='drop6']", "//div[@id='layui-layer-shade5']",
                                  "//div[@id='layui-layer-shade3']").click()

        self.get_element_by_xpath("//a[@data-filter-value='4']", "//div[@id='layui-layer-shade5']").click()
        # 再改变时间范围。前1~365天
        thred = datetime.date.today() - datetime.timedelta(ShJrjSpider.date_limit)
        for i in range(5):
            try:
                self.browser.find_element_by_xpath("//div[@id='searchMoreDiv']/a").click()
            except Exception as e:
                print(e)
                break
            time.sleep(self.get_sleeptime())
        time.sleep(self.get_sleeptime() + 1)
        news = self.browser.find_elements_by_xpath("//div[@class='result result-elm']")
        for new in news:
            news_date = new.find_element_by_xpath(".//font[@color='#9a9a9a']").text.split("-")
            news_date = [i for i in map(lambda x: int(x), news_date)]
            nDate = datetime.date(news_date[0], news_date[1], news_date[2])
            if nDate >= thred:
                content = new.find_element_by_xpath(".//div[@class='content']")
                if keyword in content.text:
                    print("-----", content.text, "--------" + new.find_element_by_xpath("a").get_attribute("href"))
                    item = CrawlJysItem()
                    item['date'] = str(nDate)
                    item['source'] = self.name
                    item['keyword'] = keyword
                    item['content'] = content.text + "..."
                    old_url = new.find_element_by_xpath("a").get_attribute("href")
                    item['url'] = self.get_real_url(old_url)
                    self.items.append(item)

    def get_real_url(self, url):
        js = 'window.open("%s");' % url  # 通过执行js，开启一个新的窗口
        self.browser.execute_script(js)
        time.sleep(self.get_sleeptime())
        handls = list(self.browser.window_handles)
        pre_handls = handls[:-1]
        for pre_handl in pre_handls:
            handls.remove(pre_handl)
        self.browser.switch_to.window(handls[0])
        real_url = self.browser.current_url
        self.browser.close()

        self.browser.switch_to.window(pre_handls[-1])
        return real_url
