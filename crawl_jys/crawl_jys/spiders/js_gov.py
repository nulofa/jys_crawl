
import random
import time
import scrapy
from selenium.webdriver.common.action_chains import ActionChains
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class JsGovSpider(scrapy.Spider, BaseCrawl):
    name = 'js_gov'
    start_urls = ['http://www.jiangsu.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 3

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):

        input_xpath = '//*[@id="t1"]'
        search_xpath = '//*[@id="Formdh03"]/div'
        items = super(JsGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='jcse-result-box news-result']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='jcse-result-box news-result']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='jcse-result-box news-result']"
        date_xp = ".//span[@class='jcse-news-date']"
        content_xp = ".//div[@class='jcse-news-abs-content']"
        title_xp = ".//div[@class='jcse-news-title']/a"
        url_xp = ".//div[@class='jcse-news-title']/a"
        next_xp = '//*[@id="pagination"]/a[last()]'
        super(JsGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="date_start"]'  # 等待《时间选择器》的出现
        time_xp = wait1_xp # 点击 时间选择器
        time_xp2 = '//*[@id="time_list"]/div[4]'  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        try:
            ActionChains(self.browser).move_to_element(self.get_element_by_xpath(time_xp)).perform()
            self.waitor(time_xp2)
        except:
            time.sleep(2)
            ActionChains(self.browser).move_to_element(self.get_element_by_xpath(time_xp)).perform()
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
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = self.get_real_url(new.find_element_by_xpath(url_xp).get_attribute("href"))
        item['source'] = '江苏政府网'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[1]
        return date_text.split("-")

