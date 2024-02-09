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
            'price': data.price,
            'quantity': data.quantity,
            'base_asset': data.base_asset,
            "created_at": data.created_at,
            'flags': {
                "full_fill_only": data.full_fill_only,
                "best_level_only": data.best_level_only,
                "post_only": data.post_only,
                "to_safe_book": data.to_safe_book,
                'is_sell_side': bool(data.side.value),
                "is_market_order": bool(data.type.value),
            },
            "ticker": (self._erc20_to_addr[data.ticker.base].as_str(), self._erc20_to_addr[data.ticker.quote].as_str()),
            "fee": {
                "trade_fee": serialize_fixed_fee(data.fee.trade_fee)[1],
                'router_fee': serialize_fixed_fee(data.fee.router_fee)[1],
                'gas_fee': serialize_gas_fee(data.fee.gas_fee, self._erc20_to_addr)[1],
            },
            'router_signer': data.router_signer.as_str(),
            "number_of_swaps_allowed": data.number_of_swaps_allowed,
            "salt": data.salt,
            "sign": data.sign,
            "router_sign": data.router_sign,
            "nonce": data.nonce,
            'stp': data.stp.value,
            'expire_at': data.expire_at,
            'version': data.version
        }
