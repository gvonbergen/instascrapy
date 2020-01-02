import pytest
from instascrapy.items import remove_empty_values


def test_remove_empty_values():
    input = {
        'string_empty': '', # False
        'string_filled': 'Test String', # True
        'boolean_false': False, # False -> needed
        'boolean_true': True, # True
        'list_empty': [], # False
        'list_filled': ['Test List'], # True
        'dict_empty': {}, # False
        'dict_filled': {'a': 'test'}, # True
        'int_zero': 0, # False -> needed
        'int_value': 100, # True
        'float_zero': 0.0, # False -> needed
        'float_value': 100.0, # True
        'none': None # False
    }
    result = remove_empty_values(input)
    assert result['string_filled'] == 'Test String'
    assert result['boolean_false'] == False
    assert result['boolean_true'] == True
    assert result['list_filled'] == ['Test List']
    assert result['dict_filled'] ==  {'a': 'test'}
    assert result['int_zero'] == 0
    assert result['int_value'] == 100
    assert result['float_zero'] == 0.0
    assert result['float_value'] == 100.0
    for key in ['string_empty', 'list_empty', 'dict_empty', 'none']:
        with pytest.raises(KeyError):
            result[key]
    assert len(result) == 9