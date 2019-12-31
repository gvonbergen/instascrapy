# -*- coding: utf-8 -*-
import scrapy


class IgpostSpider(scrapy.Spider):
    name = 'igpost'
    allowed_domains = ['instgram.com']
    start_urls = ['http://instgram.com/']

    def parse(self, response):
        pass
