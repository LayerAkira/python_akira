from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, List, Optional

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.Requests import OrderFlags, Order, STPMode, Quantity
from LayerAkira.src.common.TradedPair import TradedPair


@dataclass
class UserInfo:
    nonce: int
    fees: Dict[TradedPair, Tuple[int, int]]
    balances: Dict[ERC20Token, Tuple[str, str]]


@dataclass
class RouterDetails:
    taker_pbips: int
    maker_pbips: int
    fee_recipient: ContractAddress
    router_signer: ContractAddress


@dataclass
class TableLevel:
    price: int
    volume: int
    num_orders: int

    def __str__(self):
        return f'Lvl(px={self.price},vol={self.volume},orders={self.num_orders})'


@dataclass
class Table:
    bids: List[TableLevel]  # from lowest to lowest
    asks: List[TableLevel]  # from lowest to highest

    def __str__(self):
        asks = 'asks:[' + ','.join([ask.__str__() for ask in self.asks]) + ']'
        bids = 'bids:[' + ','.join([bid.__str__() for bid in reversed(self.bids)]) + ']'
        return '\n'.join([asks, bids])


class OrderStatus(str, Enum):
    ACCEPTED = 'ACC'  # order accepted by the exchange
    OPEN = 'OPEN'  # order successfully inserted to the book
    SCHEDULED_CANCEL = "SCHEDULED_TO_CANCEL"  # order  scheduled to be cancelled
    CANCELLED = "CANCELLED"  # order was successfully cancelled and removed from the order book
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'  # order was partially filled
    FILLED = 'FILLED'  # order was fully filled
    CLOSED = 'CLOSED'  # order was closed (in case of taker orders)
    FAILED_ROLLUP = 'FAILED_ROLLUP'  # part of order was failed due some issue, used in reports only
    REIMBURSE = 'REIMBURSE'  # part of order was failed due some issue, used in reports only
    NOT_PROCESSED = 'NOT_PROCESSED'
    EXPIRED = 'EXPIRED'  # order expired


OrderMatcherResult = str


@dataclass
class Snapshot:
    table: Table
    msg_id: int
    pair: TradedPair = None
    time: int = 0
    msg_ids_start: int = 0
    msg_ids_end: int = 0


@dataclass
class OrderStateInfo:
    filled_base_amount: int
    filled_quote_amount: int
    cur_number_of_swaps: int
    status: OrderStatus
    limit_price: Optional[int]


@dataclass
class ReducedOrderInfo:
    maker: ContractAddress
    hash: int
    state: OrderStateInfo
    price: int
    ticker: TradedPair
    qty: Quantity
    order_flags: OrderFlags
    stp: STPMode
    expiration_time: int
    source: str


@dataclass
class ExecReport:
    client: ContractAddress
    pair: TradedPair
    price: int
    base_qty: int
    quote_qty: int
    acc_base_qty: int
    acc_quote_qty: int
    order_hash: int
    is_sell_side: bool
    status: OrderStatus
    mather_result: OrderMatcherResult
    taker_source: Optional[str]


@dataclass
class CancelAllReport:
    client: ContractAddress
    hash: int
    pair: TradedPair


@dataclass
class FailProcessingReport:
    client: ContractAddress
    report_type: str
    req_hash: int
    entity_hash: int
    error_code_orderbook: Optional[str]


@dataclass
class TxHashRollupReport:
    tx_hash: int
    order_hash: int
    client: ContractAddress
    source: str
    old_tx_hash: Optional[int] = None


@dataclass
class OrderInfo:
    order: Order
    state: OrderStateInfo


@dataclass
class BBO:
    bid: Optional[TableLevel]
    ask: Optional[TableLevel]
    ts: int
    pair: TradedPair = None


#
@dataclass
class Trade:
    price: int
    base_qty: int
    is_sell_side: bool
    time: int
    pair: TradedPair = None
