
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class HenanGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'henan_gzw'
    start_urls = ['https://www.henan.gov.cn']
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
        input_xpath = '//*[@id="searchInput"]'
        search_xpath = '//*[@id="searchBtn"]'
        items = super(HenanGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = '//*[@id="new-list"]/li'  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = '//*[@id="new-list"]/li'  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = '//*[@id="new-list"]/li'
        date_xp = ".//span[@class='times']"
        content_xp = ".//div[@class='new-summary']"
        title_xp = "./a/h3"
        url_xp = "./a"
        next_xp = '//*[@id="layui-laypage-4"]/a[last()]'
        super(HenanGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                             title_xp, url_xp, next_xp)

    def time_select(self):
        # select department
        try:
            self.get_element_by_xpath("//div[@class='fl scopes']").click()
            self.waitor("//div[@class='high-search dis huntzone']")
            self.get_element_by_xpath("//div[@class='select-items'][23]").click()  # gzw
            time.sleep(random.random())
            self.get_element_by_xpath("//button[@class='fl hd-btn']").click()
        except:
            time.sleep(2)
            self.get_element_by_xpath("//div[@class='fl scopes']").click()
            self.waitor("//div[@class='high-search dis huntzone']")
            self.get_element_by_xpath("//div[@class='select-items'][1]").click()
            time.sleep(random.random())
            self.get_element_by_xpath("//button[@class='fl hd-btn']").click()

        wait1_xp = '//*[@id="test6"]'  # 等待《时间选择器》的出现
        time_xp = '//*[@id="test-startDate-1"]'  # 点击 时间选择器
        time_xp2 = '//*[@id="layui-laydate1"]/div[1]//i[@class="layui-icon laydate-icon laydate-prev-m"]'  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        try:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        except:
            time.sleep(2)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(random.random())
        self.get_element_by_xpath('//*[@id="layui-laydate1"]//span[@class="laydate-btns-confirm"]').click()  # confirm
        time.sleep(random.random())

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
        item['source'] = '河南国资委'  # 需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp):  # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[0]
        return date_text.split("-")
