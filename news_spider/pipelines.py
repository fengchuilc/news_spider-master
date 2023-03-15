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

from news_spider.items import NewsItem, BodyItem


class NewsSpiderPipeline(object):

    def process_item(self, item, spider):
        if type(item)==NewsItem:
            dir_path = os.path.join(os.getcwd(), 'news', item['source'], item['time'].split(' ')[0])
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            news_file_path = os.path.join(dir_path, item['newsId'] + '.json')
            if os.path.exists(news_file_path) and os.path.isfile(news_file_path):
                print('---------------------------------------')
                print(item['newsId'] + '.json exists, not overriden')
                print('---------------------------------------')
                return item
            news_file = codecs.open(news_file_path, 'w', 'utf-8')
            line = json.dumps(dict(item), ensure_ascii=False)
            news_file.write(line)
            news_file.close()
            return item

        elif type(item)==BodyItem:
            dir_path = os.path.join(os.getcwd(), 'news', item['source'], item['time'].split(' ')[0])
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            news_body_path = os.path.join(dir_path, item['newsId'] + '.html')
            if os.path.exists(news_body_path) and os.path.isfile(news_body_path):
                print('---------------------------------------')
                print(item['newsId'] + '.html exists, not overriden')
                print('---------------------------------------')
                return item
            news_file = codecs.open(news_body_path, 'w', 'utf-8')
            news_file.write(item['body'])
            news_file.close()
            return item
