import pytest

from storcom import filter as flt
from storcom.errors import FilterError

def test_supported_fcc_filters() -> None:
    assert flt.FCC_FILTER_FIELDS == ['batch', 'date_changed', 'date_created']

def test_to_fcc_qs_params_ignores_unsupported_filters() -> None:
    assert not flt.to_fcc_qs_params({'smth': 'eq 2'})

def test_to_fcc_qs_params_ignores_empty_filters() -> None:
    assert not flt.to_fcc_qs_params({'batch': ''})

@pytest.mark.parametrize('actual, expected', [
    ('eq test', 'test'),
    ('eq "0"', '0'),
    ("eq 'this is test'", 'this is test'),
])
def test_to_fcc_qs_params_eq_operator(actual: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': actual}) == {'batch': expected}

@pytest.mark.parametrize('actual, expected', {
    ('test', 'test'),
    ('"0"', '0'),
    ("eq 'this is test'", 'this is test'),
})
def test_to_fcc_qs_params_default_eq_operator(actual: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': actual}) == {'batch': expected}

@pytest.mark.parametrize('operator', ['lt', 'gt', 'lte', 'gte'])
def test_to_fcc_qs_params_other_operators(operator: str) -> None:
    assert flt.to_fcc_qs_params({'batch': f'{operator} 3'}) == {f'batch__{operator}': '3'}

def test_to_fcc_qs_params_not_supported_operator_throws_filter_error() -> None:
    with pytest.raises(FilterError):
        flt.to_fcc_qs_params({'batch': 'unsupported_operator 2'})

def test_to_fcc_qs_params_eq_operator_case_insensitive() -> None:
    assert flt.to_fcc_qs_params({'batch': 'EQ 3'}) == {'batch': '3'}

@pytest.mark.parametrize('operator', ['Lt', 'gT', 'lTe', 'gTE'])
def test_to_fcc_qs_params_other_operators_case_insensitive(operator: str) -> None:
    actual = flt.to_fcc_qs_params({'batch': f'{operator} test'})
    assert actual == {f'batch__{operator.lower()}': 'test'}
