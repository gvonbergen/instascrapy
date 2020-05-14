"""
MongoDB Async Extension
"""

import logging

from scrapy import signals
from scrapy.exceptions import NotConfigured
from pymongo.errors import OperationFailure
from twisted.internet.defer import inlineCallbacks
from txmongo.collection import Collection
from txmongo.connection import ConnectionPool
from txmongo.database import Database


LOGGER = logging.getLogger(__name__)

class MongoExtension:
    def __init__(self, mongo_uri, mongo_db, mongo_collection, mongo_user, mongo_password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password
        self.db_client = None
        self.db_connection = None

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.get("MONGO_URI"):
            raise NotConfigured

        ext = cls(
            mongo_uri = crawler.settings.get("MONGO_URI"),
            mongo_db = crawler.settings.get("MONGO_DB"),
            mongo_collection = crawler.settings.get("MONGO_COLLECTION"),
            mongo_user = crawler.settings.get("MONGO_USER", None),
            mongo_password = crawler.settings.get("MONGO_PASSWORD", None)
        )

        crawler.signals.connect(ext.open_spider, signal=signals.spider_opened)
        crawler.signals.connect(ext.close_spider, signal=signals.spider_closed)

        return ext

    @inlineCallbacks
    def open_spider(self, signal, sender, spider):
        self.db_client = yield ConnectionPool(self.mongo_uri)
        mongo_database = yield Database(self.db_client, self.mongo_db)

        if all([self.mongo_user, self.mongo_password]):
            try:
                yield mongo_database.authenticate(self.mongo_user, self.mongo_password)
            except OperationFailure as e:
                LOGGER.error(e)
                sender.engine.close_spider(spider=spider, reason=str(e))

        try:
            yield mongo_database.collection_names()
        except OperationFailure as e:
            LOGGER.error(e)
            sender.engine.close_spider(spider=spider, reason=str(e))
        else:
            spider.db_connection = yield Collection(mongo_database, self.mongo_collection)

        LOGGER.info('MongoPipeline is opened with "%s"', self.mongo_uri)

    @inlineCallbacks
    def close_spider(self, signal, reason, sender, spider):
        yield self.db_client.disconnect()
