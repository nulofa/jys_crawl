
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ShZqbSpider(scrapy.Spider, BaseCrawl):
    name = 'sh_zqb'
    start_urls = ['https://www.cnstock.com']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 5

    def parse(self, response):
        input_xpath = '//*[@id="nav_keywords"]'
        search_xpath = "//form[@name='navsearch_form']//input[@type='submit']"
        items = super(ShZqbSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        time.sleep(7+random.random())
        wait2_xp = "//div[@class='result-article']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='result-article']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='result-article']"
        date_xp = "./p/span"
        content_xp = "./p[@class='des']"
        title_xp = "./h3/a"
        url_xp = "./h3/a"
        next_xp = "//div[@class='pagination pagination-centered']//li[last()]"
        super(ShZqbSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        pass

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(1+random.random())
                next.click()
                self.cur_page += 1
            else:
                self.cur_page = 1
                return False
        except Exception as e:
            print("点击下一页发生错误: \n", e)
            self.cur_page = 1
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[1]
        return date_text.split("-")

