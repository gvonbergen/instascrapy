# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time

import boto3
from boto3.dynamodb.types import TypeSerializer
from scrapy import signals
from scrapy.exporters import BaseItemExporter

from instascrapy.items import IGUser
from instascrapy.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_PIPELINE_REGION_NAME, \
    DYNAMODB_PIPELINE_TABLE_NAME, DYNAMODB_EXPORTER_IGUSER_FIELDS

serialize = TypeSerializer().serialize

class InstascrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class JSONCleanser(object):
    def process_item(self, item, spider):
        return item
# Todo: Implement JSON cleanser -> Likely in Item File

class DynamoDBExporter(BaseItemExporter):

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name, **kwargs):
        self._configure(kwargs)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.table_name = table_name
        self.encoder = serialize
        self.table = None

    def start_exporting(self):
        session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )
        self.client = session.client('dynamodb')

    def finish_exporting(self):
        self.client = None

    def export_item(self, item):
        serialized_item = dict(self._get_serialized_fields(item))
        additional_fields = {}
        for field in DYNAMODB_EXPORTER_IGUSER_FIELDS:
            additional_fields[field] = self.encoder(serialized_item[field])
        if isinstance(item, IGUser):
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'pk': self.encoder('US#{}'.format(serialized_item['username'])),
                    'sk': self.encoder('US#UPDA#V1#{}'.format(time.strftime("%Y-%m-%dT%H:%M:%S",
                                                               time.localtime(serialized_item['retrieved_at_time'])))),
                    'json': self.encoder(serialized_item['user_json']),
                    **additional_fields
                }
            )
        else:
            pass


class DynamoDbPipeline(object):

    def open_spider(self, spider):
        self.exporter = DynamoDBExporter(AWS_ACCESS_KEY_ID,
                                         AWS_SECRET_ACCESS_KEY,
                                         DYNAMODB_PIPELINE_REGION_NAME,
                                         DYNAMODB_PIPELINE_TABLE_NAME)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item