from scrapy import signals
from scrapy.spiders import Spider

from instascrapy.db import DynDB


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
            table=dynamodb_settings['table']
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
