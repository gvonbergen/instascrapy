# -*- coding: utf-8 -*-
import json
import random
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from instascrapy.db import DynDB
from instascrapy.helpers import get_proxies, read_post_shortcodes
from instascrapy.items import IGUser, IGLoader


class IguserSpider(scrapy.Spider):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DynDB(table='instalytics_dev', region_name='eu-central-1')

    name = 'iguser'

    def start_requests(self):
        proxy_list = get_proxies()
        all_users = self.db.get_all_users('GSI1')
        for user in all_users:
            url = 'https://www.instagram.com/{}/'.format(user)
            header_proxy = random.choice(proxy_list)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback,
                                 headers={'User-Agent': header_proxy[1]},
                                 meta={"proxy": header_proxy[0]})

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]')\
                                 .re('window._sharedData = (.+?);</script>')[0])
        user = json_object['entry_data']['ProfilePage'][0]['graphql']['user']

        ig_user = IGLoader(item=IGUser(), response=response)

        first_level_items = ['biography', 'external_url', 'external_url_linkshimmed', 'full_name', 'has_channel',
                             'highlight_reel_count', 'id', 'is_business_account', 'is_joined_recently',
                             'business_category_name', 'is_private', 'is_verified', 'profile_pic_url',
                             'profile_pic_url_hd', 'username', 'connected_fb_page']
        for entry in first_level_items:
            ig_user.add_value(entry, user.get(entry))

        ig_user.add_value('edge_followed_by_count', user['edge_followed_by']['count'])
        ig_user.add_value('edge_follow_count', user['edge_follow']['count'])
        # TODO: Adde latest posts to seperate Post Item or handle it differently
        ig_user.add_value('last_posts', [post['node']['shortcode'] for post in
                                         user['edge_owner_to_timeline_media']['edges']])
        ig_user.add_value('user_json', user)
        ig_user.add_value('retrieved_at_time', int(time.time()))

        yield ig_user.load_item()

        # TODO: Follow Weblink an index further details

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
                username = response.url.split('/')[-2:-1][0]
                self.db.set_entity_deleted(username)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.debug('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.debug('TimeoutError on %s', request.url)