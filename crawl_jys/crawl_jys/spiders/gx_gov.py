
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class GxGovSpider(scrapy.Spider, BaseCrawl):
    name = 'gx_gov'
    start_urls = ['http://www.gxzf.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//div[@class='site-search fn-right']//input[@name='searchWord']"
        search_xpath = "//div[@class='site-search fn-right']//input[@class='search-submit']"
        items = super(GxGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//ul//div[@class='newsDiv clear_fix']"  # 等待第一页搜索结果的出现
        wait3_xp = "//ul//div[@class='newsDiv clear_fix']"  # 等待每一页的搜索结果的出现
        news_xp = "//ul//div[@class='newsDiv clear_fix']"
        date_xp = ".//span[last()]"
        content_xp = "./div[@class='news_main']"
        title_xp = "./div[@class='news_title']/a"
        url_xp = "./div[@class='news_title']/a"
        next_xp = "//button[@class='btn-next']"
        super(GxGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = "//div[@class='totolLi']"  # 等待结果出现
        time_xp = "//div[@class='el-date-editor el-range-editor el-input__inner el-date-editor--daterange el-range-editor--mini']" # 点击 时间选择器
        time_xp2 = "//div[@class='el-picker-panel__body-wrapper']/div/button[last()]"  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(1)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(1)
        # 点击按全文搜索
        self.browser.find_element_by_xpath("//li[@class='filterLi'][last()]/div/span[last()]").click()

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            next.click()
        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '广西政府网'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

