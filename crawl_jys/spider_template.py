
template = '''
import random
import time
import scrapy
from crawl_jys.BaseClass import BaseCrawl

class %s(scrapy.Spider, BaseCrawl):
    name = '%s'
    start_urls = ['%s']

    def __init__(self):
        scrapy.Spider.__init__(self)
        BaseCrawl.__init__(self)
        self.cur_page = 1
        self.max_page = 5

    def parse(self, response):
        input_xpath = ""
        search_xpath = ""
        items = super(%s, self).myParse(response, input_xpath, search_xpath)
        for item in items:
            yield item

    def myGetData(self, keyword):
        wait2_xp = ""  # 等待第一页搜索结果的出现, 无特殊情况可设置与news_xp一样
        wait3_xp = ""  # 等待每一页的搜索结果的出现, 无特殊情况可设置与news_xp一样
        news_xp = ""
        date_xp = ""
        content_xp = ""
        title_xp = ""
        url_xp = ""
        next_xp = ""
        super(%s, self).get_data(keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp,
                                          title_xp, url_xp, next_xp)

    def time_select(self):
        wait1_xp = ""  # 等待《时间选择器》的出现
        time_xp = "" # 点击 时间选择器
        time_xp2 = ""  # 时间选择需要 两次点击才能确定
        self.waitor(wait1_xp)
        self.browser.find_elements_by_xpath(time_xp)[-1].click()
        time.sleep(1)
        self.get_element_by_xpath(time_xp2).click()
        time.sleep(1)

    def click_next(self, next_xp):
        has_next = True
        try:
            next = self.get_element_by_xpath(next_xp)
            if self.cur_page < self.max_page:
                time.sleep(1+random.random())
                next.click()
                self.cur_page += 1
            else:
                self.cur_page = 1
                return False
        except Exception as e:
            print("点击下一页发生错误: \\n", e)
            self.cur_page = 1
            has_next = False
        return has_next

    def process_item(self, new, item, title_xp, url_xp):
        item['title'] = new.find_element_by_xpath(title_xp).get_attribute("title")
        item['url'] = new.find_element_by_xpath(url_xp).get_attribute("href")
        item['source'] = 'xxx'  #需要修改为当前的网站名，如：广东发改委

    def process_date(self, new, date_xp): # 返回[年，月，日]，如: 2021-12-12 则返回[2012,12,12]
        date_text = new.find_elements_by_xpath(date_xp)[0].text
        return date_text.split("-")

'''

import sys

if __name__ == '__main__':
    assert len(sys.argv) == 3
    name = sys.argv[1]
    url = sys.argv[2]
    className= "".join([ss.capitalize() for ss in name.split("_")])+"Spider"
    spider_tempate = template % (className, name, url, className, className)
    with open("crawl_jys/spiders/%s.py"%name, 'w', encoding="utf-8") as f:
        f.write(spider_tempate)
