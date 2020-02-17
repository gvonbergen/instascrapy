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


def test_set_entity_deleted(user_spider):
    """Standard test to verify if attribute is set to deleted=True"""
    user_spider.set_entity_deleted('test2', 'US#')
    deleted_user = user_spider.coll.find_one({'pk': 'US#test2'})
    assert deleted_user['deleted'] == True


def test_set_entity_deleted_xcheck(user_spider):
    """Test verifies that only one item is set to delete and not both"""
    user_spider.set_entity_deleted('test1', 'US#')
    xcheck_user = user_spider.coll.find_one({'pk': 'US#test2'})
    with pytest.raises(KeyError):
        assert xcheck_user['deleted']


def test_set_entity_deleted_not_existent(user_spider):
    """Test to verify behavior when non existent key is updated"""
    user_spider.set_entity_deleted('test0', 'US#')
    not_existent = user_spider.coll.find_one({'pk': 'US#test0'})
    assert not_existent == None