import datetime
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ScFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'sc_fgw'
    start_urls = ['http://fgw.sc.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="searchWord"]'
        search_xpath = "//input[@type='submit']"
        items = super(ScFgwSpider, self).myParse(response, input_xpath, search_xpath)
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
        super(ScFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="time"]'  # 等待《时间选择器》的出现
        time_xp = '//*[@id="time"]//i'  # 点击 时间选择器
        time_xp2 = "//a[@onclick='customTime()']"  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        self.get_element_by_xpath(time_xp).click()
        self.waitor("//ul[@id='timeRange_downSelect']")

        self.get_element_by_xpath('//*[@id="startDate"]').send_keys(
            str(datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)))
        self.get_element_by_xpath('//*[@id="endDate"]').send_keys(str(datetime.date.today()))
        time.sleep(1)

        self.get_element_by_xpath(time_xp2).click()  # 点击确定
        time.sleep(1)

    def click_next(self, next_xp):
        pre_of_next = self.get_element_by_xpath('//*[@id="pageInfo"]/li[last()-1]/a').text
        cur_page = self.get_element_by_xpath('//*[@id="pageInfo"]/li[@class="page active"]/a').text
        flg = pre_of_next != cur_page
        self.get_element_by_xpath(next_xp).click()
        return flg

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        try:
            date_text = new.find_elements_by_xpath(date_xp)[0].text
        except:  # 不是新闻，没有日期
            date_text = '1970-1-1'
        return date_text.split("-")

