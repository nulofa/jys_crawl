# -*- coding: utf-8 -*-

import scrapy
from crawl_jys.BaseClass import BaseCrawl


class AhFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'ah_fgw'
    start_urls = ['http://fzggw.ah.gov.cn']
    max_page = 3
    
    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//div[@class='search fl']//input[@class='search-keywords']"
        search_xpath = "//div[@class='search fl']//input[@name='input']"
        wait_xp = "//div[@class='searchlistw']/ul[@class='search-list']"
        items = super(AhFgwSpider, self).myParse(response, input_xpath,search_xpath,wait_xp)

        for item in items:
            print(item)

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='searchlistw']//li[@class='search-url']" # 等待第一页搜索结果的出现
        wait3_xp = "//div[@class='searchlistw']//li[@class='search-url']" # 等待每一页的搜索结果的出现
        news_xp = "//div[@class='searchlistw']/ul[@class='search-list']"
        date_xp = ".//span[@class='date']"
        content_xp = ".//li[@class='search-info']"
        title_xp = ".//li[@class='search-title']/a"
        url_xp = ".//li[@class='search-url']/a"
        next_xp = ".//div[@id='page_new']//a"
        super(AhFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp, title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = "//div[@class='reslut_type date_type']//a"  # 等待《时间选择器》的出现
        time_xp = "//div[@class='reslut_type date_type']//a"
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()


    def click_next(self, next_xp):
        has_next = True
        cur_page = self.browser.find_element_by_xpath("//div[@id='page_new']/span[@class='current']").text
        try:
            next = self.browser.find_elements_by_xpath(next_xp)[-2]
            if next.text == '下一页' and self.max_page > int(cur_page):
                next.click()
            else:
                has_next = False
        except Exception as e:
            print(e)
            has_next = False
        return has_next

    def process_item(self, new, item,title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '安徽发改委'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")


