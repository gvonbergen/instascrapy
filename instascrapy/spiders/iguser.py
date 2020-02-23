# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from instascrapy.helpers import ig_extract_shared_data, deep_dict_get
from instascrapy.items import IGUser, IGLoader
from instascrapy.spider import TxMongoSpider


class IguserSpider(TxMongoSpider):
    name = "iguser"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefix = "US#"
        self.secondary_key = "USER"

    @staticmethod
    def _parse_user(loader, data):
        USER_ELEMENTS = [
            "biography",
            "external_url",
            "external_url_linkshimmed",
            "full_name",
            "has_channel",
            "highlight_reel_count",
            "id",
            "is_business_account",
            "is_joined_recently",
            "business_category_name",
            "is_private",
            "is_verified",
            "profile_pic_url",
            "profile_pic_url_hd",
            "username",
            "connected_fb_page",
            "edge_followed_by.count",
            "edge_follow.count",
        ]
        for entry in USER_ELEMENTS:
            loader.add_value(entry.replace(".", "_"), deep_dict_get(data, entry))

        loader.add_value(
            "last_posts",
            [
                post["node"]["shortcode"]
                for post in data["edge_owner_to_timeline_media"]["edges"]
            ],
        )
        loader.add_value("user_json", data)
        loader.add_value("retrieved_at_time", int(time.time()))
        return loader

    def start_requests(self):
        all_users = self.crawling_scope()

        for user in all_users:
            url = "https://www.instagram.com/{}/".format(user)
            yield scrapy.Request(
                url=url, callback=self.parse, errback=self.errback, dont_filter=True
            )

    def parse(self, response):

        if b"Restricted profile" in response.body:
            self.logger.info("Age check: {}".format(response.url))
        else:
            ig_user_dict = ig_extract_shared_data(response=response, category="user")
            ig_user = IGLoader(item=IGUser())
            ig_user = self._parse_user(loader=ig_user, data=ig_user_dict)

            yield ig_user.load_item()

    def errback(self, failure):
        self.logger.debug(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.debug("HttpError on %s", response.url)
            if response.status == 404:
                username = response.url.split("/")[-2:-1][0]
                self.set_entity_deleted(username)
