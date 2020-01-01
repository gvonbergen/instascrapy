# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IGUser(scrapy.Item):
    biography = scrapy.Field()
    external_url = scrapy.Field()
    external_url_linkshimmed = scrapy.Field()
    edge_followed_by_count = scrapy.Field()
    edge_follow_count = scrapy.Field()
    full_name = scrapy.Field()
    has_channel = scrapy.Field()
    highlight_reel_count = scrapy.Field()
    id = scrapy.Field()
    is_business_account = scrapy.Field()
    is_joined_recently = scrapy.Field()
    business_category_name = scrapy.Field()
    is_private = scrapy.Field()
    is_verified = scrapy.Field()
    profile_pic_url = scrapy.Field()
    profile_pic_url_hd = scrapy.Field()
    username = scrapy.Field()
    connected_fb_page = scrapy.Field()
    latest_posts = scrapy.Field()



class InstascrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
