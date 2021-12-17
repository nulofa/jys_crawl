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

from crawl_jys.items import CrawlJysItem


class FjGovSpider(scrapy.Spider):
    name = 'fj_gov'
    start_urls = ['http://fj.gov.cn']

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
        self.items = []

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        input_xpath = "//input[@id='selecttags']"
        search_xpath = "//button[@class='btn_2021 iconfont']"
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
        WebDriverWait(self.browser, 5).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='searchTool']/a[@class='ss_ssgj b-free-read-leaf']")))
        self.get_element_by_xpath("//span[@id='searchTool']/a[@class='ss_ssgj b-free-read-leaf']").click()
        self.get_element_by_xpath("//span[@id='timeSelectContent']/a[@onclick='searchBean.timeSearchShow()']").click()
        # 时间范围选择
        timeStart = self.get_element_by_xpath("//input[@id='timezdyqsrq']")
        timeStart.click()
        # 等待日历出现
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='layui-laydate-content']")))

        pre_month = self.browser.find_elements_by_xpath("//div[@class='layui-laydate-header']/i")[1]
        pre_month.click()
        time.sleep(0.5)
        pre_month.click()
        time.sleep(0.5)
        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()

        # thred = datetime.date.today() - datetime.timedelta(FjGovSpider.date_limit)
        # timeStart.send_keys(str(thred))

        time.sleep(1)
        self.get_element_by_xpath("//input[@id='timezdyjsrq']").click()
        # 等待日历出现
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='layui-laydate-content']")))

        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()
        time.sleep(0.5)
        self.get_element_by_xpath('//button[@onclick="searchBean.timeLimitSearch()"]').click()



        while (True):
            try:
                time.sleep(3)
                self.get_element_by_xpath("//div[@class='tlss']").click()
            except:
                print("没有更多选项可以点击")
            news = self.browser.find_elements_by_xpath("//ul[@class='nero']/li")
            for new in news:
                content = new.find_elements_by_xpath(".//p")[0]
                news_date = new.find_elements_by_xpath("//ul[@class='nero']/li/p/font[@color='#999']")[0] \
                    .text.replace("年", "-").replace("月", "-").replace("日", "").split("-")
                news_date = [i for i in map(lambda x: int(x), news_date)]
                nDate = datetime.date(news_date[0], news_date[1], news_date[2])
                if keyword in content.text:
                    print("-----", content.text,
                          "--------" + new.find_elements_by_xpath(".//p/a")[0].get_attribute("href"))
                    item = CrawlJysItem()
                    item['date'] = str(nDate)
                    item['source'] = self.name
                    item['keyword'] = keyword
                    item['content'] = content.text + "..."
                    item['url'] = new.find_elements_by_xpath(".//p/a")[0].get_attribute("href")
                    self.items.append(item)
            try: #下一页
                self.get_element_by_xpath("//li[@class='js-page-next js-page-action ui-pager']").click()
            except Exception as e:
                print(e)
                break



