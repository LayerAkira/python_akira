from typing import Dict, Tuple, Union, Optional

from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import FixedFee, GasFee
from LayerAkira.src.common.Requests import Order, ExecuteOutsideCall, SorContext
from LayerAkira.src.common.common import precise_from_price_to_str_convert


def serialize_fixed_fee(fee: FixedFee) -> Tuple[
    bool, Union[Dict, str]]:
    return True, {
        'recipient': fee.recipient.as_str(),
        'maker_pbips': fee.maker_pbips,
        'taker_pbips': fee.taker_pbips,
    }


def serialize_gas_fee(gas_fee: GasFee, erc_to_decimals, base_token: ERC20Token = ERC20Token.STRK) -> Tuple[
    bool, Union[Dict, str]]:
    return True, {
        "gas_per_action": gas_fee.gas_per_action,
        'fee_token': gas_fee.fee_token,
        'max_gas_price': precise_from_price_to_str_convert(gas_fee.max_gas_price, erc_to_decimals[base_token]),
        'conversion_rate': [
            precise_from_price_to_str_convert(gas_fee.conversion_rate[0], erc_to_decimals[base_token]),
            precise_from_price_to_str_convert(gas_fee.conversion_rate[1], erc_to_decimals[gas_fee.fee_token])
        ]
    }


def serialize_snip9_calldata(sinp_9_calldata: Optional[ExecuteOutsideCall]) -> Optional[Dict]:
    if sinp_9_calldata is None:
        return None

    return {
        'caller': sinp_9_calldata.caller.as_str(),
        'calls': [{
            'to': call.to.as_str(),
            'selector': call.selector,
            'args': call.args,
            'kwargs': call.kwargs
        } for call in sinp_9_calldata.calls],
        'execute_after': sinp_9_calldata.execute_after,
        'execute_before': sinp_9_calldata.execute_before,
        'nonce': hex(sinp_9_calldata.nonce),
        'signer_address': sinp_9_calldata.maker.as_str(),
        'version': sinp_9_calldata.version,
        'signature': [hex(x) for x in sinp_9_calldata.signature],
    }


def sor_context_to_json(order: Order) -> dict:
    if not order.sor_ctx:
        return None

    sor_ctx = order.sor_ctx

    path_json = []
    for path_item in sor_ctx.path:
        path_json.append({
            "price": str(path_item.price),
            "ticker": [path_item.ticker.base.value, path_item.ticker.quote.value],
            "is_sell_side": path_item.is_sell_side,
            "order_hash": path_item.order_hash if hasattr(path_item, 'order_hash') else 0
        })

    order_fee_json = {
        "trade_fee": {
            "taker_pbips": sor_ctx.order_fee.trade_fee.taker_pbips,
            "maker_pbips": sor_ctx.order_fee.trade_fee.maker_pbips,
            "recipient": str(sor_ctx.order_fee.trade_fee.recipient),
            "apply_to_receipt_amount": sor_ctx.order_fee.trade_fee.apply_to_receipt_amount
        },
        "router_fee": {
            "taker_pbips": sor_ctx.order_fee.router_fee.taker_pbips,
            "maker_pbips": sor_ctx.order_fee.router_fee.maker_pbips,
            "recipient": str(sor_ctx.order_fee.router_fee.recipient),
            "apply_to_receipt_amount": sor_ctx.order_fee.router_fee.apply_to_receipt_amount
        },
        "gas_fee": {
            "fee_token": sor_ctx.order_fee.gas_fee.fee_token.value,
            "gas_per_action": sor_ctx.order_fee.gas_fee.gas_per_action,
            "max_gas_price": str(sor_ctx.order_fee.gas_fee.max_gas_price),
            "conversion_rate": [
                str(sor_ctx.order_fee.gas_fee.conversion_rate[0]),
                str(sor_ctx.order_fee.gas_fee.conversion_rate[1])
            ]
        }
    }

    result = {
        "path": path_json,
        "order_fee": order_fee_json,
        "allow_non_atomic": sor_ctx.allow_non_atomic,
        "min_receive_amount": str(sor_ctx.min_receive_amount),
        "max_spend_amount": str(sor_ctx.max_spend_amount),
        "last_base_qty": str(sor_ctx.last_qty.base_qty),
        "last_quote_qty": str(sor_ctx.last_qty.quote_qty)
    }

    return result
class SimpleOrderSerializer:
    def __init__(self, erc_to_decimals: Dict[ERC20Token, int]):
        self._erc_to_decimals = erc_to_decimals

    def serialize(self, data: Order):
        result = {
            'maker': data.maker.as_str(),
            'price': precise_from_price_to_str_convert(data.price, self._erc_to_decimals[data.ticker.quote]),
            'qty': {
                'base_qty': precise_from_price_to_str_convert(data.qty.base_qty,
                                                              self._erc_to_decimals[data.ticker.base]),
                'quote_qty': precise_from_price_to_str_convert(data.qty.quote_qty,
                                                               self._erc_to_decimals[data.ticker.quote]),
            },
            'constraints': {
                "created_at": data.constraints.created_at,
                'router_signer': data.constraints.router_signer.as_str(),
                "number_of_swaps_allowed": data.constraints.number_of_swaps_allowed,
                "nonce": hex(data.constraints.nonce),
                'stp': data.constraints.stp.value,
                'duration_valid': data.constraints.duration_valid,
                'min_receive_amount': precise_from_price_to_str_convert(data.constraints.min_receive_amount,
                                                                        self._erc_to_decimals[
                                                                            data.ticker.quote] if data.flags.is_sell_side else
                                                                        self._erc_to_decimals[data.ticker.base]
                                                                        )
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
            "ticker": (data.ticker.base, data.ticker.quote),
            "fee": {
                "trade_fee": serialize_fixed_fee(data.fee.trade_fee)[1],
                'router_fee': serialize_fixed_fee(data.fee.router_fee)[1],
                'integrator_fee': serialize_fixed_fee(data.fee.integrator_fee)[1],
                'apply_to_receipt_amount':data.fee.apply_to_receipt_amount,
                'gas_fee': serialize_gas_fee(data.fee.gas_fee, self._erc_to_decimals)[1],
            },
            "salt": hex(data.salt),
            "sign": [hex(x) for x in data.sign],
            "router_sign": [hex(x) for x in data.router_sign],
            'source': data.source,
            'sign_scheme': data.sign_scheme.value,
        }

        snip9_data = serialize_snip9_calldata(data.snip9_calldata)
        if snip9_data is not None:
            result['snip9_call'] = snip9_data

        sor = sor_context_to_json(order=data)
        if sor is not None:
            result['sor'] = sor

        return result