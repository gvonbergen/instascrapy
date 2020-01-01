# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import time
from typing import Any

import scrapy
from scrapy.loader.processors import TakeFirst


def list_string_to_integer(value):
    return [int(entry) for entry in value]

class IGUser(scrapy.Item):
    biography = scrapy.Field(output_processor=TakeFirst())
    external_url = scrapy.Field(output_processor=TakeFirst())
    external_url_linkshimmed = scrapy.Field(output_processor=TakeFirst())
    edge_followed_by_count = scrapy.Field(output_processor=TakeFirst())
    edge_follow_count = scrapy.Field(output_processor=TakeFirst())
    full_name = scrapy.Field(output_processor=TakeFirst())
    has_channel = scrapy.Field(output_processor=TakeFirst())
    highlight_reel_count = scrapy.Field(output_processor=TakeFirst())
    id = scrapy.Field(serializer=int, output_processor=TakeFirst())
    is_business_account = scrapy.Field(output_processor=TakeFirst())
    is_joined_recently = scrapy.Field(output_processor=TakeFirst())
    business_category_name = scrapy.Field(output_processor=TakeFirst())
    is_private = scrapy.Field(output_processor=TakeFirst())
    is_verified = scrapy.Field(output_processor=TakeFirst())
    profile_pic_url = scrapy.Field(output_processor=TakeFirst())
    profile_pic_url_hd = scrapy.Field(output_processor=TakeFirst())
    username = scrapy.Field(output_processor=TakeFirst())
    connected_fb_page = scrapy.Field(output_processor=TakeFirst())
    latest_posts = scrapy.Field(output_processor=TakeFirst())
    retrieved_at_time = scrapy.Field(output_processor=TakeFirst())
    user_json = scrapy.Field(output_processor=TakeFirst())
