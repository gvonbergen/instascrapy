# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from instascrapy.helpers import ig_extract_shared_data, deep_dict_get
from instascrapy.items import IGLoader, IGPost
from instascrapy.spider import TxMongoSpider


class IgpostSpider(TxMongoSpider):
    name = 'igpost'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefix = 'PO#'
        self.secondary_key = 'POST'

    def start_requests(self):
        all_posts = self.crawling_scope()

        for post in all_posts:
            url = 'https://www.instagram.com/p/{}/'.format(post)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, dont_filter=True)


    @staticmethod
    def _parse_post(loader, data):
        POST_ELEMENTS = [
            'id',
            'shortcode',
            'dimensions',
            'fact_check_overall_rating',
            'fact_check_information',
            'display_url',
            'display_resources',
            'accessibility_caption',
            'is_video',
            'tracking_token',
            'edge_media_to_tagged_user',
            'edge_media_to_caption',
            'caption_is_edited',
            'has_ranked_comments',
            'edge_media_to_parent_comment',
            'edge_media_to_hoisted_comment',
            'edge_media_preview_comment',
            'comments_disabled',
            'taken_at_timestamp',
            'edge_media_preview_like',
            'edge_media_sponsor_user',
            'location',
            'location.id',
            'owner.username',
            'owner.id',
            'is_ad',
            'edge_web_media_to_related_media',
        ]

        try:
            for entry in POST_ELEMENTS:
                loader.add_value(entry.replace('.', '_'), deep_dict_get(data, entry))
        except TypeError:
            pass

        loader.add_value('post_json', data)
        loader.add_value('retrieved_at_time', int(time.time()))
        loader.add_value('image_urls', data.get('display_url'))
        return loader

    def parse(self, response):

        ig_post_dict = ig_extract_shared_data(response=response, category="post")
        ig_post = IGLoader(item=IGPost(), response=response)
        ig_post = self._parse_post(loader=ig_post, data=ig_post_dict)

        yield ig_post.load_item()

    def errback(self, failure):
        self.logger.debug(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                post = response.url.split('/')[-2:-1][0]
                self.set_entity_deleted(post)