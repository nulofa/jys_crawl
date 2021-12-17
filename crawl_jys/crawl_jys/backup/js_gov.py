# -*- coding: utf-8 -*-
import datetime
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from selenium import webdriver
from selenium.webdriver import FirefoxProfile, DesiredCapabilities, Firefox, ActionChains


class JsGovSpider(scrapy.Spider):
    name = 'js_gov'
    start_urls = ['http://www.jiangsu.gov.cn']
    keywords = ["农村产权", "产权交易所", "股权交易中心", "知识产权", "文化产权", "碳排放权", "要素交易场所", "交易市场建设"]
    date_limit = 60

    def get_sleeptime(self):
        return random.random() + 1

    def get_element_by_xpath(self, xp, *inv_xp):
        if inv_xp != ():
            for ixp in inv_xp:
                WebDriverWait(self.browser, 10).until(EC.invisibility_of_element((By.XPATH, ixp)))
        return WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))

    def __init__(self):
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

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        input_xpath = "//input[@class='searchtext']"
        search_xpath = "//div[@class='searchbutton']"
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

            self.get_data(keyword)

            self.browser.close()
            self.browser.switch_to.window(self.default_handle)

        self.browser.close()

    def get_data(self, keyword):
        # 时间范围选择一年内
        timeSelector = self.get_element_by_xpath("//input[@id='date_start']")
        ActionChains(self.browser).move_to_element(timeSelector).perform()
        self.get_element_by_xpath("//div[@data-value='4']").click()

        # 再改变时间范围。前1~365天
        thred = datetime.date.today() - datetime.timedelta(JsGovSpider.date_limit)

        news = self.browser.find_elements_by_xpath("//div[@class='jcse-result-box news-result']")
        for new in news:
            news_date = new.find_element_by_xpath(".//span[@class='jcse-news-date']")\
                .text.split(" ").split("-")
            print(news_date)
    #         news_date = [i for i in map(lambda x: int(x), news_date)]
    #         nDate = datetime.date(news_date[0], news_date[1], news_date[2])
    #         if nDate >= thred:
    #             content = new.find_element_by_xpath(".//div[@class='content']")
    #             if keyword in content.text:
    #                 print("-----", content.text, "--------" + new.find_element_by_xpath("a").get_attribute("href"))
    #
    # def detail_parse(self, response):
    #     print("-----", response.url)
    #     self.browser.close()
    #     self.browser.switch_to.window(self.default_handle)
