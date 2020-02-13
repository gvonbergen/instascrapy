from scrapy import signals
from scrapy.spiders import Spider
from pymongo import MongoClient

from instascrapy.db import DynDB


class TxMongoSpider(Spider):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None
        self.db = None
        self.coll = None
        self.batch_size = 100

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def _set_crawler(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.conn = MongoClient(self.settings['MONGO_URI'])
        self.db = self.conn[self.settings['MONGO_DB']]
        if self.settings['MONGO_USER'] and self.settings['MONGO_PASSWORD']:
            self.db.authenticate(self.settings['MONGO_USER'],
                                 self.settings['MONGO_PASSWORD'])
        self.coll = self.db[self.settings['MONGO_COLLECTION']]
        crawler.signals.connect(self.close, signals.spider_closed)

    def get_entities(self, category):
        for result in self.coll.find({'sk': category}).batch_size(self.batch_size):
            yield result['pk'][3:]

class DynDBSpider(Spider):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None

    def setup_dynamodb(self, crawler):
        if self.db is not None:
            return

        dynamodb_settings = {
            'aws_access_key_id': crawler.settings.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': crawler.settings.get('AWS_SECRET_ACCESS_KEY'),
            'region_name': crawler.settings.get('AWS_DYNAMODB_REGION_NAME'),
            'table': crawler.settings.get('AWS_DYNAMODB_TABLE_NAME'),
            'endpoint_url': crawler.settings.get('AWS_DYNAMODB_ENDPOINT_URL', None)
        }
        if not dynamodb_settings['aws_access_key_id'] or not dynamodb_settings['aws_secret_access_key']:
            raise ValueError('AWS Credentials are missing')
        if not dynamodb_settings['region_name']:
            raise ValueError('AWS Region is missing')
        if not dynamodb_settings['table']:
            raise ValueError('AWS DynamoDB is missing')

        self.db = DynDB(
            aws_access_key_id=dynamodb_settings['aws_access_key_id'],
            aws_secret_access_key=dynamodb_settings['aws_secret_access_key'],
            region_name=dynamodb_settings['region_name'],
            table=dynamodb_settings['table'],
            endpoint_url=dynamodb_settings['endpoint_url']
        )
        self.crawler = crawler
        self.settings = crawler.settings
        # Todo: Find out how crawler signals connect work
        crawler.signals.connect(self.close, signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider.setup_dynamodb(crawler)
        return spider
