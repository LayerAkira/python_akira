from typing import Dict, Tuple, Union

from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.FeeTypes import FixedFee, GasFee
from LayerAkira.src.common.Requests import Order


def serialize_fixed_fee(fee: FixedFee) -> Tuple[
    bool, Union[Dict, str]]:
    return True, {
        'recipient': fee.recipient.as_str(),
        'maker_pbips': fee.maker_pbips,
        'taker_pbips': fee.taker_pbips,
        'apply_to_receipt_amount': fee.apply_to_receipt_amount
    }


def serialize_gas_fee(gas_fee: GasFee, erc_to_addr: Dict[ERC20Token, ContractAddress]) -> Tuple[bool, Union[Dict, str]]:
    return True, {
        "gas_per_action": gas_fee.gas_per_action,
        'fee_token': erc_to_addr[gas_fee.fee_token].as_str(),
        'max_gas_price': gas_fee.max_gas_price,
        'conversion_rate': gas_fee.conversion_rate
    }


class SimpleOrderSerializer:
    def __init__(self, erc20_to_addr: Dict[ERC20Token, ContractAddress]):
        self._erc20_to_addr = erc20_to_addr

    def serialize(self, data: Order):
        return {
            'maker': data.maker.as_str(),
            'price': str(data.price),
            'qty': {
                'base_qty': str(data.qty.base_qty),
                'quote_qty': str(data.qty.quote_qty),
                'base_asset': str(data.qty.base_asset),
            },
            'constraints': {
                "created_at": data.constraints.created_at,
                'router_signer': data.constraints.router_signer.as_str(),
                "number_of_swaps_allowed": data.constraints.number_of_swaps_allowed,
                "nonce": hex(data.constraints.nonce),
                'stp': data.constraints.stp.value,
                'duration_valid': data.constraints.duration_valid,
                'min_receive_amount': data.constraints.min_receive_amount
            },
            'flags': {
                "full_fill_only": data.flags.full_fill_only,
                "best_level_only": data.flags.best_level_only,
                "post_only": data.flags.post_only,
                "to_ecosystem_book": data.flags.to_ecosystem_book,
                'is_sell_side': data.flags.is_sell_side,
                "is_market_order": data.flags.is_market_order,
                'external_funds': data.flags.external_funds
            },
            "ticker": (self._erc20_to_addr[data.ticker.base].as_str(), self._erc20_to_addr[data.ticker.quote].as_str()),
            "fee": {
                "trade_fee": serialize_fixed_fee(data.fee.trade_fee)[1],
                'router_fee': serialize_fixed_fee(data.fee.router_fee)[1],
                'gas_fee': serialize_gas_fee(data.fee.gas_fee, self._erc20_to_addr)[1],
            },
            "salt": data.salt,
            "sign": data.sign,
            "router_sign": data.router_sign,
            'version': data.version,
            'source': data.source
        }
