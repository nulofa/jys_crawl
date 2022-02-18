
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class XjGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'xj_gzw'
    start_urls = ['http://www.xinjiang.gov.cn/xinjiang/ywdt/xw.shtml']
    # custom_settings = {
    #     'HEADLESS': False,
    #     'IMAGELESS': True
    # }

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 2

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = "//form[@name='searchForm']/input"
        search_xpath = "//form[@name='searchForm']/div[@onclick='checkForm();']"
        items = super(XjGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = '//*[@id="searchResult"]/div'  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = '//*[@id="searchResult"]/div'  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="searchResult"]/div'
        date_xp = ".//p[@class='time']/span"
        content_xp = ".//p[@class='summaryFont']"
        title_xp = "./div[@class='bigTit clearfix']/a"
        url_xp = "./div[@class='bigTit clearfix']/a"
        next_xp = '//*[@id="pageInfo"]/li[last()]/a'
        super(XjGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):

        wait1_xp = '//*[@id="time"]'  # 等待《时间选择器》的出现
        time_xp = '//*[@id="time"]/i'  # 点击 时间选择器
        time_xp2 = '//*[@id="timeRange_downSelect"]/li[3]'  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        try:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        except:
            time.sleep(2)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(1)

        # select section
        self.get_element_by_xpath('//*[@id="showSonSites2"]').click()
        time.sleep(1)
        section = '//*[@id="sonSites1"]//li[24]'
        try:
            self.waitor(section)
            self.get_element_by_xpath(section).click()
        except:
            self.get_element_by_xpath('//*[@id="showSonSites2"]').click()
            time.sleep(2)
            self.waitor(section)
            self.get_element_by_xpath(section).click()
        time.sleep(2)

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                next.click()
                time.sleep(1 + random.random())
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
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '新疆国资委'  # 需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp):  # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

