
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class ShaanxiGovSpider(scrapy.Spider, BaseCrawl):
    name = 'shaanxi_gov'
    start_urls = ['http://www.shaanxi.gov.cn']
    # custom_settings = {
    #     'HEADLESS': False,
    #     'IMAGELESS': True
    # }
    timeout = 5

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 2

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = '//*[@id="q"]'
        search_xpath = "//button[@onclick='submitsearch()']"
        items = super(ShaanxiGovSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='searKYY']/div[last()]"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='searKYY']/div[last()]"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='searKYY']/div[last()]"
        date_xp = ".//div[@class='rt']/span[last()]"
        content_xp = ".//div[@class='con2']"
        title_xp = ".//a[@class='tcon']"
        url_xp = ".//a[@class='tcon']"
        next_xp = "//div[@class='searchpage']/a[last()-1]"
        super(ShaanxiGovSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//div[@class="mainCon clearfix"]'  # 等待《时间选择器》的出现
        time_xp = "//ul[@class='lf sort_ul']/li[1]/a[2]" # 点击 时间选择器
        self.waitor(wait1_xp)
        try:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
        except:
            time.sleep(2)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(1+random.random())

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
        item['source'] = '陕西政府网'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        if len(new.find_elements_by_xpath(".//table"))>0:
            return ['1970','1','1']
        return date_text.split("-")

