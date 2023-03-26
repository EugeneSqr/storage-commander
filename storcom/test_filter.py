import pytest

from storcom import filter as flt

def test_supported_fcc_filters() -> None:
    assert flt.FCC_FILTER_FIELDS == ['batch']

def test_to_fcc_qs_params_ignores_unsupported_filters() -> None:
    assert not flt.to_fcc_qs_params({'smth': 'eq 2'})

def test_to_fcc_qs_params_ignores_empty_filters() -> None:
    assert not flt.to_fcc_qs_params({'batch': ''})

@pytest.mark.parametrize('actual,expected', [
    ('eq test', 'test'),
    ('eq "0"', '0'),
    ("eq 'this is test'", 'this is test'),
])
def test_to_fcc_qs_params_eq_operator(actual: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': actual}) == {'batch': expected}

@pytest.mark.parametrize('actual,expected', {
    ('test', 'test'),
    ('"0"', '0'),
    ("eq 'this is test'", 'this is test'),
})
def test_to_fcc_qs_params_default_eq_operator(actual: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': actual}) == {'batch': expected}

def test_to_fcc_qs_params_operator_case_insensitive() -> None:
    assert flt.to_fcc_qs_params({'batch': 'EQ 3'}) == {'batch': '3'}
