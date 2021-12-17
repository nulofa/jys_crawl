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
from selenium.webdriver import FirefoxProfile, DesiredCapabilities, Firefox


class GdGovSpider(scrapy.Spider):
    name = 'gd_gov'
    start_urls = ['http://www.gd.gov.cn']

    keywords = ["知识产权", "农村产权", "产权交易所", "股权交易中心", "文化产权", "碳排放权", "要素交易场所", "交易市场建设"]
    date_limit = 60

    def get_sleeptime(self):
        return random.random() + 1

    def get_element_by_xpath(self, xp, *inv_xp):
        if inv_xp != ():
            for ixp in inv_xp:
                WebDriverWait(self.browser, 5).until(EC.invisibility_of_element((By.XPATH, ixp)))
        return WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))

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

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        input_xpath = "//form[@onsubmit='checkKey()']//input[@name='keywords']"
        search_xpath = "//form[@onsubmit='checkKey()']//button[@type='submit']"
        self.default_handle = self.browser.current_window_handle

        for keyword in self.keywords[:1]:
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

    def get_data(self, keyword):
        # 时间范围选择
        time.sleep(1)
        self.get_element_by_xpath("//div[@id='time-list']/a[@key='year']").click()
        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='total-line']")))

        thred = datetime.date.today() - datetime.timedelta(GdGovSpider.date_limit)


        while (True):
            news = self.browser.find_elements_by_xpath("//div[@id='list-body']/div[@class='list-item  all']")
            for new in news:
                new_date = new.find_elements_by_xpath("./div[@class='url-date ']/span")[-1].text.split("-")
                new_date = [i for i in map(lambda x: int(x), new_date)]
                nDate = datetime.date(new_date[0], new_date[1], new_date[2])
                if nDate>=thred:
                    content = new.find_element_by_xpath("./div[@class='content ']")
                    if keyword in content.text:
                        print("-----", content.text,
                              "--------" + new.find_element_by_xpath("./a[@class='title']").get_attribute("href"))
            try:  # 下一页
                cur_page = self.browser.find_element_by_xpath("//div[@id='page-list']/a[@class='item cur']")
                cur_page_num = cur_page.text
                cur_page_ulr = cur_page.get_attribute("href")
                next_url = cur_page_ulr.replace("page=%s" % cur_page_num, "page=%s" % str( int(cur_page_num)+1 ))
                self.browser.get(next_url)
            except Exception as e:
                print(e)
                break
            WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='total-line']")))
