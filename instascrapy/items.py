# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import time
from decimal import Decimal
from typing import Any, List, Dict

import scrapy
import scrapy.loader
from scrapy.loader.processors import TakeFirst, Compose

from instascrapy.settings import REMOVAL_JSON_USER_FIELDS


def list_remove_empty_values(values, blacklist=None):
    """Removes empty/none values from a list and ignores boolean (False), integers (e.g. 0)
    and float (e.g. 0.0)"""
    for idx, v in enumerate(values):
        if isinstance(v, dict):
            values[idx] = dict_remove_values(v, blacklist)
        if isinstance(v, list):
            values[idx] = list_remove_empty_values(v, blacklist)
        if not isinstance(v, (bool, int, float)) and not v:
            values.remove(v)
    return values


def dict_remove_values(values, blacklist=None):
    """Removes blacklisted empty/none values from a dictionary and ignores boolean (False), integers (e.g. 0)
    and float (e.g. 0.0)"""
    if blacklist is None:
        blacklist = []
    values_copy = values.copy()
    for k, v in values.items():
        if k in blacklist:
            del values_copy[k]
            continue
        if isinstance(v, dict):
            values_copy[k] = dict_remove_values(v, blacklist)
        if isinstance(v, list):
            values_copy[k] = list_remove_empty_values(v, blacklist)
        if isinstance(v, float):
            values_copy[k] = round(Decimal(v), 2)
            continue
        if not isinstance(v, (bool, int, float)) and not v:
            del values_copy[k]
    return values_copy


def remove_key_values(values, removal_list):
    output = {}
    for key, value in values.items():
        if key not in removal_list:
            output[key] = value
    return output


def remove_user_key_values(values):
    blacklist = REMOVAL_JSON_USER_FIELDS
    return dict_remove_values(values, blacklist)


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
