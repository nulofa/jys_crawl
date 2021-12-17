import datetime
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ZgCzbSpider(scrapy.Spider, BaseCrawl):
    name = 'zg_czb'
    start_urls = ['http://www.mof.gov.cn/index.htm']
    cur_page = 1
    max_page = 5

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="andsen"]'
        search_xpath = "//img[@src='/images/czb_searicon_1.png']"
        items = super(ZgCzbSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='list_search']/dl"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='list_search']/dl"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='list_search']/dl"
        date_xp = ".//span[@class='fr']"
        content_xp = "./dd"
        title_xp = "./dt/a"
        url_xp = "./dt/a"
        next_xp = "//p[@class='pagerji']/a[@class='next-page']"
        super(ZgCzbSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):

        #选择 搜索正文
        self.waitor("//div[@class='select_box']/span")
        self.browser.find_element_by_xpath("//div[@class='label-g']//input[@value='正文']").click()
        time.sleep(1 + random.random())
        self.browser.find_element_by_xpath("//div[@class='anniu']//img").click()

        # 选择 按时间排序
        self.waitor("//div[@class='select_box']/span")
        time.sleep(random.random())
        self.browser.find_element_by_xpath("//div[@class='paixubox']//a[@onclick=\"setOrderBy('-DOCRELTIME');\"]").click()

        return # 不能选具体时间，一选就被拦截
        wait1_xp = "//div[@class='select_box']/span"  # 等待《时间选择器》的出现
        time_xp = "//div[@class='select_box']/span" # 点击 时间选择器



        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(1+random.random())
        time_xp2 = "//div[@class='select_box']//li[@onclick=\"setTimeScope('year');\"]"  # 选择一年内
        self.get_element_by_xpath(time_xp2).click()

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            time.sleep(2+random.random())
            if ZgCzbSpider.cur_page < ZgCzbSpider.max_page:
                next.click()
                ZgCzbSpider.cur_page+=1
            else:
                ZgCzbSpider.cur_page=1
                return False

        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split(".")

