
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class HbGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'hb_gzw'
    start_urls = ['https://www.hubei.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 3

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = '//*[@id="hbgov-search-word"]'
        search_xpath = '//*[@id="hbgov-search-btn"]'
        items = super(HbGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='allContent newsContent fileContent interpretationContent serviceContent publicContent clear_fix']/ul/li"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='allContent newsContent fileContent interpretationContent serviceContent publicContent clear_fix']/ul/li"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='allContent newsContent fileContent interpretationContent serviceContent publicContent clear_fix']/ul/li/div[@class='newsDiv clear_fix']"
        date_xp = ".//p[@class='fr']"
        content_xp = "./div[@class='news_main']/p"
        title_xp = "./div[@class='news_title']/a"
        url_xp = "./div[@class='news_title']/a"
        next_xp = "//button[last()]/i"
        super(HbGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        # 选择部门
        try:
            self.waitor("//div[@class='totalLi']/span/span[last()]")
            self.get_element_by_xpath("//div[@class='siteCheckDiv']").click()
            self.waitor("//div[@class='siteId_children department_site']")
            self.get_element_by_xpath("//div[@class='siteId_children department_site']//li[27]").click() # 选择部门
            self.get_element_by_xpath("//div[@class='siteIdCheckList']//div[@class='btns fr']/button[1]").click()
        except:
            if len(self.browser.find_elements_by_xpath(
                    "//div[@class='siteIdCheckList']//div[@class='btns fr']/button[2]")) > 0:
                self.get_element_by_xpath("//div[@class='siteIdCheckList']//div[@class='btns fr']/button[2]").click()
            self.waitor("//div[@class='totalLi']/span/span[last()]")
            self.get_element_by_xpath("//div[@class='siteCheckDiv']").click()
            self.waitor("//div[@class='siteId_children department_site']")
            self.get_element_by_xpath("//div[@class='siteId_children department_site']//li[27]").click()
            self.get_element_by_xpath("//div[@class='siteIdCheckList']//div[@class='btns fr']/button[1]").click()

        handls = list(self.browser.window_handles)
        new_handl = handls[-1]
        self.browser.close()
        self.browser.switch_to.window(new_handl)

        wait1_xp = "//li[@class='timeFilter filterLi']"  # 等待《时间选择器》的出现
        time_xp = "//li[@class='timeFilter filterLi']//input[1]"  # 点击 时间选择器
        time_xp2 = "//div[@class='el-picker-panel__sidebar']/button[2]"  # 时间选择需要 两次点击才能确定
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
                time.sleep(1 + random.random())
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
        item['source'] = '湖北国资委'  # 需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp):  # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")
