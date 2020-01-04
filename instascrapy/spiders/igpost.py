# -*- coding: utf-8 -*-
import scrapy

from instascrapy.db import DynDB
from instascrapy.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class IgpostSpider(scrapy.Spider):

    name = 'igpost'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DynDB(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, table='instalytics_dev', region_name='eu-central-1')


    def start_requests(self):
        all_posts = self.db.get_category_all('POST', 'GSI1')
        for post in all_posts:
            url = 'https://www.instagram.com/p/{}'.format(post)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response):
        test = response
        pass

    def errback(self, failure):
        pass