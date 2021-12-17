import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ZgGwySpider(scrapy.Spider, BaseCrawl):
    name = 'zg_gwy'
    start_urls = ['http://sousuo.gov.cn/s.htm?t=govall&q=']
    cur_page = 1
    max_page = 5

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="q"]'
        search_xpath = '//*[@id="su"]'
        items = super(ZgGwySpider, self).myParse(response, input_xpath, search_xpath,"//span[@class='total']")
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='result']//li[@class='res-list']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='result']//li[@class='res-list']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='result']//li[@class='res-list']"
        date_xp = ".//p[@class='res-other']"
        content_xp = ".//p[@class='res-sub']"
        title_xp = "//div[@class='result']//li[@class='res-list']/h3/a"
        url_xp = "//div[@class='result']//li[@class='res-list']/h3/a"
        next_xp = '//*[@id="snext"][1]'
        super(ZgGwySpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = "//ul[@class='sort-list']//a[@type='timeyn']"  # 等待《时间选择器》的出现
        time_xp = "//ul[@class='sort-list']//a[@type='timeyn']" # 点击 时间选择器
        self.waitor(wait1_xp)
        time.sleep(1)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()


    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if ZgGwySpider.cur_page < ZgGwySpider.max_page:
                next.click()
                ZgGwySpider.cur_page += 1
                time.sleep(1+random.random())
            else:
                ZgGwySpider.cur_page = 1
                return False
        except:
            has_next = False
            ZgGwySpider.cur_page = 1
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        if len(new.find_elements_by_xpath(date_xp)) == 0:
            return [1970,1,1]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("：")[1]
        return date_text.split(".")

