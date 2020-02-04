""" file includes all database functions """
import logging

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


_PREFIXES = {
    'POST': {
        'pk': 'PO#',
    },
    'USER':{
        'pk': 'US#'
    },
    'LOCATION':{
        'pk': 'LO#'
    }
}


deserializer = TypeDeserializer().deserialize
serialize = TypeSerializer().serialize



class DynDB:
    def __init__(self,
                 aws_access_key_id,
                 aws_secret_access_key,
                 region_name,
                 table,
                 endpoint_url=None):
        self.table = table
        self.logger = logging.getLogger(__name__)
        self._client = boto3.client('dynamodb',
                                    endpoint_url=endpoint_url,
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)

    def get_category_all(self, category, index, startkey=None):
        paginator = self._client.get_paginator('scan')
        kw =  {}
        if startkey:
            kw['ExclusiveStartKey'] = {'sk': serialize('USER'), 'pk': serialize(startkey)}
        response = paginator.paginate(
            TableName=self.table,
            IndexName=index,
            FilterExpression='sk = :category',
            ExpressionAttributeValues={
                ':category': serialize(category),
            },
            **kw
#            FilterExpression='attribute_not_exists(deleted)'
        )

        for page in response:
            for item in page['Items']:
                yield {k: deserializer(v) for k, v in item.items()}.get('pk')[3:]

    def set_entity_deleted(self, category: str, entity: str) -> None:
        response = self._client.update_item(
            TableName=self.table,
            Key={'pk': serialize(_PREFIXES[category]['pk'] + entity),
                 'sk': serialize(category)},
            UpdateExpression='SET deleted=:deleted',
            ExpressionAttributeValues={
                ':deleted': {'BOOL': True}
            }
        )
        #Todo: Add storage statistics to scrapy logger
        self.logger.debug('Entity %s deleted', entity)


