# -*- coding: utf-8 -*-
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl


class AhKjtSpider(scrapy.Spider, BaseCrawl):
    name = 'ah_kjt'
    start_urls = ['http://www.ah.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//input[@id='searchInput']"
        search_xpath = "//input[@name='input']"
        items = super(AhKjtSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='result']"  # 等待第一页搜索结果的出现
        wait3_xp = "//div[@class='result']//div[@class='content']/p"  # 等待每一页的搜索结果的出现
        news_xp = "//div[@class='result']"
        date_xp = ".//div[@class='explain']/span"
        content_xp = ".//div[@class='content']/p"
        title_xp = "./div[@class='title']/a"
        url_xp = "./div[@class='title']/a"
        next_xp = "//a[@title='下一页']"
        super(AhKjtSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        domain_xp = "//div[@class='module selected-container']"
        wait_xp = "//ul[@id='filllist']//a[@title='省科技厅']"
        wait_xp2 = "//ul[@id='filllist']"
        # 选择 科技厅
        self.get_element_by_xpath(domain_xp).click()
        self.waitor(wait_xp)
        self.get_element_by_xpath(wait_xp).click()
        self.waitor2(wait_xp2)

        wait1_xp = "//label[@id='dropdownMenu1']"  # 等待《时间选择器》的出现
        time_xp = "//label[@id='dropdownMenu1']"  # 点击 时间选择器
        time_xp2 = "//li[@role='presentation']/a[@tr=4]"  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(2)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(1)

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            next.click()
        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = self.get_real_url(new.find_element_by_xpath(url_xp).get_attribute("href"))

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")