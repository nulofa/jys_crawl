
import random
import time
import scrapy
from selenium.webdriver import ActionChains

from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class JsJrjSpider(scrapy.Spider, BaseCrawl):
    name = 'js_jrj'
    start_urls = ['http://jsjrb.jiangsu.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 3

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = '//*[@id="q"]'
        search_xpath = "//form[@id='SearchForm']/input[@type='submit']"
        items = super(JsJrjSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = '//*[@id="jsearch-result-items"]/div'  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = '//*[@id="jsearch-result-items"]/div'  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="jsearch-result-items"]/div'
        date_xp = ".//div[@class='jsearch-result-other-info']/span"
        content_xp = ".//div[@class='jsearch-result-abs-content']"
        title_xp = ".//div[@class='jsearch-result-title']/a"
        url_xp = ".//div[@class='jsearch-result-title']/a"
        next_xp = '//*[@id="pagination"]/a[last()]'
        super(JsJrjSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="date_start"]'  # 等待《时间选择器》的出现
        time_xp = wait1_xp  # 点击 时间选择器
        time_xp2 = "//div[@class='jsearch-condition-box-items']/div[@data-value='3']"  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        try:
            ActionChains(self.browser).move_to_element(self.get_element_by_xpath(time_xp)).perform()
            self.waitor(time_xp2)
        except:
            time.sleep(2 + random.random())
            ActionChains(self.browser).move_to_element(self.get_element_by_xpath(time_xp)).perform()
            self.waitor(time_xp2)
        ActionChains(self.browser).click(self.get_element_by_xpath(time_xp2)).perform()
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
        item['source'] = '江苏金融局'  # 需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.replace("年","-").replace("月","-").replace("日","").split("-")

