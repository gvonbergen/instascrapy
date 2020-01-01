# -*- coding: utf-8 -*-
import json
import random
import time

import scrapy
import boto3
from scrapy.loader import ItemLoader

from instascrapy.db import DynDB
from instascrapy.helpers import get_proxies, read_post_shortcodes
from instascrapy.items import IGUser


class IguserSpider(scrapy.Spider):
    name = 'iguser'

    def start_requests(self):
        db = DynDB(table='instalytics_dev', region_name='eu-central-1')
        proxy_list = get_proxies()
        all_users = db.get_all_users('GSI1')
        for user in all_users:
            url = 'https://www.instagram.com/{}/'.format(user)
            header_proxy = random.choice(proxy_list)
            yield scrapy.Request(url=url, callback=self.parse,
                                 headers={'User-Agent': header_proxy[1]},
                                 meta={"proxy": header_proxy[0]})

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]')\
                                 .re('window._sharedData = (.+?);</script>')[0])
        user = json_object['entry_data']['ProfilePage'][0]['graphql']['user']

        ig_user = ItemLoader(item=IGUser(), response=response)

        first_level_items = ['biography', 'external_url', 'external_url_linkshimmed', 'full_name', 'has_channel',
                             'highlight_reel_count', 'id', 'is_business_account', 'is_joined_recently',
                             'business_category_name', 'is_private', 'is_verified', 'profile_pic_url',
                             'profile_pic_url_hd', 'username', 'connected_fb_page']
        for entry in first_level_items:
            ig_user.add_value(entry, user.get(entry))

        ig_user.add_value('edge_followed_by_count', user['edge_followed_by']['count'])
        ig_user.add_value('edge_follow_count', user['edge_follow']['count'])
        ig_user.add_value('latest_posts', [post['node']['shortcode'] for post in
                                           user['edge_owner_to_timeline_media']['edges']])
        ig_user.add_value('user_json', user)
        ig_user.add_value('retrieved_at_time', int(time.time()))

        return ig_user.load_item()

