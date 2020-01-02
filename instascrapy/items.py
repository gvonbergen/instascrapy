# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import time
from typing import Any, List, Dict

import scrapy
import scrapy.loader
from scrapy.loader.processors import TakeFirst, Compose

from instascrapy.settings import REMOVAL_JSON_USER_FIELDS


def remove_empty_values(values):
    """Removes None/empy/zero values from a dictionary"""
    return {k: v for k, v in values.items() if v}

def remove_key_values(values, removal_list):
    output = {}
    for key, value in values.items():
        if key not in removal_list and value is not None:
            output[key] = value
    return output

def remove_user_key_values(values):
    removal_list = REMOVAL_JSON_USER_FIELDS
    return remove_key_values(values, removal_list)


class IGLoader(scrapy.loader.ItemLoader):
    default_output_processor = TakeFirst()

    user_json_out = Compose(TakeFirst(),
                            remove_user_key_values)


class IGUser(scrapy.Item):
    biography = scrapy.Field()
    external_url = scrapy.Field()
    external_url_linkshimmed = scrapy.Field()
    edge_followed_by_count = scrapy.Field()
    edge_follow_count = scrapy.Field()
    full_name = scrapy.Field()
    has_channel = scrapy.Field()
    highlight_reel_count = scrapy.Field()
    id = scrapy.Field(serializer=int)
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
    retrieved_at_time = scrapy.Field()
    user_json = scrapy.Field()
