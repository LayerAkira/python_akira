from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import OrderFee, GasFee
from LayerAkira.src.common.FixedPoint import FixedPoint
from LayerAkira.src.common.TradedPair import TradedPair

OrderTimestamp = int


class Side(Enum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return str(self.value)


@dataclass
class OrderFlags:
    __slots__ = ('full_fill_only', 'best_level_only', 'post_only', 'is_sell_side', 'is_market_order', 'to_safe_book')
    full_fill_only: bool
    best_level_only: bool
    post_only: bool
    is_sell_side: bool
    is_market_order: bool
    to_safe_book: bool

    def as_tuple(self):
        return self.full_fill_only, self.best_level_only, self.post_only, self.is_sell_side, self.is_market_order, self.to_safe_book


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1

    def __str__(self):
        return str(self.value)


@dataclass
class Order:
    maker: ContractAddress
    price: FixedPoint
    quantity: FixedPoint
    ticker: TradedPair
    fee: OrderFee
    number_of_swaps_allowed: int
    salt: int
    nonce: int
    flags: OrderFlags
    router_signer: ContractAddress
    base_asset: int
    sign: Tuple[int, int]
    router_sign: Tuple[int, int]
    created_at: OrderTimestamp

    def __post_init__(self):
        assert isinstance(self.maker, ContractAddress)
        assert isinstance(self.router_signer, ContractAddress)

    def is_passive_order(self):
        return not self.type == OrderType.MARKET and self.post_only

    @property
    def side(self) -> Side:
        return Side.SELL if self.flags.is_sell_side else Side.BUY

    @property
    def type(self) -> OrderType:
        if self.flags.is_market_order: return OrderType.MARKET
        return OrderType.LIMIT

    @property
    def full_fill_only(self):
        return self.flags.full_fill_only

    @property
    def best_level_only(self):
        return self.flags.best_level_only

    @property
    def post_only(self):
        return self.flags.post_only

    @property
    def to_safe_book(self):
        return self.flags.to_safe_book

    def is_safe_order(self):
        return self.router_sign[0] == 0 and self.router_sign[1] == 0

    def __str__(self):
        fields = [
            f"price={self.price.__str__()}",
            f"quantity={self.quantity.__str__()}",
            f"maker={self.maker}",
            f"created_at={self.created_at}",
            f"flags={self.flags}",
            f"side={self.side.value}",
            f"ticker={self.ticker}",
            f"type={self.type}",
            f"salt={self.salt}",
            f"sign={self.sign}",
            f'router_sign={self.sign},'
            f'nonce={self.nonce}',
            f'to_safe={self.to_safe_book}',
            f'order_fee={self.fee}'
        ]
        return f"Order({', '.join(fields)})\n"


@dataclass
class CancelRequest:
    maker: ContractAddress
    order_hash: Optional[int]
    salt: int
    sign: Tuple[int, int]


@dataclass
class IncreaseNonce:
    maker: ContractAddress
    new_nonce: int
    gas_fee: GasFee
    salt: int
    sign: Tuple[int, int]


@dataclass
class Withdraw:
    maker: ContractAddress
    token: ERC20Token
    amount: FixedPoint
    salt: int
    sign: Tuple[int, int]
    gas_fee: GasFee
    receiver: ContractAddress

    def __str__(self):
        fields = [
            f"maker={str(self.maker)}",
            f"token={self.token.value}",
            f"amount={self.amount}",
            f'gas_fee={self.gas_fee}'
        ]
        return f"Withdraw({', '.join(fields)})\n"

    def __post_init__(self):
        assert isinstance(self.maker, ContractAddress)
        assert isinstance(self.receiver, ContractAddress)
