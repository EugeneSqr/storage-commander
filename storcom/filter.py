from typing import Dict, Tuple

FCC_FILTER_FIELDS = ['batch']

def to_fcc_qs_params(filters: Dict[str, str]) -> Dict[str, str]:
    return dict(_to_fcc_qs_param(k, v) for k, v in filters.items() if v and k in FCC_FILTER_FIELDS)

def _to_fcc_qs_param(key: str, value: str) -> Tuple[str, str]:
    split_value = value.split()
    return key, split_value[1].strip('\'"')
