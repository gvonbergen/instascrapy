""" This file includes helper functions """
import itertools
import random

from instascrapy.settings import PROXY_LIST

def get_random_useragent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)'
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
