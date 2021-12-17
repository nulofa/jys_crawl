import datetime
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from selenium.webdriver.common.keys import Keys


class ZgGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'zg_gzw'
    start_urls = ['http://www.sasac.gov.cn/']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 5

    def parse(self, response):
        input_xpath = '//*[@id="thekey"]'
        search_xpath = '//*[@id="search_form"]/a'
        items = super(ZgGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = '//*[@id="info"]/ul/li'  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = '//*[@id="info"]/ul/li'  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="info"]/ul/li'
        date_xp = "./p[@class='zsy_scdate']"
        content_xp = "./p[@class='zsy_scdescribe']"
        title_xp = ".//p[@class='zsy_schead']/a"
        url_xp = ".//p[@class='zsy_schead']/a"
        next_xp = '//*[@id="page"]/a[last()]'
        super(ZgGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        try:
            self.waitor('//*[@id="info"]/ul/li',5)
        except:
            return
        self.browser.find_element_by_xpath('//*[@id="timeTextL"]').click()
        try:
            self.waitor("//li[@class='zdyDate']",3)
        except:
            self.browser.find_element_by_xpath('//*[@id="timeTextL"]').click()
            self.waitor("//li[@class='zdyDate']", 3)

        from_date = datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)
        todaty = datetime.date.today()
        self.browser.find_element_by_xpath('//*[@id="lowerLimit"]').send_keys(str(from_date))
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="upperLimit"]').send_keys(str(todaty))
        self.browser.find_element_by_xpath('//*[@id="upperLimit"]').send_keys(Keys.ENTER)
        time.sleep(1)
        self.browser.find_element_by_xpath("//li[@class='zdyDate']//input[@value='确定']").click()


    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(2+random.random())
                next.click()
                self.cur_page += 1
                time.sleep(2+random.random())
            else:
                self.cur_page = 1
                return False
        except Exception as e:
            print("点击下一页发生错误\n", e)
            self.cur_page = 1
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[1]
        return date_text.split("-")

