import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class ShJrjSpider(scrapy.Spider, BaseCrawl):
    name = 'sh_jrj'
    start_urls = ['https://www.shanghai.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.part = 1
        BaseCrawl.timeout = 10

    def parse(self, response):
        input_xpath = "//input[@id='search-input']"
        search_xpath = "//button[@id='searchBtn']"
        items = super(ShJrjSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='result result-elm']"  # 等待第一页搜索结果的出现
        wait3_xp = "//div[@class='result result-elm']"  # 等待每一页的搜索结果的出现
        news_xp = ["//div[@class='result result-elm']", "//div[@class='result result-elm ']"]
        date_xp = ".//font[@color='#9a9a9a']"
        content_xp = ".//div[@class='content']"
        title_xp = "./a"
        url_xp = "./a"
        next_xp = ""
        super(ShJrjSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)
        self.part += 1
        super(ShJrjSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        time.sleep(2)

        if self.part == 1:
            # 选择单位：金融局
            try:
                self.waitor2("//div[@id='layui-layer-shade1']")
            except:
                pass
            self.waitor("//div[@id='results']")
            time.sleep(1)
            try:
                self.browser.find_elements_by_xpath('//*[@id="siteLocate"]')[0].click()
                self.waitor("//div[@class='modal-content']")
            except:
                self.browser.find_elements_by_xpath('//*[@id="siteLocate"]')[0].click()
                self.waitor("//div[@class='modal-content']")

            self.get_element_by_xpath("//a[@data-code='jrj.sh.gov.cn']").click()
            time.sleep(1)
            # 在《要闻动态》下搜索
            self.get_element_by_xpath("//li[@data-channel='xwzx']", "//div[@id='layui-layer-shade2']").click()
        else:
            # 在《政务公开》下搜索
            try:
                self.get_element_by_xpath("//li[@data-channel='xxgk']", "//div[@id='layui-layer-shade2']").click()
            except:
                time.sleep(3)
                self.get_element_by_xpath("//li[@data-channel='xxgk']", "//div[@id='layui-layer-shade2']").click()
            self.part = 1

        time.sleep(2)
        # 时间范围选择一年内
        try:
            self.get_element_by_xpath("//a[@id='drop6']", "//div[@id='layui-layer-shade2']",
                                  "//div[@id='layui-layer-shade5']",
                                  "//div[@id='layui-layer-shade3']").click()
        except:
            time.sleep(2+random.random())
            self.get_element_by_xpath("//a[@id='drop6']", "//div[@id='layui-layer-shade2']",
                                      "//div[@id='layui-layer-shade5']",
                                      "//div[@id='layui-layer-shade3']").click()

        self.get_element_by_xpath("//a[@data-filter-value='3']", "//div[@id='layui-layer-shade5']").click()

        for i in range(5):
            try:
                time.sleep(1)
                self.browser.find_element_by_xpath("//div[@id='searchMoreDiv']/a").click()
            except Exception as e:
                print(e)
                break
            time.sleep(self.get_sleeptime())
        time.sleep(self.get_sleeptime() + 1)

    def click_next(self, next_xp):
        return False

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = self.get_real_url(new.find_element_by_xpath(url_xp).get_attribute("href"))

        item['source'] = '上海金融局'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

