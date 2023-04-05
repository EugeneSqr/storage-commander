from dataclasses import dataclass, fields
from typing import Dict, Tuple, List, Callable, Optional, Union

from dateutil.parser import isoparse

from storcom.errors import FilterError


# TODO: move to aliases.py and reuse
QueryArg = Optional[Union[str, Tuple[str]]]

class FccFilterField:
    BATCH: str = 'batch'
    DATE_CHANGED: str = 'date_changed'
    DATE_CREATED: str = 'date_created'

@dataclass
class FccOperator:
    # Using simple dataclass, because no decent Enum for python3.6 is available
    # StrEnum is available in standard library only in python 3.11
    # StrEnum backports aren't mypy compatible at least in python3.6
    # FccOperator(str, Enum) doesn't work well with mypy when it comes to assigning enum values
    # like o = FccOperator.EQ - FccOpeartor.EQ.value has to be used instead
    EQ: str = 'eq'
    LT: str = 'lt'
    GT: str = 'gt'
    LTE: str = 'lte'
    GTE: str = 'gte'

    @classmethod
    def values(cls) -> List[str]:
        return [f.default for f in fields(cls)]

@dataclass
class Filter:
    field: str = ''
    multiple: bool = False
    input_adapter: Optional[Callable[[str], str]] = None

def get_fcc_filters() -> List[Filter]:
    return [
        Filter(FccFilterField.BATCH),
        Filter(FccFilterField.DATE_CHANGED,
               multiple=True,
               input_adapter=_to_iso_datetime),
        Filter(FccFilterField.DATE_CREATED,
               multiple=True,
               input_adapter=_to_iso_datetime),
    ]

def to_fcc_qs_params(query_args: Dict[str, QueryArg]) -> Dict[str, str]:
    qs_params = dict(_to_fcc_qs_param(f, query_args[f.field])
                     for f in get_fcc_filters()
                     if f.field in query_args)
    return {k: v for k, v in qs_params.items() if k != ''}

def _to_fcc_qs_param(fcc_filter: Filter, query_arg: QueryArg) -> Tuple[str, str]:
    empty_qs_param = ('', '')
    if not query_arg:
        return empty_qs_param
    print('>>>>', query_arg, len(query_arg))
    if fcc_filter.multiple and len(query_arg) > 1:
        # TODO: not supported so far
        return empty_qs_param
    assert isinstance(query_arg, str)
    split_query_arg = query_arg.split(' ', 1)
    param_operator, param_value = FccOperator.EQ, ''
    if len(split_query_arg) == 1:
        param_value = split_query_arg[0]
    else:
        param_operator, param_value = split_query_arg
    return _to_fcc_filter_expression(fcc_filter.field, param_operator, param_value)

def _to_fcc_filter_expression(field: str, operator: str, value: str) -> Tuple[str, str]:
    operator = operator.lower()
    value = value.strip('\'"')
    date_fields = [FccFilterField.DATE_CHANGED, FccFilterField.DATE_CREATED]
    value = _to_iso_datetime(value) if field in date_fields else value
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
