"""This file tests all the helper functions"""
import pytest

from instascrapy.helpers import deep_dict_get, secondary_key_update


@pytest.fixture()
def nested_dict_sample():
    nested_dict = {
        'a': {
            'b': {
                'c': 'string',
                'd': 6,
                'e': {'ea': 'eb'},
                'f': ['fa', 'fb']
            }
        }
    }
    return nested_dict


def test_nested_dict_flat(nested_dict_sample):
    result = deep_dict_get(nested_dict_sample, 'a')
    assert isinstance(result, dict)


def test_nested_dict_str(nested_dict_sample):
    result = deep_dict_get(nested_dict_sample, 'a.b.c')
    assert result == 'string'


def test_nested_dict_int(nested_dict_sample):
    result = deep_dict_get(nested_dict_sample, 'a.b.d')
    assert result == 6


def test_nested_dict_dictionary(nested_dict_sample):
    result = deep_dict_get(nested_dict_sample, 'a.b.e')
    assert isinstance(result, dict)


def test_nested_dict_list(nested_dict_sample):
    result = deep_dict_get(nested_dict_sample, 'a.b.f')
    assert isinstance(result, list)


def test_secondary_key_update():
    sk = secondary_key_update("US#", 1582488023)
    assert sk == "US#UPDA#V1#2020-02-23T21:00:23"

def test_secondary_key_update_string():
    sk = secondary_key_update("US#", 2792884137)
    assert isinstance(sk, str)