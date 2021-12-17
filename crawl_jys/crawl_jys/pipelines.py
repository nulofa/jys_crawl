# -*- coding: utf-8 -*-
import pymysql
import redis
from elasticsearch import Elasticsearch
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class CrawlJysPipeline:
    # This method is called when the spider is opened.
    def open_spider(self, spider):
        self.conn = pymysql.connect(host="192.168.12.231", user="root", password="apex2021", database="jys_msg",
                                    charset="utf8")
        self.cnt_mysql = 0

    def process_item(self, item, spider):
        print("mysql: item = ", item)
        insert_sql = 'insert into message values(null, "%s","%s", "%s", "%s", "%s", "%s")'\
                     % (item['date'],item['source'],item['keyword'], item['title'], item['content'], item['url'])
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(insert_sql)
                self.conn.commit()
                self.cnt_mysql += 1
        except Exception as e:
            print(e)
            cursor.close()
            self.conn.rollback()
        return item


    #This method is called when the spider is closed.
    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        print("入库mysql已结束, 入库%d条数据" % self.cnt_mysql)

class CrawlJysPipeline2es:
    # This method is called when the spider is opened.
    def open_spider(self, spider):
        # self.es = Elasticsearch("http://192.168.12.233:9200", http_auth=('elastic', 'apexes'))
        self.cnt_es = 0

    def process_item(self, item, spider):
        # print("es: item = ", item)
        # item = dict(item)
        # self.es.index(index="jys_msgs", doc_type="_doc", body=item)
        # self.cnt_es += 1
        return item

    #This method is called when the spider is closed.
    def close_spider(self, spider):
        print("入库es已结束, 入库%d条数据" % self.cnt_es)
