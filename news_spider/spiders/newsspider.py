#!usr/bin/env python
#-*- coding:utf-8 -*-


import random
import html
from news_spider.items import NewsItem, BodyItem
from news_spider.settings import DEFAULT_REQUEST_HEADERS
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy import Request, Spider
from scrapy.selector import Selector
import json
import re
import time
import datetime

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')\
        .replace('[]','')


class NeteaseNewsSpider(CrawlSpider):
    name = "netease_news_spider"
    allowed_domains = ['163.com']
    start_urls = ['https://news.163.com',
                  ]

    # http://news.163.com/17/0823/20/CSI5PH3Q000189FH.html

    url_pattern = r'https://www\.163\.com/\w+/article/(\w+)\.html'

    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]


    def parse_news(self, response):
        ran = random.randint(1, 30)
        if ran == 1:
            time.sleep(3)
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'netease'
        if response.css('.post_body'):
            body=html.unescape(response.css('.post_body').extract()[0])
        else:
            body='null'
        if response.css('.post_info'):
            time_ = response.css('.post_info').extract()[0].split()[2]+'  '+response.css('.post_info').extract()[0].split()[3]
            # time_ = response.css('.post_info').extract()[1].split()[0]+' '+response.css('.post_info').extract()[1].split()[1]
        else:
            time_ = 'unknown'
        newsId = pattern.group(1)
        url = response.url
        title=response.css('h1::text').extract()[0]
        # title = sel.xpath('//*[@id="container"]/div[1]/h1/text()').extract()[0]
        contents = ListCombiner(sel.xpath('//p/text()').extract()[2:-3])
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{}'.format(newsId)
        yield Request(comment_url,  self.parse_comment, meta={'source':source,
                                                             'newsId':newsId,
                                                             'url':url,
                                                             'title':title,
                                                             'contents':contents,
                                                             'time':time_,
                                                             'body':body
                                                             },dont_filter=True)

    def parse_comment(self, response):
        result = json.loads(response.text)
        item = NewsItem()
        body=BodyItem()
        body['type']='body'
        body['body']=response.meta['body']
        body['time'] = response.meta['time']
        body['source'] = response.meta['source']
        body['newsId'] = response.meta['newsId']
        yield body
        item['type']='item'
        item['source'] = response.meta['source']
        item['newsId'] = response.meta['newsId']
        item['url'] = response.meta['url']
        item['title'] = response.meta['title']
        item['contents'] = response.meta['contents']
        item['comments'] = result['cmtAgainst'] + result['cmtVote'] + result['rcount']
        item['time'] = response.meta['time']
        yield item



class SinaNewsSpider(CrawlSpider):
    name = "sina_news_spider"
    start_urls = ['https://news.sina.com.cn']
    # start_urls = ['https://edu.sina.com.cn/zxx/2023-02-16/doc-imyfwccx5310997.shtml']
    # https://finance.sina.com.cn/review/hgds/2017-08-25/doc-ifykkfas7684775.shtml
    # url_pattern = r'(https://(?:\w+\.)*news\.sina\.com\.cn)/.*/(\d{4}-\d{2}-\d{2})/doc-(.*)\.shtml'

    url_pattern = r'https://(?:\w+\.)sina\.com\.cn/.*/doc-(.*)\.shtml'

    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        ran = random.randint(1, 30)
        if ran == 1:
            time.sleep(3)
        sel = Selector(response)
        title=response.css('h1::text').extract()[0]

        source = 'sina'
        if response.css('.article'):
            body = html.unescape(response.css('.article').extract()[0]).replace('src="//','src="https://')
        else:
            body = 'null'
        try:
            if response.css('.date'):
                time_=response.css('.date::text').get().strip().replace('年','-').replace('月','-').replace('日','')
            elif response.css('#pub_date'):
                t=response.css('#pub_date::text').get()
                time_ = response.css('#pub_date::text').get().strip().replace('年','-').replace('月','-').replace('日',' ').split(' ')[0]+'  '+response.css('#pub_date::text').get().strip().replace('年','-').replace('月','-').replace('日',' ').split(' ')[1]
            else:
                time_ = 'unknown'
        except:
            time_='unknown'
        newsId = 'i'+sel.xpath("//meta[@name='publishid']").xpath('@content').extract()[0]
        url = response.url
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
        comment_elements = sel.xpath("//meta[@name='comment']").xpath('@content').extract()[0]
        comment_channel = comment_elements.split(':')[0]
        comment_id = comment_elements.split(':')[1]
        comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={}&newsid={}'.format(comment_channel,comment_id)
        yield Request(comment_url, self.parse_comment, dont_filter=True , meta={'source':source,
                                                             'newsId':newsId,
                                                             'url':url,
                                                             'title':title,
                                                             'contents':contents,
                                                             'time':time_,
                                                             'body':body
                                                            })


    def parse_comment(self, response):
        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        body = BodyItem()
        body['type'] = 'body'
        body['body'] = response.meta['body']
        body['time'] = response.meta['time']
        body['source'] = response.meta['source']
        body['newsId'] = response.meta['newsId']
        yield body
        item = NewsItem()
        item['type'] = 'item'
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        yield item


