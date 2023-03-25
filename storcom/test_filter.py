import pytest

from storcom import filter as flt

def test_supported_fcc_filters() -> None:
    assert flt.FCC_FILTER_FIELDS == ['batch']

def test_to_fcc_qs_params_ignores_unsupported_filters() -> None:
    assert not flt.to_fcc_qs_params({'smth': 'eq 2'})

@pytest.mark.parametrize('value', ['eq test', 'eq "test"', "eq 'test'"])
def test_to_fcc_qs_params_supports_eq_text_values(value: str) -> None:
    assert flt.to_fcc_qs_params({'batch': value}) == {'batch': 'test'}

@pytest.mark.parametrize('value', ['eq 42', 'eq "42"', "eq '42'"])
def test_to_fcc_qs_params_supports_eq_number_values(value: str) -> None:
    assert flt.to_fcc_qs_params({'batch': value}) == {'batch': '42'}

# TODO: none tests line {'batch': None}
# TODO: add default eq filter tests
# TODO: case tests for EQ vs eq
