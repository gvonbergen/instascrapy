# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from instascrapy.db import DynDB
from instascrapy.items import IGLoader, IGLocation
from instascrapy.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class IglocationSpider(scrapy.Spider):
    name = 'iglocation'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DynDB(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, table='instalytics_dev', region_name='eu-central-1')

    def start_requests(self):
        all_locations = ['1011353671']
        for location in all_locations:
            url = 'https://www.instagram.com/explore/locations/{}/'.format(location)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]') \
                                 .re('window._sharedData = (.+?);</script>')[0])
        location = json_object['entry_data']['LocationsPage'][0]['graphql']['location']

        ig_location = IGLoader(item=IGLocation(), response=response)
        keys = list(ig_location.item.fields.keys())
        for k in keys:
            try:
                ig_location.add_value(k, location[k])
            except KeyError:
                pass

        ig_location.add_value('location_json', location)
        ig_location.add_value('retrieved_at_time', int(time.time()))
        ig_location.add_value('edge_location_to_media_count', location['edge_location_to_media']['count'])
        ig_location.add_value('last_posts', [post['node']['shortcode'] for post in
                                             location['edge_location_to_media']['edges']])

        yield ig_location.load_item()

    def errback(self, failure):
        self.logger.debug(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                location = response.url.split('/')[-2:-1][0]
                self.db.set_entity_deleted('LOCATION', location)
            else:
                request = failure.request
                self.logger.debug('Error on %s', request.url)