# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from instascrapy.items import IGLoader, IGPost
from instascrapy.spider import DynDBSpider


class IgpostSpider(DynDBSpider):
    name = 'igpost'

    def start_requests(self):
        # Todo: Get only those that have not yet been retrieved (maybe with a new search index)
        all_posts = self.db.get_category_all('POST', 'GSI1')
        # all_posts = ['B6vfD0QJ1O-', 'B7L9oCipfWo']
        for post in all_posts:
            url = 'https://www.instagram.com/p/{}'.format(post)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]') \
                                 .re('window._sharedData = (.+?);</script>')[0])
        post = json_object['entry_data']['PostPage'][0]['graphql']['shortcode_media']

        ig_post = IGLoader(item=IGPost(), response=response)
        keys = list(ig_post.item.fields.keys())
        keys_to_delete = ['owner', 'retrieved_at_time', 'image_urls', 'images']
        for k in keys_to_delete:
            keys.remove(k)
        for k in keys:
            try:
                ig_post.add_value(k, post[k])
            except KeyError:
                pass
        ig_post.add_value('owner', post['owner']['username'])
        ig_post.add_value('owner_id', post['owner']['id'])
        try:
            ig_post.add_value('location_id', post['location']['id'])
        except TypeError:
            pass
        ig_post.add_value('post_json', post)
        ig_post.add_value('retrieved_at_time', int(time.time()))
        ig_post.add_value('image_urls', post.get('display_url'))

        yield ig_post.load_item()

    def errback(self, failure):
        self.logger.debug(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                post = response.url.split('/')[-2:-1][0]
                self.db.set_entity_deleted('POST', post)
            else:
                request = failure.request
                self.logger.debug('Error on %s', request.url)