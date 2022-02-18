
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

from crawl_jys.items import CrawlJysItem


class XhsSpider(scrapy.Spider, BaseCrawl):
    name = 'xhs'
    start_urls = ['http://xinhuanet.com']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 1

    def parse(self, response):
        input_xpath = '//*[@id="inputwd"]'
        search_xpath = '//*[@id="searchSubmit"]'
        items = super(XhsSpider, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = "//div[@class='news']"  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = "//div[@class='news']"  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = "//div[@class='news']"
        date_xp = ".//p[@class='newstime']/span"
        content_xp = ".//p[@class='newstext']"
        title_xp = "./h2/a"
        url_xp = "./h2/a"
        next_xp = '//*[@id="pagination"]/a[last()]'
        super(XhsSpider, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = '//*[@id="newsCount"]'  # 等待搜索结果数的出现
        try:
            self.waitor(wait1_xp,5)
        except:
            return
        self.get_element_by_xpath('//*[@id="radioAll"]').click() # 点击按全文搜索
        time.sleep(1+ random.random())

        # self.get_element_by_xpath('//*[@id="sort"]').click()
        # sorted_by_time = '//*[@id="sort"]/option[@value="0"]'
        # self.waitor(sorted_by_time)
        # self.get_element_by_xpath(sorted_by_time).click()
        # time.sleep(1+random.random())

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(1+random.random())
                next.click()
                time.sleep(1+random.random())
                self.waitor("//div[@class='news']")
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

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text.split(" ")[0]
        return date_text.split("-")


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
            self.waitor('/html/body/div/div/div//p')
        except:
            print("找不到段落， url=", self.browser.current_url)
            ##关闭新建的窗口
            self.browser.close()
            self.browser.switch_to.window(pre_handls[-1])
            return
        ##进行处理
        paragraphs = self.browser.find_elements_by_xpath('/html/body/div/div/div//p')
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
        item['source'] = "新华网"
        item['keyword'] = keyword
        item['content'] = content.text + "..."
        return item
