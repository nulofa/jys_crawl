
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class GzKjtSpider(scrapy.Spider, BaseCrawl):
    name = 'gz_kjt'
    start_urls = ['http://kjt.guizhou.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = '//*[@id="keyword"]'
        search_xpath = "//p[@class='seachBtn']/a[1]"
        items = super(GzKjtSpider, self).myParse(response, input_xpath, search_xpath,"//div[@class='seach_result_num js_seach_result_num']/span")
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='item hasImg is-news']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='item hasImg is-news']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='item hasImg is-news']"
        date_xp = "./span[@class='sourceTime']"
        content_xp = ".//p[@class='js_text']"
        title_xp = "./a[@class='title log-anchor']"
        url_xp = "./a[@class='title log-anchor']"
        next_xp = "//div[@class='oPager']/a[last()]"
        super(GzKjtSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = "//div[@class='search_filter_item search_filter_item_time js_search_filter_item_time']/span"  # 等待《时间选择器》的出现
        time_xp = "//div[@class='search_filter_item search_filter_item_time js_search_filter_item_time']/span"  # 点击 时间选择器
        time_xp2 = "//div[@class='btn js_time_btn']"  # 确定按钮
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        self.waitor("//div[@class='time_list js_time_list']")

        self.get_element_by_xpath("//input[@id='startTime']").click()
        self.waitor('//*[@id="layui-laydate1"]')  # 等待日历出现
        pre_month = self.browser.find_elements_by_xpath("//div[@class='layui-laydate-header']/i")[1]
        pre_month.click()
        time.sleep(0.5)
        pre_month.click()
        time.sleep(0.5)
        # 确定开始日期
        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()
        time.sleep(1)

        # 设置结束日期
        self.get_element_by_xpath("//input[@id='endTime']").click()
        self.waitor('//*[@id="layui-laydate2"]')  # 等待日历出现
        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()

        # 确定时间范围
        self.get_element_by_xpath(time_xp2).click()

    def click_next(self, next_xp):
        has_next = True
        try:
            pre_url = self.browser.current_url
            next = self.get_element_by_xpath(next_xp)
            next.click()
            time.sleep(2)
            cur_url = self.browser.current_url
            if pre_url == cur_url:
                return False
        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = '贵州科技厅'

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("：")[1].split(" ")[0]
        return date_text.split("-")

