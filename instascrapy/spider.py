import json
import time

from scrapy import signals
from scrapy.spiders import Spider
from pymongo import MongoClient
from typing import List


class TxMongoSpider(Spider):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coll = None
        self.prefix = None
        self.secondary_key = None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def _set_crawler(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        client = MongoClient(self.settings["MONGODB_URI"])
        db = client[self.settings["MONGODB_DB"]]
        self.coll = db[self.settings["MONGODB_COLLECTION"]]
        crawler.signals.connect(self.close, signals.spider_closed)

    def crawling_scope(self):
        if hasattr(self, "file"):
            scope = self.read_file_json(self.file)
        elif hasattr(self, "keys"):
            scope = [item for item in self.keys.split(",")]
        else:
            update_mode = getattr(self, "update", False)
            scope = self.get_entities(self.secondary_key, update_mode)
        return scope

    @staticmethod
    def read_file_json(file_name: str) -> List:
        """
        Read a JSON formatted byte-stream with entities (e.g. users) and return a list for crawling
        :param file_name: absolute or relative path of the JSON file
        :return: list element with entities for crawling
        """
        with open(file_name, 'r') as f:
            return [item for item in json.load(f)]

    def get_entities(self, category, update_mode=False):
        if update_mode:
            for result in self.coll.find(
                    {
                        'sk': category,
                        "retrieved_at_time": {"$exists": True},
                        'deleted': {'$exists': False}
                    }
            ):
                yield result['pk'][3:]
        else:
            for result in self.coll.find({'sk': category, 'deleted': {'$exists': False},
                                          'retrieved_at_time': {'$exists': False}}):
                yield result['pk'][3:]

    def set_entity_deleted(self, entity, actual_time=None):
        """Sets the entity to deleted"""
        if not actual_time:
            actual_time = int(time.time())
        entry = {'pk': '{}{}'.format(self.prefix, entity), 'sk': self.secondary_key}
        if self.coll.find_one(entry):
            self.coll.update_one(entry, {'$set': {'deleted': True, 'deleted_at_time': actual_time}})
        else:
            entry.update({'deleted': True, 'deleted_at_time': actual_time})
            self.coll.insert_one(entry)
