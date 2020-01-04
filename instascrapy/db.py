""" file includes all database functions """
import logging

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

deserializer = TypeDeserializer().deserialize
serialize = TypeSerializer().serialize

class DynDB:
    def __init__(self,
                 aws_access_key_id,
                 aws_secret_access_key,
                 table,
                 region_name):
        self.table = table
        self.logger = logging.getLogger(__name__)
        self._client = boto3.client('dynamodb',
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)

    def get_category_all(self, category, index):
        paginator = self._client.get_paginator('query')
        response = paginator.paginate(
            TableName=self.table,
            IndexName=index,
            KeyConditionExpression='sk = :category',
            ExpressionAttributeValues={
                ':category': serialize(category),
            },
            FilterExpression='attribute_not_exists(deleted)'
        )

        for page in response:
            for item in page['Items']:
                yield {k: deserializer(v) for k, v in item.items()}.get('pk')[3:]

    def set_entity_deleted(self, entity):
        response = self._client.update_item(
            TableName=self.table,
            Key={'pk': serialize('US#' + entity),
                 'sk': serialize('USER')},
            UpdateExpression='SET deleted=:deleted',
            ExpressionAttributeValues={
                ':deleted': serialize(True)
            }
        )
        self.logger.debug('Entity %s deleted', entity)