from enum import Enum


class ERC20Token(str, Enum):
    ETH = 'ETH'
    USDC = 'USDC'
    USDT = 'USDT'
