from typing import Dict, Tuple

FCC_FILTER_FIELDS = ['batch']

def to_fcc_qs_params(filters: Dict[str, str]) -> Dict[str, str]:
    return dict(_to_fcc_qs_param(k, v) for k, v in filters.items() if v and k in FCC_FILTER_FIELDS)

def _to_fcc_qs_param(key: str, filter_value: str) -> Tuple[str, str]:
    split_filter_value = filter_value.split(' ', 1)
    param_operator, param_value = 'eq', ''
    if len(split_filter_value) == 1:
        param_value = split_filter_value[0]
    else:
        param_operator, param_value = split_filter_value
        param_operator = param_operator.lower()
    return key, param_value.strip('\'"')
