import datetime
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from selenium.webdriver.common.keys import Keys


class JxGovSpider(scrapy.Spider, BaseCrawl):
    name = 'jx_gov'
    start_urls = ['http://jiangxi.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//input[@id='q']"
        search_xpath = "//input[@class='form_sub']"
        items = super(JxGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='jcse-result-box news-result']"  # 等待第一页搜索结果的出现, 不知道设置什么就和news_xp一样
        wait3_xp = "//div[@class='jcse-result-box news-result']"  # 等待每一页的搜索结果的出现，不知道设置什么就和news_xp一样
        news_xp = "//div[@class='jcse-result-box news-result']"
        date_xp = ".//span[@class='jcse-news-date']"
        content_xp = ".//div[@class='jcse-news-abs-content']"
        title_xp = ".//div[@class='jcse-news-title']/a"
        url_xp = ".//div[@class='jcse-news-url']/a"
        next_xp = ""
        super(JxGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        # 时间范围选择
        timeStart = self.get_element_by_xpath("//input[@id='date_start']")
        timeStart.click()
        thred = datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)
        timeStart.send_keys(str(thred))

        time.sleep(1)
        timeEnd = self.get_element_by_xpath("//input[@id='date_end']")
        # timeEnd.click()
        timeEnd.send_keys(str(datetime.date.today()))
        timeEnd.send_keys(Keys.ENTER)

        while (True):
            try:
                self.get_element_by_xpath("//div[@class='uploadmore']").click()
            except Exception as e:
                print(e)
                break

    def click_next(self, next_xp):
        return False

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).text
        item['source'] = '江西政府网'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

