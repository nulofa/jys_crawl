import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class CqGovSpider(scrapy.Spider, BaseCrawl):
    name = 'cq_gov'
    start_urls = ['http://www.cq.gov.cn']
    max_page = 3
    cur_page = 1

    custom_settings = {
        'HEADLESS': True,
        'IMAGELESS': True
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="searchWord"]'
        search_xpath = '//*[@id="toSearch"]'
        items = super(CqGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp ='//*[@id="news_list"]/div[@class="item is-news"]' # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = wait2_xp  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="news_list"]/div[@class="item is-news"]'
        date_xp = ".//span[@class='time']"
        content_xp = './/p[@class="zw"]'
        title_xp = './/div[@class="title"]/a'
        url_xp = './/div[@class="title"]/a'
        next_xp = '//*[@id="layui-laypage-1"]/a[last()]'
        super(CqGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        self.waitor("//div[@class='search_result f14']/span[@class='countNum']")
        self.browser.find_element_by_xpath('//*[@id="location"]/a[@data-value="all"]').click()

        self.waitor("//div[@class='search_result f14']/span[@class='countNum']")
        time_xp = '//*[@id="sorting"]/a[@data-value="time"]' # 点击 按时间排序
        self.browser.find_elements_by_xpath(time_xp)[-1].click()




    def click_next(self, next_xp):
        if CqGovSpider.cur_page < CqGovSpider.max_page:
            self.browser.find_element_by_xpath(next_xp).click()
            CqGovSpider.cur_page += 1
            time.sleep(2+random.random())
            return True
        CqGovSpider.cur_page = 1
        return False

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '重庆政府网'

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

