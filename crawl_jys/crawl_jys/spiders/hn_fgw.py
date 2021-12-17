import datetime
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class HnFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'hn_fgw'
    start_urls = ['http://plan.hainan.gov.cn/sfgw/index.shtml']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="keywords"]'
        search_xpath = '//*[@id="dataform"]/div[1]'
        items = super(HnFgwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='wordGuide Residence-permit']//p[@class='summaryFont']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='wordGuide Residence-permit']//p[@class='summaryFont']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='wordGuide Residence-permit']"
        date_xp = ".//span[@class='sourceDateFont']"
        content_xp = ".//p[@class='summaryFont']"
        title_xp = './/a[@class="fl titleFont permitT titleSelf"]'
        url_xp = './/a[@class="fl titleFont permitT titleSelf"]'
        next_xp = '//*[@id="pageInfo"]/li[last()]/a'
        super(HnFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        self.waitor('//*[@id="selectRange"]')

        wait1_xp = '//*[@id="time"]/i'  # 等待《时间选择器》的出现
        time_xp = '//*[@id="time"]/i'  # 点击 时间选择器

        self.waitor(wait1_xp)
        self.get_element_by_xpath(time_xp).click()
        try:
            self.waitor("//ul[@id='timeRange_downSelect']")
        except:
            self.get_element_by_xpath(time_xp).click()
            time.sleep(1)
        self.get_element_by_xpath("//ul[@id='timeRange_downSelect']//li[@data='1']").click()


        # 选择全文匹配
        self.get_element_by_xpath("//div[@class='downMenu wh135 fl rang']/i").click()
        try:
            self.waitor('//*[@id="selectRange_downSelect"]')
        except:
            self.get_element_by_xpath("//div[@class='downMenu wh135 fl rang']/i").click()

        self.get_element_by_xpath('//*[@id="selectRange_downSelect"]/li[1]').click()



    def click_next(self, next_xp):
        pre_of_next = self.get_element_by_xpath('//*[@id="pageInfo"]/li[last()-1]/a').text
        cur_page = self.get_element_by_xpath('//*[@id="pageInfo"]/li[@class="page active"]/a').text
        flg = pre_of_next != cur_page
        self.get_element_by_xpath(next_xp).click()
        return flg

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        res = new.find_elements_by_xpath(date_xp)
        res2 = new.find_elements_by_xpath(".//table")
        #有表格或无日期，不要
        if len(res2) > 0 or len(res) == 0:
            date_text = '1970-1-1'
        else:
            date_text = res[0].text
        return date_text.split("-")