class ChinaNewsSpider(CrawlSpider):
    name = 'china_news_spider'

    start_urls = ['https://www.chinanews.com.cn/']
    url_pattern = r'https://www.chinanews.com.cn/.*/[0-9]{4}/[0-9]{2}-[0-9]{2}/\d+.shtml'

    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        ran = random.randint(1, 30)
        if ran == 1:
            time.sleep(3)

        sel = Selector(response)
        title = response.css('h1::text').extract()[0].replace('\n','').replace('\r','').strip()
        source = 'china'
        if response.css('.content_maincontent_content'):
            body = html.unescape(response.css('.content_maincontent_content').extract()[0]).replace('src="//', 'src="https://')
        if response.css("#newsdate"):
            date=response.css("#newsdate").attrib['value']
        else:
            date=""
        if response.css("#newstime"):
            t=response.css("#newstime").attrib['value']
        else:
            t=""
        time_=date+" "+t
        newsId =response.css("#newsid").attrib['value']
        url = response.url
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
        comment_url = 'https://www.chinanews.com.cn/'
        yield Request(comment_url, self.parse_comment, dont_filter=True, meta={'source': source,
                                                                               'newsId': newsId,
                                                                               'url': url,
                                                                               'title': title,
                                                                               'contents': contents,
                                                                               'time': time_,
                                                                               'body': body
                                                                               })

    def parse_comment(self, response):
        body = BodyItem()
        body['type'] = 'body'
        body['body'] = response.meta['body']
        body['time'] = response.meta['time']
        body['source'] = response.meta['source']
        body['newsId'] = response.meta['newsId']
        yield body
        item = NewsItem()
        item['type'] = 'item'
        item['comments'] =0
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        yield item


