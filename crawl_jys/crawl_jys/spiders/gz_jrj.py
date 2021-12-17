
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class GzJrjSpider(scrapy.Spider, BaseCrawl):
    name = 'gz_jrj'
    start_urls = ['http://jr.guizhou.gov.cn']
    cur_page = 1
    max_page = 5

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="keyword"]'
        search_xpath = "//div[@class='search']/a"
        items = super(GzJrjSpider, self).myParse(response, input_xpath, search_xpath,"//div[@class='seach_result_num js_seach_result_num']/span")
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='seach_result_num js_seach_result_num']/span"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='seach_result_num js_seach_result_num']/span"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='item hasImg is-news']"
        date_xp = "./span[@class='sourceTime']"
        content_xp = ".//p[@class='js_text']"
        title_xp = "./a[@class='title log-anchor']"
        url_xp = "./a[@class='title log-anchor']"
        next_xp = "//div[@class='oPager']/a[last()]"
        super(GzJrjSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        time.sleep(2)
        return  # gz_jrj的时间选择有问题


    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            next.click()
            time.sleep(2)
            if (GzJrjSpider.cur_page == GzJrjSpider.max_page):
                GzJrjSpider.cur_page = 1
                return False
            GzJrjSpider.cur_page += 1

        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("：")[1].split(" ")[0]
        return date_text.split("-")

