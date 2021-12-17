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


class ZjJrjSpider(scrapy.Spider):
    name = 'zj_jrj'
    start_urls = ['http://sjrb.zj.gov.cn']

    keywords = ["碳排放权", "知识产权", "农村产权", "要素交易场所", "产权交易所", "股权交易中心", "文化产权", "交易市场建设"]
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
        search_xpath = "//input[@id='tjiao']"
        self.default_handle = self.browser.current_window_handle

        for keyword in self.keywords[:]:
            input = self.browser.find_element_by_xpath(input_xpath)
            input.click()
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
        for item in self.items:
            yield item

    def get_data(self, keyword):

        self.get_element_by_xpath("//div[@class='TimeType lf']/p[@class='textWrap']").click()
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='TimeTypeList']")))
        # self.get_element_by_xpath("//div[@class='TimeTypeList']//p[@data-value='4']").click()

        from_date = datetime.date.today() - datetime.timedelta(ZjJrjSpider.date_limit)
        self.browser.find_element_by_xpath("//input[@class='utimeqsrq']").send_keys(str(from_date))
        self.browser.find_element_by_xpath("//input[@class='utimejsrq']").send_keys(str(datetime.date.today()))
        self.get_element_by_xpath("//input[@id='datebtu']").click()
        try:
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@id='pagination']//li[@class='totalPage']")))
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='jcse-result-box news-result']")))
        except Exception as e:
            print(e)
            print("没有搜索结果")
            return

        total_page = self.browser.find_elements_by_xpath("//div[@id='pagination']//li[@class='totalPage']")[1].text[
                     1:-1]
        total_page = int(total_page)
        cur_page = 0
        while (cur_page < total_page):
            cur_page += 1
            next = self.get_element_by_xpath("//div[@id='pagination']//li[last()-2]")

            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='jcse-result-box news-result']")))
            news = self.browser.find_elements_by_xpath("//div[@class='jcse-result-box news-result']")
            for new in news:
                nDate = new.find_elements_by_xpath(".//div[@class='website-source']/span")[0].text.split("：")[1].strip()
                content = new.find_element_by_xpath("./div[@class='jcse-news-abs']")
                if keyword in content.text:
                    print("-----", content.text,
                          "--------" + new.find_element_by_xpath("./div[@class='jcse-news-title']/a")
                          .get_attribute("href"))
                    item = CrawlJysItem()
                    item['date'] = str(nDate)
                    item['source'] = self.name
                    item['keyword'] = keyword
                    item['content'] = content.text + "..."
                    item['url'] = new.find_element_by_xpath("./div[@class='jcse-news-title']/a").get_attribute("href")
                    self.items.append(item)
            next.click()