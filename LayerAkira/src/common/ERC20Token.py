from enum import Enum


class ERC20Token(str, Enum):
    ETH = 'ETH'
    USDC = 'USDC'
    USDT = 'USDT'
    STRK = 'STRK'
    AETH = 'AETH'
    AUSDC = 'AUSDC'
    AUSDT = 'AUSDT'


TEST_TOKENS = [ERC20Token.AUSDC, ERC20Token.AUSDT, ERC20Token.AETH,]
