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
from selenium.webdriver import FirefoxProfile, DesiredCapabilities,Firefox
from crawl_jys.items import CrawlJysItem

class AhJrjSpider(scrapy.Spider):
    name = 'ah_jrj'
    start_urls = ['http://www.ah.gov.cn']

    keywords = ["知识产权", "农村产权", "要素交易场所", "产权交易所", "股权交易中心", "文化产权", "碳排放权", "交易市场建设"]
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
        input_xpath = "//input[@id='searchInput']"
        search_xpath = "//input[@name='input']"
        self.default_handle = self.browser.current_window_handle
        total_items = []
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

            # 选择 金融局
            self.get_element_by_xpath("//div[@class='module selected-container']").click()
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                    "//ul[@id='filllist']//a[@title='省地方金融监管局']")))
            self.get_element_by_xpath("//ul[@id='filllist']//a[@title='省地方金融监管局']").click()
            WebDriverWait(self.browser, 10).until(EC.invisibility_of_element((By.XPATH, "//ul[@id='filllist']")))


            self.get_data(keyword)

            self.browser.close()
            self.browser.switch_to.window(self.default_handle)

        self.browser.close()
        for item in self.items:
            yield item

    def get_data(self, keyword):
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "//label[@id='dropdownMenu1']")))
        self.browser.find_elements_by_xpath("//label[@id='dropdownMenu1']")[-1].click()
        time.sleep(1)
        self.get_element_by_xpath("//li[@role='presentation']/a[@tr=4]").click()
        time.sleep(1)
        thred = datetime.date.today() - datetime.timedelta(AhJrjSpider.date_limit)

        try:
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='result']")))
        except Exception as e:
            print(e)
            print("没有搜索结果")
            return
        #
        has_next = True

        while (has_next):
            WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='result']//div[@class='content']/p")))
            news = self.browser.find_elements_by_xpath("//div[@class='result']")
            for new in news:
                news_date = new.find_element_by_xpath(".//div[@class='explain']/span").text.split("-")
                news_date = [i for i in map(lambda x: int(x), news_date)]
                nDate = datetime.date(news_date[0], news_date[1], news_date[2])
                if nDate >= thred:
                    content = new.find_element_by_xpath(".//div[@class='content']/p")
                    if keyword in content.text:
                        print("-----", content.text,
                              "--------" + new.find_element_by_xpath("./div[@class='title']/a").get_attribute("href"))
                        item = CrawlJysItem()
                        item['date'] = str(nDate)
                        item['source'] = self.name
                        item['keyword'] = keyword
                        item['content'] = content.text + "..."
                        old_url = new.find_element_by_xpath("./div[@class='title']/a").get_attribute("href")
                        item['url'] = self.get_real_url(old_url)
                        self.items.append(item)
            try:
                next = self.get_element_by_xpath("//a[@title='下一页']")
                next.click()
            except:
                has_next = False

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

