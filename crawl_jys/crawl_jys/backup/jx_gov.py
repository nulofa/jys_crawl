# -*- coding: utf-8 -*-
import datetime
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxProfile, DesiredCapabilities, Firefox, ActionChains

from crawl_jys.items import CrawlJysItem


class JxGovSpider(scrapy.Spider):
    name = 'jx_gov'
    start_urls = ['http://jiangxi.gov.cn']

    keywords = ["知识产权", "农村产权", "产权交易所", "股权交易中心", "文化产权", "碳排放权", "要素交易场所", "交易市场建设"]
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
        input_xpath = "//input[@id='q']"
        search_xpath = "//input[@class='form_sub']"
        self.default_handle = self.browser.current_window_handle

        for keyword in self.keywords[:]:
            input = self.get_element_by_xpath(input_xpath)
            input.clear()
            input.send_keys(keyword)
            self.get_element_by_xpath(search_xpath).click()
            time.sleep(self.get_sleeptime())

            handles = list(self.browser.window_handles)
            handles.remove(self.default_handle)
            self.browser.switch_to.window(handles[0])
            print(self.browser.current_url, "keyword = " + keyword)

            self.get_data(keyword)

            self.browser.close()
            self.browser.switch_to.window(self.default_handle)

        self.browser.close()
        for item in self.items:
            yield item

    def get_data(self, keyword):

        # 时间范围选择
        timeStart = self.get_element_by_xpath("//input[@id='date_start']")
        timeStart.click()
        thred = datetime.date.today() - datetime.timedelta(JxGovSpider.date_limit)
        timeStart.send_keys(str(thred))

        time.sleep(1)
        timeEnd = self.get_element_by_xpath("//input[@id='date_end']")
        timeEnd.click()
        timeEnd.send_keys(str(datetime.date.today()))
        timeEnd.send_keys(Keys.ENTER)


        while (True) :
            try:
                self.get_element_by_xpath("//div[@class='uploadmore']").click()
            except Exception as e:
                print(e)
                break

        news = self.browser.find_elements_by_xpath("//div[@class='jcse-result-box news-result']")

        for new in news:
            content = new.find_element_by_xpath(".//div[@class='jcse-news-abs-content']")
            news_date = new.find_element_by_xpath(".//span[@class='jcse-news-date']").text.split("-")
            news_date = [i for i in map(lambda x: int(x), news_date)]
            nDate = datetime.date(news_date[0], news_date[1], news_date[2])
            if keyword in content.text:
                print("-----", content.text, "--------" + new.find_element_by_xpath(".//div[@class='jcse-news-url']/a").get_attribute("text"))
                item = CrawlJysItem()
                item['date'] = str(nDate)
                item['source'] = self.name
                item['keyword'] = keyword
                item['content'] = content.text + "..."
                item['url'] = new.find_element_by_xpath(".//div[@class='jcse-news-url']/a").get_attribute("text")
                self.items.append(item)

