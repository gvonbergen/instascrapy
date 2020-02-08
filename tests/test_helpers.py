"""This file tests all the helper functions"""
import pytest

from instascrapy.helpers import deep_dict_get


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
