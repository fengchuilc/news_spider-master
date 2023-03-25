# -*- coding: gbk -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import os
import random
import string
from asyncio import sleep

import pymongo
from scrapy.utils.project import get_project_settings

from news_spider import settings
from news_spider.items import NewsItem
# PyKafka
from pykafka import KafkaClient

class ScrapyKafkaPipeline(object):
    def __init__(self):
        # �ж������������������ɶ
        # 1. ������ȵ���1, listֻ��һ������, ������ַ��϶�����1
        # 2. ����, �ж������Ƿ���list, �ǵĻ��� ���ŷָ�
        # 3. �������һ���ַ���
        settings=get_project_settings()
        kafka_ip_port = settings["KAFKA_IP_PORT"]
        if len(kafka_ip_port) == 1:
            kafka_ip_port = kafka_ip_port[0]
        else:
            if isinstance(kafka_ip_port, list):
                kafka_ip_port = ",".join(kafka_ip_port)
            else:
                kafka_ip_port = kafka_ip_port

        # ��ʼ��client
        self._client = KafkaClient(hosts=kafka_ip_port)

        # ��ʼ��Producer ��Ҫ��topic name����ֽڵ���ʽ
        self._producer = \
            self._client.topics[
                settings["KAFKA_TOPIC_NAME"].encode(encoding="UTF-8")
            ].get_producer()

    def process_item(self, item, spider):
        """
        д���ݵ�Kafka
        :param item:
        :param spider:
        :return:
        """
        self._producer.produce(str(item).encode(encoding="UTF-8"))
        return item

    def close_spider(self, spider):
        """
        ����֮��ر�Kafka
        :return:
        """
        self._producer.stop()



# class NewsSpiderPipeline(object):
#     def process_item(self, item, spider):
#         return item
#
#
# class MongoPipeline(object):
#     # -*- coding: utf-8 -*-
#     def __init__(self):
#         settings = get_project_settings()
#         host = settings["MONGODB_HOST"]
#         port = settings["MONGODB_PORT"]
#         dbname = settings["MONGODB_DBNAME"]
#         self.sheetitems = settings["MONGODB_ITEMS"]
#         self.sheetbody=settings['MONGODB_BODY']
#
#         # ����MONGODB���ݿ�����
#         client = pymongo.MongoClient(host=host, port=port)
#         # ָ�����ݿ�
#         self.mydb = client[dbname]
#         # ������ݵ����ݿ����
#
#
#     def process_item(self, item, spider):
#         self.sheet = self.mydb[self.sheetitems]
#         data = dict(item)
#         self.sheet.insert_one(data)
#         return item
#

# class NewsSpiderPipeline(object):
#
#     def process_item(self, item, spider):
#         if type(item)==NewsItem:
#             dir_path = os.path.join(os.getcwd(), 'news', item['source'], item['time'].split(' ')[0])
#             if not os.path.exists(dir_path):
#                 os.makedirs(dir_path)
#             news_file_path = os.path.join(dir_path, item['newsId'] + '.json')
#             if os.path.exists(news_file_path) and os.path.isfile(news_file_path):
#                 print('---------------------------------------')
#                 print(item['newsId'] + '.json exists, not overriden')
#                 print('---------------------------------------')
#                 return item
#             news_file = codecs.open(news_file_path, 'w', 'utf-8')
#             line = json.dumps(dict(item), ensure_ascii=False)
#             news_file.write(line)
#             news_file.close()
#             return item
#
#         elif type(item)==BodyItem:
#             dir_path = os.path.join(os.getcwd(), 'news', item['source'], item['time'].split(' ')[0])
#             if not os.path.exists(dir_path):
#                 os.makedirs(dir_path)
#             news_body_path = os.path.join(dir_path, item['newsId'] + '.html')
#             if os.path.exists(news_body_path) and os.path.isfile(news_body_path):
#                 print('---------------------------------------')
#                 print(item['newsId'] + '.html exists, not overriden')
#                 print('---------------------------------------')
#                 return item
#             news_file = codecs.open(news_body_path, 'w', 'utf-8')
#             line1 = json.dumps(dict(item), ensure_ascii=False)
#             news_file.write(line1)
#             news_file.close()
#             return item
