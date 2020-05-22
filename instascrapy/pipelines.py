# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from pymongo.errors import BulkWriteError
from twisted.internet.defer import inlineCallbacks
from txmongo.connection import ConnectionPool
from bson.codec_options import DEFAULT_CODEC_OPTIONS

from instascrapy.helpers import secondary_key_update
from instascrapy.items import IGUser, IGPost

log = logging.getLogger(__name__)


def mongo_dict(item):
    retrieved_at_time = item.get('retrieved_at_time')
    db_entries = []
    db_entry = {
        'retrieved_at_time': retrieved_at_time
    }
    if isinstance(item, IGUser):
        primary_key = 'US#{}'.format(item.get('username'))
        secondary_key = 'USER'
        db_entry.update({'pk': primary_key,
                         'sk': secondary_key_update("US#", retrieved_at_time),
                         'username': item.get('username'),
                         'user_id': item.get('id'),
                         'json': item.get('user_json')})
        db_entries.append(db_entry)
        db_entries.append({'pk': primary_key, 'sk': secondary_key, 'discovered_at_time': retrieved_at_time})
        for post in item.get('last_posts', []):
            db_entries.append({
                'pk': 'PO#{}'.format(post),
                'sk': 'POST',
                'discovered_at_time': retrieved_at_time
            })
    elif isinstance(item, IGPost):
        primary_key = 'PO#{}'.format(item.get('shortcode'))
        secondary_key = 'POST'
        db_entry.update({
            'pk': primary_key,
            'sk': secondary_key_update("PO#", retrieved_at_time),
            'shortcode': item.get('shortcode'),
            'username': item.get('owner_username'),
            'user_id': item.get('owner_id'),
            'post_id': item.get('id'),
            'json': item.get('post_json')
        })
        if "location_id" in item:
            db_entry.update({"location_id": item.get("location_id")})
        db_entries.append(db_entry)
        db_entries.append({'pk': primary_key, 'sk': secondary_key, 'discovered_at_time': retrieved_at_time})
    else:
        primary_key = None
        secondary_key = None

    return primary_key, secondary_key, db_entries



class MongoDBPipeline(object):
    def __init__(self, mongodb_uri, mongodb_db, mongodb_collection):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.mongodb_collection = mongodb_collection
        self.async_client = None
        self.async_coll = None
        self.codec_options = DEFAULT_CODEC_OPTIONS

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DB'),
            mongodb_collection=crawler.settings.get('MONGODB_COLLECTION'),
        )

    @inlineCallbacks
    def open_spider(self, spider):
        self.async_client = yield ConnectionPool(self.mongodb_uri)
        db = getattr(self.async_client, self.mongodb_db)
        self.async_coll = getattr(db, self.mongodb_collection)

    def close_spider(self, spider):
        self.async_client.disconnect()

    @inlineCallbacks
    def process_item(self, item, spider):
        primary_key, secondary_key, db_entries = mongo_dict(item)
        try:
            yield self.async_coll.insert_many(db_entries, ordered=False)
        except BulkWriteError as e:
            failed_items = ', '.join([x['keyValue']['pk'] for x in e.details['writeErrors']])
            log.debug('Item(s) not written to DB: {}'.format(failed_items))

        set_values = {}
        set_values['retrieved_at_time'] = item.get('retrieved_at_time')

        if isinstance(item, IGPost):
            yield self.async_coll.update_one(
                {'pk': primary_key, 'sk': secondary_key},
                {'$set': {
                    'image': item.get('images')[0],
                    **set_values
                }}
            )
        else:
            yield self.async_coll.update_one(
                {'pk': primary_key, 'sk': secondary_key},
                {'$set': set_values}
            )

        return item
