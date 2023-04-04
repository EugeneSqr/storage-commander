from enum import Enum
from typing import Dict, Tuple, List

from dateutil.parser import isoparse

from storcom.errors import FilterError

class EnumWithValues(Enum):
    @classmethod
    def values(cls) -> List[str]:
        return [item.value for item in cls]

class FccFilter(str, EnumWithValues):
    BATCH = 'batch'
    DATE_CHANGED = 'date_changed'
    DATE_CREATED = 'date_created'

class FccOperator(str, EnumWithValues):
    EQ = 'eq'
    LT = 'lt'
    GT = 'gt'
    LTE = 'lte'
    GTE = 'gte'

def to_fcc_qs_params(filters: Dict[str, str]) -> Dict[str, str]:
    return dict(_to_fcc_qs_param(k, v) for k, v in filters.items() if v and k in FccFilter.values())

def _to_fcc_qs_param(filter_field: str, filter_value: str) -> Tuple[str, str]:
    split_filter_value = filter_value.split(' ', 1)
    param_operator, param_value = FccOperator.EQ.value, ''
    if len(split_filter_value) == 1:
        param_value = split_filter_value[0]
    else:
        param_operator, param_value = split_filter_value
    return _to_fcc_filter_expression(filter_field, param_operator, param_value)

def _to_fcc_filter_expression(field: str, operator: str, value: str) -> Tuple[str, str]:
    operator = operator.lower()
    value = value.strip('\'"')
    value = (_to_iso_datetime(value) if field in [FccFilter.DATE_CHANGED, FccFilter.DATE_CREATED]
             else value)
    if operator not in FccOperator.values():
        raise FilterError(f'Filter operator {operator} is not supported')
    field = field if operator == FccOperator.EQ else f'{field}__{operator}'
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
