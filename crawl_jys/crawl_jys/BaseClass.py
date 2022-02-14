import datetime
import random
import time
import redis
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver import ChromeOptions, FirefoxProfile, DesiredCapabilities, Firefox
from crawl_jys.items import CrawlJysItem


class BaseCrawl():
    keywords = ["农村产权流转交易", "文化产权", "碳排放权交易","知识产权交易", "数据交易","技术交易","交易场所", "金融资产交易","区域股权","要素市场","产权交易"]
    date_limit = 60
    max_page = 3
    timeout = 7
    browser = None
    # def myGet(self, url):
    #     self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #         "source": """
    #                 Object.defineProperty(navigator, 'webdriver', {
    #                   get: () => undefined
    #                 })
    #               """
    #     })
    #     self.browser.get(url)

    def get_sleeptime(self):
        return random.random() + 1

    def get_element_by_xpath(self, xp, *inv_xp):
        if inv_xp != ():
            for ixp in inv_xp:
                WebDriverWait(self.browser, self.timeout).until(EC.invisibility_of_element((By.XPATH, ixp)))
        return WebDriverWait(self.browser, self.timeout).until(EC.element_to_be_clickable((By.XPATH, xp)))

    def waitor(self, xp, t=timeout):
        WebDriverWait(self.browser, t).until(EC.visibility_of_element_located(
            (By.XPATH, xp)))

    def waitor2(self, xp):
        WebDriverWait(self.browser, self.timeout).until(EC.invisibility_of_element(
            (By.XPATH, xp)))

    def __init__(self, **kwargs):
        # firefox
        # profile = FirefoxProfile()
        # profile.set_preference('devtools.jsonview.enabled', False)
        # profile.set_preference("dom.webdriver.enabled", False)
        # profile.set_preference('useAutomationExtension', False)
        #
        # profile.set_preference('permissions.default.image', 2)
        # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        # # profile.set_preference('javascript.enabled', 'false')
        #
        # profile.update_preferences()
        # options = webdriver.FirefoxOptions()
        # # options.add_argument('-headless')     #取消注释则以无界面形式启动
        # desired = DesiredCapabilities.FIREFOX
        # self.browser = Firefox(firefox_profile=profile, desired_capabilities=desired,
        #                        executable_path='./geckodriver',
        #                        options=options)

        # option = ChromeOptions()  // chrome
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # option.add_experimental_option("prefs", prefs)
        # option.add_experimental_option('useAutomationExtension', False)
        # option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # option.add_argument("--headless") #取消注释则以无界面形式启动
        # self.browser = webdriver.Chrome('./chromedriver', options=option)

        self.myPool = redis.ConnectionPool(host='192.168.12.233', port=6379, db=2)
        self.rds = redis.Redis(connection_pool=self.myPool)
        self.items = []

    def myParse(self, response, input_xp, search_xpath, wait_xp=""):
        url = response.url
        self.browser.get(url)
        input_xpath = input_xp
        search_xpath = search_xpath
        self.default_handle = self.browser.current_window_handle

        if self.name == 'jx_kjt':
            for cancel in self.browser.find_elements_by_xpath(
                    "//div[@id='roll']//img[@src='http://kjt.jiangxi.gov.cn/picture/721/2107231259311833586.gif']"):
                time.sleep(2)
                cancel.click()
        if self.name == "gz_gzw":
            for cancel in self.browser.find_elements_by_xpath('//*[@id="closepiaofu"]/a'):
                cancel.click()

        for keyword in BaseCrawl.keywords[:]:
            # gz_kjt的弹窗
            if self.name == 'gz_kjt' and len(self.browser.find_elements_by_xpath("//div[@id='LAY_layuipro']")) > 0:
                self.browser.find_element_by_xpath(
                    "//a[@class='layui-layer-ico layui-layer-close layui-layer-close2']").click()

            time.sleep(1)
            input = self.get_element_by_xpath(input_xpath)
            input.click()
            input.clear()
            try:
                input.click()
            except:
                pass
            input.send_keys(keyword)
            time.sleep(1)
            try:
                self.get_element_by_xpath(search_xpath).click()
            except Exception as e:
                print("搜索按钮无法点击", e)
                input.send_keys(Keys.ENTER)
            if wait_xp != "": # wait_xp 等待结果页面加载. 搜索结果不会新建窗口时使用
                WebDriverWait(self.browser, self.timeout).until(EC.visibility_of_element_located(
                    (By.XPATH, wait_xp)))
                time.sleep(1)
                new_url = self.browser.current_url
                self.browser.back()
                time.sleep(1)
                js = 'window.open("%s");' % new_url  # 通过执行js，开启一个新的窗口
                self.browser.execute_script(js)

            time.sleep(self.get_sleeptime())
            handles = list(self.browser.window_handles)
            handles.remove(self.default_handle)
            self.browser.switch_to.window(handles[0])
            if self.name == 'gz_kjt': # 贵州kjt需要最大化窗口
                self.browser.maximize_window()
            print(self.browser.current_url, "keyword = " + keyword)
            self.myGetData(keyword)

            self.browser.close()
            self.browser.switch_to.window(self.default_handle)

        self.browser.close()

        res = []
        for item in self.items:
            if self.rds.get(item['url']):
                continue
            if self.rds.get(self.name+"."+ item['title']):
                continue

            self.rds.set(item['url'],1)
            self.rds.set(self.name +"."+ item['title'],1)
            res.append(item)
        self.rds.close()
        return res

    def myGetData(self, keyword):
        pass

    def get_data(self, keyword, wait2_xp, wait3_xp, news_xp, date_xp, content_xp, title_xp, url_xp, next_xp, block_xp=""):
        self.time_select()
        thred = datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)
        if len(news_xp) == 2: # for 上海变化的xp
            if len(self.browser.find_elements_by_xpath(news_xp[0]))>0:
                wait2_xp = news_xp[0]
                wait3_xp = news_xp[0]
                news_xp = news_xp[0]
            else:
                wait2_xp = news_xp[1]
                wait3_xp = news_xp[1]
                news_xp = news_xp[1]

        try:
            WebDriverWait(self.browser, self.timeout).until(EC.visibility_of_element_located(
                (By.XPATH, wait2_xp)))
        except Exception as e:
            print(e)
            print("没有搜索结果")
            return
        #
        has_next = True
        cur = 1
        while (has_next):
            try:
                WebDriverWait(self.browser, self.timeout).until(EC.visibility_of_element_located(
                    (By.XPATH, wait3_xp)))
            except:
                print("当前页没有数据")
                break

            if block_xp != "":
                try:
                    time.sleep(3)
                    self.get_element_by_xpath(block_xp).click()
                except:
                    print("没有更多选项可以点击")

            news = self.browser.find_elements_by_xpath(news_xp)
            for new in news:
                if block_xp != "" and (len(new.find_elements_by_xpath(block_xp))>0 or
                                       len(new.find_elements_by_xpath("./div[@class='clearflx']")) >0):
                    continue
                news_date = self.process_date(new, date_xp)
                news_date = [i for i in map(lambda x: int(x), news_date)]
                nDate = datetime.date(news_date[0], news_date[1], news_date[2])
                if nDate >= thred:

                    if self.name == 'xhs': # 新华社的进行特殊处理
                        self.special_process(keyword, new,content_xp, url_xp,title_xp, nDate)
                        continue
                    else:
                        content = new.find_elements_by_xpath(content_xp)[0]
                    if keyword in content.text:
                        item = CrawlJysItem()
                        item['date'] = str(nDate)
                        item['source'] = self.name
                        item['keyword'] = keyword
                        item['content'] = content.text + "..."
                        self.process_item(new, item, title_xp, url_xp)
                        self.items.append(item)
                        print(item)

            has_next = self.click_next(next_xp)
            cur += 1
            if cur > self.max_page:
                break


    def time_select(self):
        pass

    def click_next(self, next_xp):
        pass

    def process_item(self, new, item, title_xp, url_xp):
        pass

    def process_date(self, new, date_xp):
        pass

    def special_process(self, keyword,new, content_xp, url_xp, title_xp, nDate):
        pass

    def get_real_url(self, url):
        js = 'window.open("%s");' % url  # 通过执行js，开启一个新的窗口
        self.browser.execute_script(js)
        time.sleep(self.get_sleeptime())

        handls = list(self.browser.window_handles)
        pre_handls = handls[:-1]

        for pre_handl in pre_handls:
            handls.remove(pre_handl)
        self.browser.switch_to.window(handls[0])
        real_url = self.browser.current_url
        self.browser.close()

        self.browser.switch_to.window(pre_handls[-1])
        return real_url
