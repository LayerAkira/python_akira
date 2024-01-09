from dataclasses import dataclass


@dataclass
class FixedPoint:
    value: int
    decimals: int


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
