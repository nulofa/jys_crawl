
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class HnGovSpider(scrapy.Spider, BaseCrawl):
    name = 'hn_gov'
    start_urls = ['https://www.hainan.gov.cn/s?siteCode=4600000001&searchWord=%25E5%2586%259C%25E6%259D%2591%25E4%25BA%25A7%25E6%259D%2583&column=2675&wordPlace=0&orderBy=1&pageSize=10&pageNum=0&timeStamp=1&labelHN=&uc=0&checkHandle=1&strFileType=0&countKey=%200&sonSiteCode=&areaSearchFlag=-1&secondSearchWords=&left_right_flag=1']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="allSearchWord"]'
        search_xpath = "//input[@class='fl search_icon']"
        items = super(HnGovSpider, self).myParse(response, input_xpath, search_xpath, "//p[@class='fl']")
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = ""  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = ""  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = ["//div[@class='clearfix Residence-permit ']", "//div[@class='clearfix Residence-permit']"]
        date_xp = "./span[@class='quily-con']"
        content_xp = "./p"
        title_xp = "./div/h3/a"
        url_xp = title_xp
        next_xp = '//*[@id="pageInfo"]/li[last()]/a'
        super(HnGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        pass

    def click_next(self, next_xp):
        pre_of_next = self.get_element_by_xpath('//*[@id="pageInfo"]/li[last()-1]/a').text
        cur_page = self.get_element_by_xpath('//*[@id="pageInfo"]/li[@class="page active"]/a').text
        flg = pre_of_next != cur_page
        self.get_element_by_xpath(next_xp).click()
        return flg

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '海南政府网'

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        res = new.find_elements_by_xpath(date_xp)
        date_text = res[0].text
        return date_text.split("-")

