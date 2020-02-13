import json

import pytest
import requests
import requests_mock

from instascrapy.helpers import ig_extract_shared_data
from instascrapy.items import IGLoader, IGUser
from instascrapy.spiders.iguser import IguserSpider


@pytest.fixture()
def ig_user_html(datadir):
    user_html = (datadir / '0livierjordan18.html').read_text()
    user_dict = json.loads((datadir / '0livierjordan18.json').read_text())
    user_result = json.loads((datadir / '0livierjordan18.result').read_text())
    return user_html, user_dict, user_result


def test_extract_shared_data_user(ig_user_html):
    user_html, user_dict, _ = ig_user_html
    with requests_mock.mock() as m:
        m.get('ig://0livierjordan18', text=user_html)
        response = requests.get('ig://0livierjordan18')
    user_json = ig_extract_shared_data(response=response, category='user')
    assert user_json == user_dict


def test_parse_user(ig_user_html):
    _, user_dict, user_result = ig_user_html
    loader = IGLoader(item=IGUser())
    spider = IguserSpider()
    ig_user = spider._parse_user(loader, user_dict)
    for k in ig_user._values.keys():
        if k != 'retrieved_at_time':
            assert ig_user.get_output_value(k) == user_result[k]


@pytest.fixture()
def user_spider(mongodb):
    spider = IguserSpider()
    spider.db = mongodb
    spider.coll = mongodb.user
    return spider


def test_get_entity_user(user_spider):
    users = list(user_spider.get_entities('USER'))
    assert users == ['test1', 'test2']