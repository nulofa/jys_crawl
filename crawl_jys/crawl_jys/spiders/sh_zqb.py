# -*- coding: utf-8 -*-
import datetime
import random
import time

import redis
import scrapy
from urllib.parse import unquote,quote
from crawl_jys.BaseClass import BaseCrawl
from scrapy import Request

from crawl_jys.items import CrawlJysItem


class ShZqbSpider(scrapy.Spider):
    name = 'sh_zqb'
    start_urls = ['https://search.cnstock.com/']
    keywords = BaseCrawl.keywords
    thred = datetime.date.today() - datetime.timedelta(BaseCrawl.date_limit)
    myPool = redis.ConnectionPool(host='192.168.12.233', port=6379, db=2)
    rds = redis.Redis(connection_pool=myPool)

    def parse(self, response):
        for keyword in ShZqbSpider.keywords[:]:
            keyword_str = quote(keyword, "utf-8")
            time.sleep(random.random())
            yield Request(response.url+"go.aspx?q="+keyword_str, callback=self.my_parse)

    def my_parse(self, res):
        keyword_str = res.url.split("=")[1]
        keyword = unquote(keyword_str, encoding='utf-8')
        contents = res.xpath("//div[@class='result-article']")
        items = []
        for content in contents:
            cont = content.xpath("./p[@class='des']").xpath("string(.)").extract_first()
            if keyword in cont:
                url_date = content.xpath(".//span[@class='g']/text()").extract_first().replace('\xa0',' ').split(" ")
                url = url_date[0]
                date = url_date[1]
                news_date = [i for i in map(lambda x: int(x), date.split('-'))]
                nDate = datetime.date(news_date[0], news_date[1], news_date[2])

                if nDate > self.thred:
                    title = content.xpath(".//a/text()").extract_first()
                    item = CrawlJysItem()
                    item['url'] = url
                    item['title'] = title
                    item['source'] = '上海证券报'
                    item['content'] = cont
                    item['date'] = str(nDate)
                    item['keyword'] = keyword
                    items.append(item)

        for item in items:
            if self.rds.get(item['url']):
                continue
            if self.rds.get(self.name + "." + item['title']):
                continue

            self.rds.set(item['url'], 1)
            self.rds.set(self.name + "." + item['title'], 1)
            yield item

        try: # 尝试下一页
            next_url = res.xpath("//div[@class='pagination pagination-centered']//li[last()]/a/@href").extract_first()
            if next_url.startswith("http"):
                time.sleep(random.random())
                yield Request(next_url, self.my_parse)
        except Exception as e:
            print("没有下一页", e)




