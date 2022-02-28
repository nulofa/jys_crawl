
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class GdGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'gd_gzw'
    start_urls = ['http://www.gd.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//form[@onsubmit='checkKey()']//input[@name='keywords']"
        search_xpath = "//form[@onsubmit='checkKey()']//button[@type='submit']"
        items = super(GdGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='total-line']"  # 等待第一页搜索结果的出现
        wait3_xp = "//div[@class='total-line']"  # 等待每一页的搜索结果的出现
        news_xp = "//div[@id='list-body']/div[@class='list-item  all']"
        date_xp = "./div[@class='url-date ']/span[@class='date'] "
        content_xp = "./div[@class='content ']"
        title_xp = "./a[@class='title']"
        url_xp = "./a[@class='title']"
        next_xp = ""
        super(GdGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        # 选择国资委 金融196，科技厅172
        self.waitor("//div[@class='list-part']")
        try:
            self.get_element_by_xpath("//span[@id='pickRange']").click()
            self.waitor("//div[@class='item-box']")
        except:
            time.sleep(2)
            self.get_element_by_xpath("//span[@id='pickRange']").click()
            self.waitor("//div[@class='item-box']")
        self.get_element_by_xpath("//div[@class='item-box']//div[@class='item-list']/span[@data-id='195']").click()
        try:
            self.waitor("//div[@class='total-line']")
            self.get_element_by_xpath("//div[@id='pos-list']/a[@key='all']").click()
            self.waitor("//div[@class='total-line']")
        except:
            return
        self.get_element_by_xpath("//div[@id='time-list']/a[@key='year']").click()

    def click_next(self, next_xp):
        try:
            cur_page = self.browser.find_element_by_xpath("//div[@id='page-list']/a[@class='item cur']")
            cur_page_num = cur_page.text
            cur_page_ulr = cur_page.get_attribute("href")
            next_url = cur_page_ulr.replace("page=%s" % cur_page_num, "page=%s" % str(int(cur_page_num) + 1))
            self.browser.get(next_url)
            return True
        except:
            return False

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).text
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '广东国资委'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

