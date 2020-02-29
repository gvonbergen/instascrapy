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
    """Retrieve entities which are not yet downloaded"""
    users = list(user_spider.get_entities('USER'))
    assert users == ['test1', 'test2']


def test_get_entity_user_including_downloaded(user_spider):
    """Retrieve entities which have already been downloaded but are not deleted"""
    users = list(user_spider.get_entities('USER', get_retrieved=True))
    assert users == ['test1', 'test2', 'user4']


def test_set_entity_deleted(user_spider):
    """Standard test to verify if attribute is set to deleted=True"""
    user_spider.set_entity_deleted('test2')
    deleted_user = user_spider.coll.find_one({'pk': 'US#test2', 'sk': 'USER'})
    assert deleted_user['deleted'] == True


def test_set_entity_deleted_xcheck(user_spider):
    """Test verifies that only one item is set to delete and not both"""
    user_spider.set_entity_deleted('test1')
    xcheck_user = user_spider.coll.find_one({'pk': 'US#test2', 'sk': 'USER'})
    with pytest.raises(KeyError):
        assert xcheck_user['deleted']


def test_set_entity_deleted_not_existent(user_spider):
    """Test to verify behavior when non existent key is updated"""
    not_existent = user_spider.coll.find_one({'pk': 'US#test0', 'sk': 'USER'})
    assert not_existent is None
    user_spider.set_entity_deleted('test0', 123)
    not_existent = user_spider.coll.find_one({'pk': 'US#test0', 'sk': 'USER'})
    not_existent.pop('_id')
    assert not_existent == {'pk': 'US#test0', 'sk': 'USER', 'deleted': True, 'deleted_at_time': 123}


def test_set_entity_already_deleted(user_spider):
    """Verifies that the state doesn't change if there is a deleted entity"""
    result = user_spider.coll.find_one({'pk': 'US#test3', 'sk': 'USER'})
    assert result['deleted'] == True
    user_spider.set_entity_deleted('test3', 123)
    result2 = user_spider.coll.find_one({'pk': 'US#test3', 'sk': 'USER'})
    assert result == result2


def test_file_read_no_prefix(datadir):
    """Test if file is read correctly when provided in command line"""
    spider = IguserSpider()
    spider.file = datadir / 'users.json'
    users = spider.read_file()
    assert isinstance(users, list)
    assert users == ['user1', 'user2']
