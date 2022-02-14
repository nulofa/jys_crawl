
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class HunanGovSpider(scrapy.Spider, BaseCrawl):
    name = 'hunan_gov'
    start_urls = ['http://www.hunan.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 3

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = '//*[@id="inputid"]'
        search_xpath = '//*[@id="submitid"]'
        items = super(HunanGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = '//*[@id="hits"]/li'  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = '//*[@id="hits"]/li'  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="hits"]/li'
        date_xp = './/span[@class="source-time"]'
        content_xp = './div[@class="right"]/span'
        title_xp = './div[@class="com-title"]//a'
        url_xp = title_xp
        next_xp = '//*[@id="listPage"]/a[last()-1]'
        super(HunanGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = "//select[@name='timeSelect']"  # 等待《时间选择器》的出现
        time_xp = "//select[@name='timeSelect']" # 点击 时间选择器
        time_xp2 = "//select[@name='timeSelect']/option[@value='timeyy']"  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        try:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        except:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(1)

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(1+random.random())
                next.click()
                self.cur_page += 1
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
        item['source'] = '湖南政府网'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("：")[1]
        return date_text.split("-")

