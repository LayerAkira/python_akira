from dataclasses import dataclass
from random import random
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    data: T
    error_type: Optional[Any] = None
    error: str = ''


def precise_to_price_convert(value: str, decimals: int) -> int:
    point_index = value.find('.')
    if point_index == -1:
        decimals = ''.join((['0'] * decimals))
        return int(value + decimals)
    num_digits_after_point = len(value) - point_index - 1
    before_point, after_point = value[:point_index], value[point_index + 1:]
    if before_point == '0':
        decimals = ''.join(['0'] * (decimals - num_digits_after_point))
        return int(after_point.lstrip('0') + decimals)
    else:
        decimals = ''.join(['0'] * (decimals - num_digits_after_point))
        return int(before_point + after_point + decimals)


def precise_from_price_to_str_convert(value: int, decimals: int) -> str:
    if value == 0: return '0'
    value_str = str(value)
    if len(value_str) <= decimals:
        return '0.' + '0' * (decimals - len(value_str)) + value_str.rstrip('0') or '0'

    before_point = value_str[:-decimals]
    after_point = value_str[-decimals:].rstrip('0')

    if not after_point:
        return before_point

    return before_point + '.' + after_point


def random_int(to=100000000):
    return abs(int(random() * to))
