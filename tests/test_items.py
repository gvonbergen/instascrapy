import time
from decimal import Decimal

import pytest
from instascrapy.items import dict_remove_values, IGLoader, IGUser, IGPost

REMOVAL_JSON_USER_FIELDS = {'to_be_deleted'}

def test_remove_empty_values():
    input = {
        'string_empty': '', # False
        'string_filled': 'Test String', # True
        'boolean_false': False, # False -> needed
        'boolean_true': True, # True
        'list_empty': [], # False
        'list_filled': ['Test List'], # True
        'list_nested': ['Test 1', '', True, 'Test 2'],
        'dict_empty': {}, # False
        'dict_filled': {'a': 'test'}, # True
        'dict_nested': {'string_empty': '',
                        'boolean_false': False,
                        'dict_empty': {},
                        'int_value': 100,
                        'deep_nested': {'string_value': '',
                                        'int_value': 100,
                                        'to_be_deleted': {'value 1': 1,
                                                          'value 2': 2}}},
        'int_zero': 0, # False -> needed
        'int_value': 100, # True
        'float_zero': 0.0, # False -> needed
        'float_value': 100.004645489878465153, # True
        'none': None, # False
        'edge_owner_to_timeline_media': {'edges': [{'node': {'location': {'id': 123455,
                                                                          'slug': '',
                                                                          'to_be_deleted': 200}}}]}
    }
    result = dict_remove_values(input, REMOVAL_JSON_USER_FIELDS)
    assert result['string_filled'] == 'Test String'
    assert result['boolean_false'] == False
    assert result['boolean_true'] == True
    assert result['list_filled'] == ['Test List']
    assert result['list_nested'] == ['Test 1', True, 'Test 2']
    assert result['dict_filled'] ==  {'a': 'test'}
    assert result['dict_nested'] == {'boolean_false': False, 'int_value': 100, 'deep_nested': {'int_value': 100}}
    assert result['int_zero'] == 0
    assert result['int_value'] == 100
    assert result['float_zero'] == 0.0
    # assert result['float_value'] == Decimal(100.00)
    assert result['edge_owner_to_timeline_media'] == {'edges': [{'node': {'location': {'id': 123455}}}]}
    with pytest.raises(KeyError):
        for key in ['string_empty', 'list_empty', 'dict_empty', 'none']:
            result[key]
    assert len(result) == 12


class TestIGUser:
    @pytest.fixture(scope="function")
    def iguser_scrapy_item(self):
        loader = IGLoader(item=IGUser())
        loader.add_value("username", "testuser")
        loader.add_value("id", "12345")
        loader.add_value("id", "111")
        loader.add_value("last_posts", "XAB")
        loader.add_value("last_posts", "XBB")
        loader.add_value("retrieved_at_time", time.time())
        loader.add_value("user_json", {"biography": "My Biography",
                                       "external_url": "https://www.test.ch/",
                                       "edge_followed_by": {"count": 4}}
                         )

        return loader.load_item()

    def test_user_username_string(self, iguser_scrapy_item):
        username = iguser_scrapy_item.get("username")
        assert isinstance(username, str)

    def test_user_id_integer(self, iguser_scrapy_item):
        user_id = iguser_scrapy_item.get("id")
        assert isinstance(user_id, int)

    def test_user_id_5digits(self, iguser_scrapy_item):
        user_id = iguser_scrapy_item.get("id")
        assert user_id == 12345

    def test_user_last_posts_dict(self, iguser_scrapy_item):
        last_posts = iguser_scrapy_item.get("last_posts")
        assert isinstance(last_posts, list)

    def test_user_last_posts_values(self, iguser_scrapy_item):
        last_posts = iguser_scrapy_item.get("last_posts")
        assert last_posts == ["XAB", "XBB"]

    def test_user_retrieved_time_integer(self, iguser_scrapy_item):
        retrieved_time = iguser_scrapy_item.get("retrieved_at_time")
        assert isinstance(retrieved_time, int)

    def test_user_json_dict(self, iguser_scrapy_item):
        user_json = iguser_scrapy_item.get("user_json")
        assert isinstance(user_json, dict)


class TestIGPost:
    @pytest.fixture(scope="function")
    def igpost_scrapy_item(self):
        loader = IGLoader(item=IGPost())
        loader.add_value("shortcode", "AAA")
        loader.add_value("shortcode", "BBB")
        loader.add_value("owner_username", "testuser")
        loader.add_value("owner_username", "testuser2")
        loader.add_value("owner_id", "12345")
        loader.add_value("owner_id", "111")
        loader.add_value("id", "12345")
        loader.add_value("id", 123)
        loader.add_value("post_json", {"biography": "My Biography",
                                       "external_url": "https://www.test.ch/",
                                       "edge_followed_by": {"count": 4}}
                         )

        return loader.load_item()

    def test_post_shortcode_string(self, igpost_scrapy_item):
        shortcode = igpost_scrapy_item.get("shortcode")
        assert shortcode == "AAA"

    def test_post_owner_username_string(self, igpost_scrapy_item):
        username = igpost_scrapy_item.get("owner_username")
        assert username == "testuser"

    def test_post_owner_id_integer(self, igpost_scrapy_item):
        owner_id = igpost_scrapy_item.get("owner_id")
        assert owner_id == 12345

    def test_post_id_integer(self, igpost_scrapy_item):
        post_id = igpost_scrapy_item.get("id")
        assert post_id == 12345

    def test_post_json_dict(self, igpost_scrapy_item):
        post_json = igpost_scrapy_item.get("post_json")
        assert isinstance(post_json, dict)