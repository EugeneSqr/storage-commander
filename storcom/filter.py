from typing import Dict, Tuple

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
    if operator not in _FCC_OPERATORS:
        raise FilterError(f'Filter operator {operator} is not supported')
    field = field if operator == 'eq' else f'{field}__{operator}'
    return field, value
