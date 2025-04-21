from enum import Enum


class ERC20Token(str, Enum):
    ETH = 'ETH'
    USDC = 'USDC'
    USDT = 'USDT'
    STRK = 'STRK'
    AETH = 'AETH'
    AUSDC = 'AUSDC'
    AUSDT = 'AUSDT'

    def __format__(self, format_spec: str) -> str:
        return format(self.value, format_spec)

TEST_TOKENS = [ERC20Token.AUSDC, ERC20Token.AUSDT, ERC20Token.AETH,]