# -*- coding: utf-8 -*-
import datetime
import random
import time

import redis
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from selenium import webdriver
from selenium.webdriver import FirefoxProfile, DesiredCapabilities,Firefox
from crawl_jys.items import CrawlJysItem

class AhFgwSpider(scrapy.Spider):
    name = 'ah_fgw'
    start_urls = ['http://fzggw.ah.gov.cn']

    keywords = ["知识产权", "农村产权", "要素交易场所", "产权交易所", "股权交易中心", "文化产权", "碳排放权", "交易市场建设"]
    date_limit = 60
    max_page = 30

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
        self.myPool = redis.ConnectionPool(host='192.168.12.233', port=6379, db=2)
        self.rds = redis.Redis(connection_pool=self.myPool)

        self.items = []

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        input_xpath = "//div[@class='search fl']//input[@class='search-keywords']"
        search_xpath = "//div[@class='search fl']//input[@name='input']"
        self.default_handle = self.browser.current_window_handle

        for keyword in self.keywords[:]:
            input = self.browser.find_element_by_xpath(input_xpath)
            input.click()
            input.clear()
            input.send_keys(keyword)
            self.get_element_by_xpath(search_xpath).click()

            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='searchlistw']/ul[@class='search-list']")))
            new_url = self.browser.current_url
            self.browser.back()
            js = 'window.open("%s");' % new_url  # 通过执行js，开启一个新的窗口
            self.browser.execute_script(js)
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
            if self.rds.get(item['url']):
                continue
            # self.rds.set(item['url'],1)
        #     yield item
        self.rds.close()

    def get_data(self, keyword):
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='reslut_type date_type']//a")))
        self.browser.find_elements_by_xpath("//div[@class='reslut_type date_type']//a")[-1].click()

        thred = datetime.date.today() - datetime.timedelta(AhFgwSpider.date_limit)
        try:
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='searchlistw']/ul[@class='search-list']")))
        except Exception as e:
            print(e)
            print("没有搜索结果")
            return
        #
        has_next = True
        cur_page = 1
        while (has_next):
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='searchlistw']//li[@class='search-url']")))
            news = self.browser.find_elements_by_xpath("//div[@class='searchlistw']/ul[@class='search-list']")
            for new in news:
                news_date = new.find_element_by_xpath(".//span[@class='date']").text.split("-")
                news_date = [i for i in map(lambda x: int(x), news_date)]
                nDate = datetime.date(news_date[0], news_date[1], news_date[2])
                if nDate >= thred:
                    content = new.find_element_by_xpath(".//li[@class='search-info']")
                    if keyword in content.text:
                        item = CrawlJysItem()
                        item['title'] = new.find_element_by_xpath(".//li[@class='search-title']/a").get_attribute("title")
                        item['date'] = str(nDate)
                        item['source'] = self.name
                        item['keyword'] = keyword
                        item['content'] = content.text + "..."
                        item['url'] = new.find_element_by_xpath(".//li[@class='search-url']/a").get_attribute("href")
                        self.items.append(item)
                        print(item)

            try:
                next = self.browser.find_elements_by_xpath(".//div[@id='page_new']//a")[-2]
                if next.text == '下一页' and self.max_page > cur_page:
                    next.click()
                    cur_page+=1
                else:
                    has_next = False
            except Exception as e:
                print(e)
                has_next = False