#
# class TencentRollNewsSpider(Spider):
#     name = 'tencent_roll_news_spider'
#     allowed_domains = ['news.qq.com', 'tech.qq.com','ent.qq.com','sport.qq.com','edu.qq.com',
#                        'finance.qq.com','games.qq.com','auto.qq.com','house.qq.com']
#     # start_urls = ['http://news.qq.com/articleList/rolls/']
#     url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
#
#     list_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site={class_}&mode=1&cata=&date={date}&page={page}&_={time_stamp}'
#     date_time = datetime.datetime.now().strftime('%Y-%m-%d')
#     time_stamp = int(round(time.time()*1000))
#     item_num = 0
#
#     def start_requests(self):
#         categories = ['tech', 'news', 'ent', 'sports', 'finance', 'games', 'auto', 'edu', 'house']
#         dates = ['2018-06-06']
#         for date in dates:
#             for category in categories:
#                 DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
#                 DEFAULT_REQUEST_HEADERS['Host'] = 'roll.news.qq.com'
#                 DEFAULT_REQUEST_HEADERS['Referer'] = 'http://{}.qq.com/articleList/rolls/'.format(category)
#                 yield Request(self.list_url.format(class_=category, date=date, page='1', time_stamp=str(self.time_stamp)), callback=self.parse_list, meta={'category':category, 'date':date},dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)
#
#     def parse_list(self, response):
#         results = json.loads(response.text[9:-1])
#         article_info = results['data']['article_info']
#         category = response.meta['category']
#         for element in article_info:
#             time_ = element['time']
#             title = element['title']
#             column = element['column']
#             url = element['url']
#             if column != u'图片':
#                 DEFAULT_REQUEST_HEADERS['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
#                 DEFAULT_REQUEST_HEADERS['Host'] = '{}.qq.com'.format(category)
#                 DEFAULT_REQUEST_HEADERS['Referer'] = ''
#
#                 yield Request(url, callback=self.parse_news, meta={'column':column,
#                                                                    'url':url,
#                                                                    'title':title,
#                                                                    'time':time_,
#                                                                    'category':category
#                                                                   },
#                                                                    dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)
#         list_page = results['data']['page']
#         list_count = results['data']['count']
#         if list_page < list_count:
#             time_stamp = int(round(time.time() * 1000))
#             yield Request(self.list_url.format(class_=category, date=response.meta['date'], page=str(list_page+1), time_stamp=str(time_stamp)), callback=self.parse_list, meta={'category':category}, dont_filter=True)
#
#     def parse_news(self, response):
#         sel = Selector(response)
#
#         url = response.meta['url']
#         title = response.meta['title']
#         column = response.meta['column']
#         time_ = response.meta['time']
#         category = response.meta['category']
#
#         pattern = re.match(self.url_pattern, str(response.url))
#         source = 'tencent.rollnews'
#         date = pattern.group(2)
#         date = date[0:4] + '-' + date[4:6] + '-' + date[6:]
#         newsId = pattern.group(3)
#         contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
#
#         if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]'):
#             cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()').extract()[0]
#             cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
#         elif category == 'tech' and sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script'):
#             cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script/text()').extract()[0]
#             cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
#         elif category == 'ent' and sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[3]/script[2]'):
#             cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[3]/script[2]/text()').extract()[0]
#             cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
#         elif category == 'auto' and sel.xpath('//*[@id="Main-Article-QQ"]/div[1]/div[1]/div[3]/div[8]/script'):
#             cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div[1]/div[1]/div[3]/div[8]/script/text()').extract()[0]
#             cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
#         elif category == 'edu' and sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[3]/script[2]'):
#             cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[3]/script[2]/text()').extract()[0]
#             cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
#         elif category == 'house':
#             cmt_id = re.findall(r'cmt_id = (\d*);', response.text)[0]
#         else:
#             item = TencentRollNewsItem()
#             item['source'] = source
#             item['category'] = category
#             item['time'] = time_
#             item['date'] = date
#             item['contents'] = contents
#             item['title'] = title
#             item['url'] = url
#             item['newsId'] = newsId
#             item['comments'] = 0
#             item['column'] = column
#             return item
#
#         comment_url = 'http://coral.qq.com/article/{}/comment?commentid=0&reqnum=1&tag=&callback=mainComment&_=1389623278900'.format(cmt_id)
#         print(comment_url)
#         yield Request(comment_url, callback=self.parse_comment, dont_filter=True, meta={'source': source,
#                                                                                'date': date,
#                                                                                'newsId': newsId,
#                                                                                'url': url,
#                                                                                'title': title,
#                                                                                'contents': contents,
#                                                                                'time': time_,
#                                                                                'column': column,
#                                                                                'category': category
#                                                                                })
#     def parse_comment(self, response):
#         if re.findall(r'"total":(\d*)\,', response.text):
#             comments = re.findall(r'"total":(\d*)\,', response.text)[0]
#         else:
#             comments = 0
#         item = TencentRollNewsItem()
#         item['category'] = response.meta['category']
#         item['source'] = response.meta['source']
#         item['time'] = response.meta['time']
#         item['date'] = response.meta['date']
#         item['contents'] = response.meta['contents']
#         item['title'] = response.meta['title']
#         item['url'] = response.meta['url']
#         item['newsId'] = response.meta['newsId']
#         item['comments'] = comments
#         item['column'] = response.meta['column']
#         return item
#
#
# class SohuNewsSpider(CrawlSpider):
#     name = "sohu_news_spider"
#     pass
#
#
#
# class IfengNewsSpider(CrawlSpider):
#     name = "ifeng_news_spider"
#     pass
#
#
