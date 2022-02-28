
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

class NxGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'nx_gzw'
    start_urls = ['http://www.nx.gov.cn']
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
        search_xpath = '//*[@id="btn"]'
        items = super(NxGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='nxrq_search_sec2_cont nxrq_ofh']/div"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='nxrq_search_sec2_cont nxrq_ofh']/div"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='nxrq_search_sec2_cont nxrq_ofh']/div/div[@class='nxrq_search_sec2_cont_item1']"
        date_xp = ".//div[@class='nxrq_search_conmon_st']/span[2]"
        content_xp = ".//div[@class='nxrq_search_conmon_abs']"
        title_xp = ".//p[@class='nxrq_search_conmon_tit']/a"
        url_xp = ".//p[@class='nxrq_search_conmon_tit']/a"
        next_xp = "//div[@class='cm-page']/a[@class='pagenext']"
        super(NxGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        self.waitor2("//div[@class='loadingback']")
        time.sleep(1 + random.random())
        self.get_element_by_xpath('//*[@id="locselect"]').click()
        self.waitor('//*[@id="locselect1"]')
        self.get_element_by_xpath('//*[@id="buscroll"]/li[19]').click()  # select department
        self.get_element_by_xpath('//*[@id="locClose"]').click()  # confirm
        self.waitor2("//div[@class='loadingback']")
        time.sleep(1 + random.random())
        return  # 日期选择有问题
        # wait1_xp = '//*[@id="test1"]'  # 等待《时间选择器》的出现
        # time_xp = '//*[@id="test1"]' # 点击 时间选择器
        # time_xp2 = "//div[@class='layui-laydate-main laydate-main-list-0']//i[@class='layui-icon laydate-icon laydate-prev-m']"  # 时间选择需要 两次点击才能确定
        # self.waitor(wait1_xp)
        # try:
        #     self.browser.find_elements_by_xpath(time_xp)[-1].click()
        #     self.waitor(time_xp2)
        # except:
        #     time.sleep(2)
        #     self.browser.find_elements_by_xpath(time_xp)[-1].click()
        #     self.waitor(time_xp2)
        # self.get_element_by_xpath(time_xp2).click()
        # time.sleep(1)
        # self.get_element_by_xpath("//span[@class='laydate-btns-confirm']").click() # comfirm
        # self.waitor2("//div[@class='loadingback']")

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
        item['source'] = '宁夏国资委'  # 需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp):  # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split("：")[1]
        return date_text.split("-")

