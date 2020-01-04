# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import time

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.errorfactory import ClientError
from scrapy import signals
from scrapy.exporters import BaseItemExporter

from instascrapy.items import IGUser, IGPost, IGLocation
from instascrapy.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_PIPELINE_REGION_NAME, \
    DYNAMODB_PIPELINE_TABLE_NAME, DYNAMODB_EXPORTER_IGUSER_FIELDS, \
    DYNAMODB_EXPORTER_IGPOST_FIELDS, DYNAMODB_EXPORTER_IGLOCATION_FIELDS

try:
    from instascrapy.settings import DYNAMODB_PIPELINE_ENDPOINT_URL
except:
    DYNAMODB_PIPELINE_ENDPOINT_URL = None

serialize = TypeSerializer().serialize


class InstascrapyPipeline(object):
    def process_item(self, item, spider):
        return item


class DynamoDBExporter(BaseItemExporter):

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name, endpoint_url=None, **kwargs):
        super().__init__(**kwargs)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.table_name = table_name
        self.endpoint_url = endpoint_url
        self.encoder = serialize
        self.logger = logging.getLogger(__name__)
        self.table = None

    def start_exporting(self):
        session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )
        self.client = session.client('dynamodb', endpoint_url=self.endpoint_url)

    def finish_exporting(self):
        self.client = None

    def _dict_serialized(self, input_dict: dict, **kwargs) -> dict:
        serialized_items = {k: serialize(v) for k, v in input_dict.items()}
        if kwargs:
            serialized_items.update({k: serialize(v) for k, v in kwargs.items()})
        return serialized_items

    def _transaction_put_condition(self, data, table, pk, sk, condition, **kwargs):
        put_dict = {
            'TableName': table,
            'ConditionExpression': condition,
            'Item': self._dict_serialized(data, pk=pk, sk=sk, **kwargs),
            'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
        }
        return put_dict

    def export_item(self, item):
        serialized_item = dict(self._get_serialized_fields(item))
        additional_fields = {}
        actual_time = {'retrieved_at_time': serialized_item['retrieved_at_time']}
        if isinstance(item, IGUser):
            for field in DYNAMODB_EXPORTER_IGUSER_FIELDS:
                additional_fields[field] = self.encoder(serialized_item[field])
            # Upload user detail updates
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'pk': self.encoder('US#{}'.format(serialized_item['username'])),
                    'sk': self.encoder('US#UPDA#V1#{}'.format(time.strftime("%Y-%m-%dT%H:%M:%S",
                                                                            time.localtime(actual_time\
                                                                                               ['retrieved_at_time'])))),
                    'json': self.encoder(serialized_item['user_json']),
                    **additional_fields
                }
            )
            # Update main element that there is an update available
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'pk': self.encoder('US#{}'.format(serialized_item['username'])),
                    'sk': self.encoder('USER'),
                },
                UpdateExpression='SET retrieved_at_time = :retrieved_at_time',
                ExpressionAttributeValues={
                    ':retrieved_at_time': self.encoder(actual_time['retrieved_at_time'])
                }
            )
            # Add new pictures
            try:
                for post in serialized_item['last_posts']:
                    self.client.put_item(
                        TableName=self.table_name,
                        Item={
                            'pk': self.encoder('PO#{}'.format(post)),
                            'sk': self.encoder('POST'),
                            'status': self.encoder('PO#ADDE'),
                            'discovered_at_time': self.encoder(actual_time['retrieved_at_time'])
                        },
                        ConditionExpression='attribute_not_exists(pk)'
                    )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    self.logger.debug('Post %s already exists in database', post)
                else:
                    pass
            except KeyError:
                self.logger.debug('User %s has no posts', serialized_item['username'])
        if isinstance(item, IGPost):
            for field in DYNAMODB_EXPORTER_IGPOST_FIELDS:
                try:
                    additional_fields[field] = self.encoder(serialized_item[field])
                except KeyError:
                    pass
            # Upload post detail updates
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'pk': self.encoder('PO#{}'.format(serialized_item['shortcode'])),
                    'sk': self.encoder('PO#UPDA#V1#{}'.format(time.strftime("%Y-%m-%dT%H:%M:%S",
                                                                            time.localtime(actual_time \
                                                                                               ['retrieved_at_time'])))),
                    'json': self.encoder(serialized_item['post_json']),
                    **additional_fields
                }
            )
            # Update main element that there is an update available
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'pk': self.encoder('PO#{}'.format(serialized_item['shortcode'])),
                    'sk': self.encoder('POST'),
                },
                UpdateExpression='SET retrieved_at_time = :retrieved_at_time',
                ExpressionAttributeValues={
                    ':retrieved_at_time': self.encoder(actual_time['retrieved_at_time'])
                }
            )
        if isinstance(item, IGLocation):
            for field in DYNAMODB_EXPORTER_IGLOCATION_FIELDS:
                try:
                    additional_fields[field] = self.encoder(serialized_item[field])
                except KeyError:
                    pass
            # Upload post detail updates
            self.client.put_item(
                TableName=self.table_name,
                Item={
                    'pk': self.encoder('LO#{}'.format(serialized_item['id'])),
                    'sk': self.encoder('LO#UPDA#V1#{}'.format(time.strftime("%Y-%m-%dT%H:%M:%S",
                                                                            time.localtime(actual_time \
                                                                                               ['retrieved_at_time'])))),
                    'json': self.encoder(serialized_item['location_json']),
                    **additional_fields
                }
            )
            # Update main element that there is an update available
            self.client.update_item(
                TableName=self.table_name,
                Key={
                    'pk': self.encoder('LO#{}'.format(serialized_item['id'])),
                    'sk': self.encoder('LOCATION'),
                },
                UpdateExpression='SET retrieved_at_time = :retrieved_at_time',
                ExpressionAttributeValues={
                    ':retrieved_at_time': self.encoder(actual_time['retrieved_at_time'])
                }
            )
        else:
            pass


class DynamoDbPipeline(object):

    def open_spider(self, spider):
        self.exporter = DynamoDBExporter(AWS_ACCESS_KEY_ID,
                                         AWS_SECRET_ACCESS_KEY,
                                         DYNAMODB_PIPELINE_REGION_NAME,
                                         DYNAMODB_PIPELINE_TABLE_NAME,
                                         endpoint_url=DYNAMODB_PIPELINE_ENDPOINT_URL)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item