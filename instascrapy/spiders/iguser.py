# -*- coding: utf-8 -*-
import scrapy


class IguserSpider(scrapy.Spider):
    name = 'iguser'
    allowed_domains = ['instgram.com']
    start_urls = ['http://instgram.com/']

    def parse(self, response):
        pass
