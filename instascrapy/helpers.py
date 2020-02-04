""" This file includes helper functions """
import itertools
import re
import json
import random
from typing import List

from instascrapy.settings import PROXY_LIST

IG_JSON_LOCATION = re.compile('window._sharedData = (.+?);</script>')

def ig_extract_shared_data(response, category=None) -> dict:
    """
    Function returns a dictionary with the entity information from Instagram
    :param response: HTML response as string
    :return: parsed entity meta data as dictionary or shared_data
    """
    shared_data = json.loads(IG_JSON_LOCATION.findall(response.text)[0])
    if category == 'user':
        return shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
    elif category == 'post':
        return shared_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
    elif category == 'location':
        return shared_data['entry_data']['LocationsPage'][0]['graphql']['location']
    else:
        return shared_data


def get_random_useragent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/71.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/71.0',
        'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/71.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 Edg/44.18362.449.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 OPR/65.0.3467.78',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 OPR/65.0.3467.78',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 OPR/65.0.3467.78'
    ]
    return random.choice(user_agents)


def get_proxies():
    proxy_list = []
    for proxy in PROXY_LIST:
        proxy_value = proxy.split(':')
        if len(proxy_value) == 3:
            ip, start_value, end_value = proxy_value
            for port in range(int(start_value), int(end_value) + 1):
                proxy_list.append(('{}:{}'.format(ip, port), get_random_useragent()))

    return proxy_list


def read_post_shortcodes(user_json) -> None or List:
    """
    Returns a list of the last 12 shortcodes included in the user profile
    :param user_json: ['entry_data']['ProfilePage'][0]['graphql']['user'] JSON input
    :return: None or a list with Shortcodes
    """
    if user_json['is_private']:
        return None
    else:
        return [post['node']['shortcode'] for post in user_json['edge_owner_to_timeline_media']['edges']]
