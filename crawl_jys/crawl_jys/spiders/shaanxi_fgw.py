
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class ShaanxiFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'shaanxi_fgw'
    start_urls = ['http://sndrc.shaanxi.gov.cn']
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
        input_xpath = '//*[@id="text"]'
        search_xpath = "//input[@type='button']"
        items = super(ShaanxiFgwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='xx_box']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='xx_box']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='xx_box']"
        date_xp = "./p/span"
        content_xp = "./p[@class='fbt']"
        title_xp = "./p[@class='btwz_1']/a"
        url_xp = "./p[@class='btwz_1']/a"
        next_xp = "//div[@class='fenye fr']/a[last()-1]"
        super(ShaanxiFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        time.sleep(2)
        wait1_xp = "//div[@class='fl zclb']"  # 等待《时间选择器》的出现
        time_xp = "//div[@class='fl zclb']/ul/li[5]" # 点击 时间选择器
        try:
            self.waitor(wait1_xp)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
        except:
            time.sleep(2)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(1)

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                next.click()
                time.sleep(1+random.random())
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
        item['source'] = '陕西发改委'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

