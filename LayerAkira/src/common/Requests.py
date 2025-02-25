from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List, Dict, Union, Set

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.ExecuteOutside import validate_human_readable_call
from LayerAkira.src.common.FeeTypes import OrderFee, GasFee
from LayerAkira.src.common.TradedPair import TradedPair

OrderTimestamp = int


class Side(Enum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class SpotTicker:
    """
    A  data class that represents a spot ticker.
    Attributes:
        pair (TradedPair): The traded pair associated with this ticker.
        is_ecosystem_book (bool): A flag indicating if it is an ecosystem book or router.
    """
    pair: TradedPair
    is_ecosystem_book: bool


@dataclass
class OrderFlags:
    full_fill_only: bool
    best_level_only: bool
    post_only: bool
    is_sell_side: bool
    is_market_order: bool
    to_ecosystem_book: bool
    external_funds: bool

    def as_tuple(self):
        return (self.full_fill_only, self.best_level_only, self.post_only, self.is_sell_side, self.is_market_order,
                self.to_ecosystem_book, self.external_funds)


class STPMode(int, Enum):
    """
    Self trade prevention mode
    STP mode, if NONE process as usual
    """
    NONE = 0
    EXPIRE_TAKER = 1
    EXPIRE_MAKER = 2
    EXPIRE_BOTH = 3


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1

    def __str__(self):
        return str(self.value)


@dataclass
class Quantity:
    base_qty: int  # quantity in base asset raw amount
    quote_qty: int  # quantity in quote asset raw amount
    base_asset: int  # raw amount of base asset representing 1, eg 1 eth is 10**18


@dataclass
class Constraints:
    number_of_swaps_allowed: int
    duration_valid: int
    created_at: int
    stp: STPMode
    nonce: int
    min_receive_amount: int
    router_signer: ContractAddress


@dataclass
class SignScheme(str, Enum):
    ECDSA = "ecdsa curve"
    ACCOUNT = "account"
    DIRECT = "direct"
    NOT_SPECIFIED = ""


ECDSASignature = Tuple[int, int]
ClientSignature = Union[Tuple[int, ...], ECDSASignature]


@dataclass(frozen=True)
class Call:
    to: int
    selector: int
    calldata: List[int]


@dataclass(frozen=True)
class HumanReadableCall:
    to: ContractAddress
    selector: str
    args: List[str]
    kwargs: Dict[str, str]


@dataclass
class ExecuteOutsideCall:
    """
    Snip-9 support of execute outside functionality
    Only applicable for external takers, not saved to database
    """
    caller: ContractAddress
    calls: List[HumanReadableCall]  # without last call to our method placeOrder
    execute_after: int
    execute_before: int
    nonce: int
    signature: ClientSignature
    maker: ContractAddress  # aka signer
    version: str

    def get_multicall(self, allowed_erc: Set[ContractAddress], core: ContractAddress, executor: ContractAddress) -> \
            List[Tuple[Optional[Tuple[ContractAddress, Optional[int]]], Optional[str]]]:
        calls = [validate_human_readable_call(call, allowed_erc, core, executor) for call in self.calls]
        if len([call for call in calls if call[0][0] == core]) > 1:
            return [(None, 'Duplicate call to approve executor')]
        return calls


@dataclass
class Order:
    maker: ContractAddress
    price: int
    qty: Quantity
    ticker: TradedPair
    fee: OrderFee
    constraints: Constraints
    salt: int
    flags: OrderFlags
    sign: Tuple[int, int]
    router_sign: Tuple[int, int]
    source: str = 'layerakira'
    sign_scheme: SignScheme = None
    snip9_calldata: Optional[ExecuteOutsideCall] = None

    def __post_init__(self):
        assert isinstance(self.maker, ContractAddress)
        assert isinstance(self.constraints.router_signer, ContractAddress)
        assert self.sign is not None, 'Sign scheme for order should be specified'

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
    def to_ecosystem_book(self):
        return self.flags.to_ecosystem_book

    def is_ecosystem_order(self):
        return self.router_sign[0] == 0 and self.router_sign[1] == 0

    def __str__(self):
        fields = [
            f"price={self.price.__str__()}",
            f"qty={self.qty}",
            f"maker={self.maker}",
            f"constraints={self.constraints}",
            f"flags={self.flags}",
            f"side={self.side.value}",
            f"ticker={self.ticker}",
            f"type={self.type}",
            f"salt={self.salt}",
            f"sign={self.sign}",
            f'router_sign={self.sign},'
            f'to_ecosystem={self.to_ecosystem_book}',
            f'order_fee={self.fee}'
        ]
        return f"Order({', '.join(fields)})\n"


@dataclass
class CancelRequest:
    maker: ContractAddress
    order_hash: Optional[int]
    exchange_ticker: Optional[SpotTicker]  # ignored in case order hash defined
    salt: int
    sign: Tuple[int, int]


@dataclass
class IncreaseNonce:
    maker: ContractAddress
    new_nonce: int
    gas_fee: GasFee
    salt: int
    sign: Tuple[int, int]
    sign_scheme: SignScheme


@dataclass
class Withdraw:
    maker: ContractAddress
    token: ERC20Token
    amount: int
    salt: int
    sign: Tuple[int, int]
    gas_fee: GasFee
    receiver: ContractAddress
    sign_scheme: SignScheme

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


@dataclass
class Snip9OrderMatch:
    """
    msghash of following:
    approve,
    ...,
    approve,
    placeTakerOrder(order:order)

    """
    maker: ContractAddress
    approves: List[Call]
    place_order: Call
    outside_execute: ExecuteOutsideCall