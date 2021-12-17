import datetime
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ZjJrjSpider(scrapy.Spider, BaseCrawl):
    name = 'zj_jrj'
    start_urls = ['http://sjrb.zj.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//input[@id='q']"
        search_xpath = "//input[@id='tjiao']"
        items = super(ZjJrjSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='jcse-result-box news-result']"  # 等待第一页搜索结果的出现
        wait3_xp = "//div[@class='jcse-result-box news-result']"  # 等待每一页的搜索结果的出现
        news_xp = "//div[@class='jcse-result-box news-result']"
        date_xp = ".//div[@class='website-source']/span[@class='jcse-news-date jcse-news-date1']"
        content_xp = "./div[@class='jcse-news-abs']"
        title_xp = "./div[@class='jcse-news-title']/a"
        url_xp = "./div[@class='jcse-news-title']/a"
        next_xp = "//div[@id='pagination']//li[last()-2]"
        super(ZjJrjSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        self.get_element_by_xpath("//div[@class='TimeType lf']/p[@class='textWrap']").click()
        self.waitor("//div[@class='TimeTypeList']")

        from_date = datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)
        self.browser.find_element_by_xpath("//input[@class='utimeqsrq']").send_keys(str(from_date))
        time.sleep(1)
        self.browser.find_element_by_xpath("//input[@class='utimejsrq']").send_keys(str(datetime.date.today()))
        self.get_element_by_xpath("//input[@id='datebtu']").click()

        time.sleep(2)

    def click_next(self, next_xp):
        total_page = self.browser.find_elements_by_xpath("//div[@id='pagination']//li[@class='totalPage']")[1].text[
                     1:-1]
        cur_page = self.browser.find_element_by_xpath("//div[@id='pagination']//li[@class='active']").text
        if int(cur_page) < int(total_page):
            self.get_element_by_xpath(next_xp).click()
            return True
        else:
            return False

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("：")[1].strip().split("-")

