
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class NxKjtSpider(scrapy.Spider, BaseCrawl):
    name = 'nx_kjt0' #有问题先跳过
    start_urls = ['https://kjt.nx.gov.cn']
    timeout = 15
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
        input_xpath = '//*[@id="textfield"]'
        search_xpath = '//*[@id="search"]/input[3]'
        items = super(NxKjtSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//*[@id='main_content']/div[@class='js-con']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = wait2_xp  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = wait3_xp
        date_xp = "./p/span"
        content_xp = "./a[@class='js-text']"
        title_xp = "./a[@class='js-title']"
        url_xp = title_xp
        next_xp = "//a[@class='next-page']"
        super(NxKjtSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):

        wait1_xp = "//div[@class='jiansuo-con-left']"  # 等待《时间选择器》的出现
        time_xp = "//span[@id='tdtime30days']" # 点击 时间选择器
        self.waitor(wait1_xp)
        try:
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
        item['source'] = '宁夏科技厅'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

