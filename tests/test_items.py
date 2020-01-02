import pytest
from instascrapy.items import dict_remove_empty_values

{}

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
                                        'int_value': 100}},
        'int_zero': 0, # False -> needed
        'int_value': 100, # True
        'float_zero': 0.0, # False -> needed
        'float_value': 100.0, # True
        'none': None, # False
        'edge_owner_to_timeline_media': {'edges': [{'node': {'location': {'id': 123455, 'slug': ''}}}]}
    }
    result = dict_remove_empty_values(input)
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
    assert result['float_value'] == 100.0
    assert result['edge_owner_to_timeline_media'] == {'edges': [{'node': {'location': {'id': 123455}}}]}
    with pytest.raises(KeyError):
        for key in ['string_empty', 'list_empty', 'dict_empty', 'none']:
            result[key]
    assert len(result) == 12