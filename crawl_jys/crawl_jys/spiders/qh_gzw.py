
import random
import time
import scrapy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request
from selenium.webdriver.common.by import By

from crawl_jys.items import CrawlJysItem


class QhGzwSpider(scrapy.Spider, BaseCrawl):
    name = 'qh_gzw'
    start_urls = ['http://gxgz.qinghai.gov.cn']
    timeout = 7
    # custom_settings = {
    #     'HEADLESS': False,
    #     'IMAGELESS': True
    # }

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 1

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        input_xpath = '//*[@id="txt1"]'
        search_xpath = '//*[@id="sheach"]/input[@class="btn"]'
        items = super(QhGzwSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//*[@id='GridView1']//td[@align='left']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//*[@id='GridView1']//td[@align='left']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//*[@id='GridView1']//td[@align='left']"
        date_xp = "./table/tbody/tr[2]/td"
        content_xp = "./table/tbody/tr[1]/td"
        title_xp = "./a"
        url_xp = "./a"
        next_xp = ""
        super(QhGzwSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="RadioButtonList1_2"]'  # 等待《时间选择器》的出现
        time_xp = '//*[@id="RadioButtonList1_2"]' # 点击 时间选择器
        time_xp2 = '//*[@id="Button1"]'  # 时间选择需要 两次点击才能确定
        WebDriverWait(self.browser, self.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, wait1_xp)))
        try:
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        except:
            time.sleep(2)
            self.browser.find_elements_by_xpath(time_xp)[-1].click()
            self.waitor(time_xp2)
        self.get_element_by_xpath(time_xp2).click()
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
        item['source'] = '青海国资委'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        print('data = ', new.find_elements_by_xpath(date_xp)[0].text)
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[-2]
        return date_text.split("/")

    def special_process(self, keyword, new, content_xp, url_xp, title_xp, nDate):
        contents = new.find_elements_by_xpath(content_xp)
        if len(contents) == 0:
            self.keyword_exist(keyword, new,url_xp, title_xp, nDate)
        elif keyword in contents[0].text: # 当前页面就有关键词出现的段落，不需要进来具体新闻
            item = self.build_item(nDate, keyword, contents[0])
            self.process_item(new, item, title_xp, url_xp)
            self.items.append(item)
            print(item)
        else:
            self.keyword_exist(keyword, new ,url_xp, title_xp, nDate)



    def keyword_exist(self, keyword, new, url_xp, title_xp, nDate):
        url = new.find_element_by_xpath(url_xp).get_attribute("href")
        js = 'window.open("%s");' % url  # 通过执行js，开启一个新的窗口
        self.browser.execute_script(js)

        handls = list(self.browser.window_handles)
        pre_handls = handls[:-1]

        for pre_handl in pre_handls:
            handls.remove(pre_handl)
        self.browser.switch_to.window(handls[0])

        time.sleep(1 + random.random())
        try:
            self.waitor("//td[@class='yhhei15']//span")
        except:
            print("找不到段落， url=", self.browser.current_url)
            ##关闭新建的窗口
            self.browser.close()
            self.browser.switch_to.window(pre_handls[-1])
            return
        ##进行处理
        paragraphs = self.browser.find_elements_by_xpath("//td[@class='yhhei15']//span")
        content = None
        for p in paragraphs:
            if keyword in p.text:
                content = p
                break
        if content != None:
            item = self.build_item(nDate, keyword, content)
        else:
            ##关闭新建的窗口
            self.browser.close()
            self.browser.switch_to.window(pre_handls[-1])
            return
        time.sleep(random.random())

        ##关闭新建的窗口
        self.browser.close()
        self.browser.switch_to.window(pre_handls[-1])

        self.process_item(new, item, title_xp, url_xp)
        self.items.append(item)
        print(item)

    def build_item(self,nDate, keyword, content):
        item = CrawlJysItem()
        item['date'] = str(nDate)
        item['source'] = "青海国资委"
        item['keyword'] = keyword
        item['content'] = content.text + "..."
        return item

