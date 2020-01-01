""" file includes all database functions """
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
