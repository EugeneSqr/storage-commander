# from dataclasses import dataclass
# from typing import TypeVar, Optional, Generic, Type
#
# T = TypeVar('T', str, int)
#
# @dataclass
# class FilterField(Generic[T]):
#     value_type: T
#     name: str
#     operator: str = 'eq'
#     serialized_value: str = str()
#     value: Optional[T] = None
