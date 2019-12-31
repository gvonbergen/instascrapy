# -*- coding: utf-8 -*-
import json
import time

import scrapy
import boto3

from instascrapy.db import DynDB


class IguserSpider(scrapy.Spider):
    name = 'iguser'

    def start_requests(self):
        db = DynDB(table='instalytics_dev', region_name='eu-central-1')
        all_users = db.get_all_users('GSI1')
        for user in all_users:
            url = 'https://www.instagram.com/{}/'.format(user)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        json_object = json.loads(response.xpath('//script[@type="text/javascript"]')\
                                 .re('window._sharedData = (.+?);</script>')[0])
        user = json_object['entry_data']['ProfilePage'][0]['graphql']['user']

        yield {
            'pk': 'US#' + user['username'],
            'sk': 'US#UPDA#V1' + time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            'id': user['id'],
            'retrieved_at_time': int(time.time()),
            'json': user
        }
