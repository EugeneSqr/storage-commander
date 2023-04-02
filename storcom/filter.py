from typing import Dict, Tuple

from dateutil.parser import isoparse

from storcom.errors import FilterError

FCC_FILTER_FIELDS = ['batch', 'date_changed', 'date_created']

_FCC_OPERATORS = ['eq', 'lt', 'gt', 'lte', 'gte']

def to_fcc_qs_params(filters: Dict[str, str]) -> Dict[str, str]:
    return dict(_to_fcc_qs_param(k, v) for k, v in filters.items() if v and k in FCC_FILTER_FIELDS)

def _to_fcc_qs_param(filter_field: str, filter_value: str) -> Tuple[str, str]:
    split_filter_value = filter_value.split(' ', 1)
    param_operator, param_value = 'eq', ''
    if len(split_filter_value) == 1:
        param_value = split_filter_value[0]
    else:
        param_operator, param_value = split_filter_value
    return _to_fcc_filter_expression(filter_field, param_operator, param_value)

def _to_fcc_filter_expression(field: str, operator: str, value: str) -> Tuple[str, str]:
    operator = operator.lower()
    value = value.strip('\'"')
    value = _to_iso_datetime(value) if field in ['date_changed', 'date_created'] else value
    if operator not in _FCC_OPERATORS:
        raise FilterError(f'Filter operator {operator} is not supported')
    field = field if operator == 'eq' else f'{field}__{operator}'
    return field, value

def _to_iso_datetime(date_filter_value: str) -> str:
    if not date_filter_value:
        return date_filter_value
    date_filter_value = date_filter_value.lower()
    if date_filter_value == "now":
        # TODO: parse offsets like now+1d, now-1h
        return date_filter_value
    try:
        return str(isoparse(date_filter_value))
    except ValueError as e:
        raise FilterError(f"Incorrect filter value: {date_filter_value}") from e
