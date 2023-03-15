from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    # process.crawl('netease_news_spider')
    process.crawl('china_news_spider')
    process.start()
