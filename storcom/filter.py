from dataclasses import dataclass, fields
from typing import Dict, Tuple, List, Callable, cast, Iterable
from functools import reduce

from dateutil.parser import isoparse

from storcom.errors import FilterError
from storcom.aliases import QueryArg


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
    input_adapter: Callable[[str], str] = lambda x: x

def get_fcc_filters() -> List[Filter]:
    return [
        Filter("batch"),
        Filter("date_changed", multiple=True, input_adapter=_to_iso_datetime),
        Filter("date_created", multiple=True, input_adapter=_to_iso_datetime),
    ]

def to_fcc_qs_params(query_args: Dict[str, QueryArg]) -> Dict[str, str]:
    return _merge_dictionaries(_to_fcc_qs_param(f, query_args[f.field])
                               for f in get_fcc_filters()
                               if f.field in query_args)

def _to_fcc_qs_param(fcc_filter: Filter, query_arg: QueryArg) -> Dict[str, str]:
    if not query_arg:
        return {}
    return (
        _to_fcc_qs_param_multivalue(fcc_filter, cast(Tuple[str], query_arg)) if fcc_filter.multiple
        else _to_fcc_qs_param_single_value(fcc_filter, cast(str, query_arg))
    )

def _to_fcc_qs_param_multivalue(fcc_filter: Filter, values: Tuple[str]) -> Dict[str, str]:
    return _merge_dictionaries(_to_fcc_qs_param_single_value(fcc_filter, v) for v in values)

def _to_fcc_qs_param_single_value(fcc_filter: Filter, query_arg_value: str) -> Dict[str, str]:
    split_query_arg = query_arg_value.split(' ', 1)
    operator, value = FccOperator.EQ, ''
    if len(split_query_arg) == 1:
        value = split_query_arg[0]
    else:
        operator, value = split_query_arg
    operator = operator.lower()
    value = fcc_filter.input_adapter(value.strip('\'"'))
    if operator not in FccOperator.values():
        raise FilterError(f'Filter operator {operator} is not supported')
    field = fcc_filter.field if operator == FccOperator.EQ else f'{fcc_filter.field}__{operator}'
    return {field: value}

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

def _merge_dictionaries(dictionaries: Iterable[Dict[str, str]]) -> Dict[str, str]:
    return reduce(lambda accumulated, new: dict(accumulated, **new), dictionaries, {})
