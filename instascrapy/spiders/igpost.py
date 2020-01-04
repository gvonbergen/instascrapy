# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from instascrapy.db import DynDB
from instascrapy.items import IGLoader, IGUser, IGPost
from instascrapy.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class IgpostSpider(scrapy.Spider):

    name = 'igpost'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DynDB(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, table='instalytics_dev', region_name='eu-central-1')


    def start_requests(self):
        all_posts = self.db.get_category_all('POST', 'GSI1')
        all_posts = ['-L2WwkSDeq']
        for post in all_posts:
            url = 'https://www.instagram.com/p/{}'.format(post)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]') \
                                 .re('window._sharedData = (.+?);</script>')[0])
        post = json_object['entry_data']['PostPage'][0]['graphql']['shortcode_media']

        ig_post = IGLoader(item=IGPost(), response=response)
        keys = ig_post.item.fields.keys()
        for k in keys:
            try:
                ig_post.add_value(k, post[k])
            except KeyError:
                pass
        ig_post.add_value('post_json', post)
        ig_post.add_value('retrieved_at_time', int(time.time()))
        ig_post.add_value('image_urls', post.get('display_url'))

        yield ig_post.load_item()

    def errback(self, failure):
        # log all failures
        self.logger.debug(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.debug('HttpError on %s', response.url)
            if response.status == 404:
                # username = response.url.split('/')[-2:-1][0]
                # self.db.set_entity_deleted(username)