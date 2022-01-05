
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class HnKjtSpider(scrapy.Spider, BaseCrawl):
    name = 'hn_kjt'
    start_urls = ['http://dost.hainan.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="keywords"]'
        search_xpath = '//*[@id="pageform"]/img'
        items = super(HnKjtSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = ""  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = ""  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = ["//div[@class='clearfix Residence-permit ']", "//div[@class='clearfix Residence-permit']"]
        date_xp = "./span[@class='quily-con']"
        content_xp = "./p"
        title_xp = ".//h3/a"
        url_xp = ".//h3/a"
        next_xp = '//*[@id="pageInfo"]/li[last()-1]/a'
        super(HnKjtSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="relatedResult"]'  # 等待搜索结果
        time_xp = '//*[@id="searchAllarticle"]'  # 点击全文匹配
        time_xp2 = '//*[@id="year"]'  # 时间选择 一年内
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        self.waitor(wait1_xp)
        self.get_element_by_xpath(time_xp2).click()

    def click_next(self, next_xp):
        pre_of_next = self.get_element_by_xpath('//*[@id="pageInfo"]/li[last()-1]/a').text
        cur_page = self.get_element_by_xpath('//*[@id="pageInfo"]/li[@class="page active"]/a').text
        flg = pre_of_next != cur_page
        self.get_element_by_xpath(next_xp).click()

        wait1_xp = '//*[@id="relatedResult"]'  # 等待搜索结果
        time_xp2 = '//*[@id="year"]'  # 时间选择 一年内
        self.waitor(wait1_xp)
        self.get_element_by_xpath(time_xp2).click()
        return flg

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '海南科技厅'

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        res = new.find_elements_by_xpath(date_xp)
        res2 = new.find_elements_by_xpath(".//table")
        # 有表格或无日期，不要
        if len(res2) > 0 or len(res) == 0:
            date_text = '1970-1-1'
        else:
            date_text = res[0].text
        return date_text.split("-")
