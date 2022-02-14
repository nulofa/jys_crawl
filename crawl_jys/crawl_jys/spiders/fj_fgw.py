import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class FjFgwSpider(scrapy.Spider, BaseCrawl):
    name = 'fj_fgw'
    start_urls = ['http://fj.gov.cn']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)

    def parse(self, response):
        input_xpath = "//input[@id='selecttags']"
        search_xpath = "//div[@class='ss_box2_2021 clearflx']//button[@class='btn_2021 iconfont b-free-read-leaf']"
        items = super(FjFgwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//ul[@class='nero']/li"  # 等待第一页搜索结果的出现
        wait3_xp = "//ul[@class='nero']/li"  # 等待每一页的搜索结果的出现
        news_xp = "//ul[@class='nero']/li"
        date_xp = "./p/font[@color='#999']"
        content_xp = ".//p"
        title_xp = ".//p/a"
        url_xp = ".//p/a"
        next_xp = "//li[@class='js-page-next js-page-action ui-pager']"
        block_xp = "//div[@class='tlss']"
        super(FjFgwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp, block_xp)


    def time_select(self):
        # 选择站点《发改委》, 先等待搜索结果的出现
        time.sleep(2)
        self.get_element_by_xpath("//span[@id='siteSelect']").click()
        self.get_element_by_xpath("//ul[@id='BMDWLIST']//a[@siteid='ff8080816e59baf3016e5e6956043e2a']").click()
        # self.get_element_by_xpath("//input[@onclick='searchBean.closeModal()']").click()

        self.waitor("//span[@id='searchTool']/a[@class='ss_ssgj b-free-read-leaf']") # 等待搜索工具的出现
        self.get_element_by_xpath("//span[@id='searchTool']/a[@class='ss_ssgj b-free-read-leaf']","//div[@id='layui-layer-shade100002']").click()

        wait1_xp = "//span[@id='timeSelectContent']/a[@onclick='searchBean.timeSearchShow()']"  # 等待《时间选择器》的出现
        time_xp = "//span[@id='timeSelectContent']/a[@onclick='searchBean.timeSearchShow()']" # 点击 时间选择器

        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()

        #设置开始日期
        self.get_element_by_xpath("//input[@id='timezdyqsrq']").click()
        timeTable = "//div[@class='layui-laydate-content']"  # 等待日历的出现
        self.waitor(timeTable)
        pre_month = self.browser.find_elements_by_xpath("//div[@class='layui-laydate-header']/i")[1]
        pre_month.click()
        time.sleep(0.5)
        pre_month.click()
        time.sleep(0.5)
        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()
        time.sleep(1)

        # 设置结束日期
        self.get_element_by_xpath("//input[@id='timezdyjsrq']").click()
        # 等待日历出现
        self.waitor(timeTable)

        self.get_element_by_xpath("//div[@class='laydate-footer-btns']/span[@class='laydate-btns-confirm']").click()
        time.sleep(0.5)
        self.get_element_by_xpath('//button[@onclick="searchBean.timeLimitSearch()"]').click()

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            next.click()
        except:
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = self.get_real_url(new.find_element_by_xpath(url_xp).get_attribute("href"))
        item['source'] = '福建发改委'

    def process_date(self, new, date_xp):
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split(' ')[0].replace("年","-").replace("月","-").replace("日","").split("-")

