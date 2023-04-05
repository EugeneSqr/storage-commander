from typing import Optional, Tuple

import pytest

from storcom import filter as flt
from storcom.errors import FilterError

def test_supported_fcc_filters() -> None:
    assert [f.field for f in flt.get_fcc_filters()] == ['batch', 'date_changed', 'date_created']

def test_to_fcc_qs_params_ignores_unsupported_filters() -> None:
    assert not flt.to_fcc_qs_params({'smth': 'eq 2'})

@pytest.mark.parametrize('empty', ['', None])
def test_to_fcc_qs_params_ignores_empty_single_filters(empty: Optional[str]) -> None:
    assert not flt.to_fcc_qs_params({'batch': empty})

@pytest.mark.parametrize('empty', [(), None])
def test_to_fcc_qs_params_ignores_empty_multiple_filters(empty: Optional[Tuple[str]]) -> None:
    assert not flt.to_fcc_qs_params({'date_changed': empty})

@pytest.mark.parametrize('provided, expected', [
    ('eq test', 'test'),
    ('eq "0"', '0'),
    ("eq 'this is test'", 'this is test'),
])
def test_to_fcc_qs_params_eq_operator(provided: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': provided}) == {'batch': expected}

@pytest.mark.parametrize('provided, expected', {
    ('test', 'test'),
    ('"0"', '0'),
    ("eq 'this is test'", 'this is test'),
})
def test_to_fcc_qs_params_default_eq_operator(provided: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'batch': provided}) == {'batch': expected}

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

@pytest.mark.parametrize('invalid_value', [('test',), ('123',)])
def test_to_fcc_qs_params_datetime_invalid_value_raises_error(invalid_value: Tuple[str]) -> None:
    with pytest.raises(FilterError):
        flt.to_fcc_qs_params({'date_changed': invalid_value})

# TODO: fix multiple
@pytest.mark.parametrize('provided, expected', {
    ('2023-01-01', '2023-01-01 00:00:00')
})
def test_to_fcc_qs_params_datetime_partial_datetime_is_ok(provided: str, expected: str) -> None:
    assert flt.to_fcc_qs_params({'date_changed': provided}) == {'date_changed': expected}

# TODO: fix_multiple
def test_to_fcc_qs_params_datetime_full_is_ok() -> None:
    actual = flt.to_fcc_qs_params({'date_changed': '2023-02-14T10:09:07.060011Z'})
    assert actual == {'date_changed': '2023-02-14 10:09:07.060011+00:00'}
