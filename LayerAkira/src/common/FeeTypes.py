from dataclasses import dataclass
from typing import Tuple

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token


@dataclass
class FixedFee:
    recipient: ContractAddress
    maker_pbips: int
    taker_pbips: int
    apply_to_receipt_amount: bool = True

    def __post_init__(self):
        assert isinstance(self.recipient, ContractAddress)


@dataclass
class GasFee:
    gas_per_action: int
    fee_token: ERC20Token
    max_gas_price: int
    conversion_rate: Tuple[float, float]  # conversion rate to


@dataclass
class OrderFee:
    trade_fee: FixedFee
    router_fee: FixedFee
    gas_fee: GasFee

    def __str__(self):
        return f'OrderFee(trade_fee={self.trade_fee},router_fee={self.router_fee},gas_fee={self.gas_fee})'
