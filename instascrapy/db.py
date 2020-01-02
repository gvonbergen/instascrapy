""" file includes all database functions """
import logging

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

deserializer = TypeDeserializer().deserialize
serialize = TypeSerializer().serialize

class DynDB:
    def __init__(self,
                 table=None,
                 region_name=None
                 ):
        self.table = table
        self.region = region_name
        self.logger = logging.getLogger(__name__)
        self._client = boto3.client('dynamodb', region_name=self.region)

    def get_all_users(self, index):
        paginator = self._client.get_paginator('query')
        response = paginator.paginate(
            TableName=self.table,
            IndexName=index,
            KeyConditionExpression='sk = :user',
            ExpressionAttributeValues={
                ':user': serialize('USER')
            }
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