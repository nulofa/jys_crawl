
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ZgFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'zg_fgw'
    start_urls = ['https://www.ndrc.gov.cn/']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 5

    def parse(self, response):
        input_xpath = '//*[@id="qt"]'
        search_xpath = '//*[@id="search"]'
        items = super(ZgFgwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//*[@id='results']/div[@class='news clearfix']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//*[@id='results']/div[@class='news clearfix']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//*[@id='results']/div[@class='news clearfix']"
        date_xp = "./div[@class='content']/div[2]"
        content_xp = "./div[@class='content']/div[@class='txt']"
        title_xp = "./div[@class='title']/a"
        url_xp = "./div[@class='title']/a"
        next_xp = "//div[@class='pagination']/a[@class='next']"
        super(ZgFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        try:
            self.waitor('//*[@id="loading"]')
        except:
            pass
        self.waitor2('//*[@id="loading"]')
        time_xp = '//*[@id="timesSpanId"]' # 点击 时间选择器
        self.browser.find_element_by_xpath(time_xp).click()
        try:
            self.waitor('//*[@id="times"]')
        except:
            self.browser.find_element_by_xpath(time_xp).click()

        # 点击设置 开始时间
        self.get_element_by_xpath('//*[@id="utimeqsrq"]').click()
        self.waitor('//*[@id="layui-laydate5"]')  # 等待日历出现
        pre_month = self.browser.find_elements_by_xpath("//div[@id='layui-laydate5']//div[@class='layui-laydate-header']/i")[1]
        pre_month.click()
        time.sleep(0.5)
        pre_month.click()
        time.sleep(0.5)
        # 确定开始日期
        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()
        time.sleep(1)

        # 设置结束日期
        # self.get_element_by_xpath('//*[@id="utimejsrq"]').click()
        # self.waitor('//*[@id="layui-laydate6"]')  # 等待日历出现
        # self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()

        # 确定时间范围
        time.sleep(random.random()) #等待日历消失
        time_xp2 = "//*[@id='times']/li/input[@type='button']"
        self.get_element_by_xpath(time_xp2).click()
        self.waitor2('//*[@id="loading"]')

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(1+random.random())
                next.click()
                self.cur_page += 1
                self.waitor2('//*[@id="loading"]')
            else:
                self.cur_page = 1
                return False
        except Exception as e:
            print("点击下一页发生错误: \n", e)
            self.cur_page = 1
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '中国发改委'

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("\n")[0]
        return date_text.split("-")[1:]

