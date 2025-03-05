from typing import Union


class ContractAddress:
    def __init__(self, val: Union[str, int]):
        if isinstance(val, str):
            self._value = int(val, 16)
        elif isinstance(val, int):
            self._value = int(val)
        elif isinstance(val, ContractAddress):
            self._value = val._value
        else:
            raise Exception(f'Unknown type for {val}')

    def __str__(self):
        return self.as_str()

    def __repr__(self):
        return f"ContractAddress({hex(self._value)})"

    def __eq__(self, other):
        return self._value == other._value

    def __ne__(self, other):
        return not self._value == other._value

    def __hash__(self):
        return self._value

    def as_int(self) -> int:
        return self._value

    def as_str(self):
        return f"{self._value:#0{66}x}"