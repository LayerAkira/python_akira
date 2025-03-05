from typing import Dict

from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import FixedFee, GasFee
from LayerAkira.src.common.Requests import Order, OrderFlags, IncreaseNonce, Withdraw
from LayerAkira.src.common.ContractAddress import ContractAddress


class AkiraFormatter:
    """Formatter that prepares data for the call/execution"""

    def __init__(self, erc_to_addr: Dict[ERC20Token, ContractAddress]):
        self._erc_to_addr = erc_to_addr

    def prepare_withdraw(self, withdraw: Withdraw):
        return {
            'withdraw': {
                'maker': withdraw.maker.as_int(),
                'token': self._erc_to_addr[withdraw.token].as_int(),
                'amount': withdraw.amount,
                'salt': withdraw.salt,
                'gas_fee': self._prepare_gas_fee(withdraw.gas_fee),
                'receiver': withdraw.receiver.as_int(),
            },
            'sign': (withdraw.sign[0], withdraw.sign[1])
        }

    def prepare_order(self, order: Order):
        return {
            'sign': tuple(order.sign), 'router_sign': tuple(order.router_sign),
            'order': {
                'maker': order.maker.as_int(), 'price': order.price,
                'qty': {'base_qty': order.qty.base_qty, 'quote_qty': order.qty.quote_qty,
                        'base_asset': order.qty.base_asset},
                'ticker': (
                    self._erc_to_addr[order.ticker.base].as_int(), self._erc_to_addr[order.ticker.quote].as_int()),
                'fee': {
                    'trade_fee': self._prepare_fixed_fee(order.fee.trade_fee),
                    'router_fee': self._prepare_fixed_fee(order.fee.router_fee),
                    'gas_fee': self._prepare_gas_fee(order.fee.gas_fee),
                },
                'salt': order.salt,
                'constraints': {
                    'number_of_swaps_allowed': order.constraints.number_of_swaps_allowed,
                    'nonce': order.constraints.nonce,
                    'router_signer': order.constraints.router_signer.as_int(),
                    'created_at': order.constraints.created_at,
                    'duration_valid': order.constraints.duration_valid,
                    'stp': [order.constraints.stp.name, None],
                    'min_receive_amount': order.constraints.min_receive_amount
                },
                'flags': self._prepare_order_flags(order.flags),
                'source': order.source,
                'sign_scheme': order.sign_scheme.value
            }
        }

    def prepare_increase_nonce(self, increase_nonce: IncreaseNonce):
        return {
            'increase_nonce': {
                'maker': increase_nonce.maker.as_int(),
                'new_nonce': increase_nonce.new_nonce,
                'gas_fee': self._prepare_gas_fee(increase_nonce.gas_fee),
                'salt': increase_nonce.salt
            },
            'sign': tuple(increase_nonce.sign)
        }

    def _prepare_gas_fee(self, gas_fee: GasFee):
        return {
            'gas_per_action': gas_fee.gas_per_action,
            'fee_token': self._erc_to_addr[gas_fee.fee_token].as_int(),
            'max_gas_price': gas_fee.max_gas_price,
            'conversion_rate': tuple(gas_fee.conversion_rate),
        }

    @staticmethod
    def _prepare_fixed_fee(fixed_fee: FixedFee):
        return {
            'recipient': fixed_fee.recipient.as_int(), 'maker_pbips': fixed_fee.maker_pbips,
            'taker_pbips': fixed_fee.taker_pbips, 'apply_to_receipt_amount':fixed_fee.apply_to_receipt_amount
        }

    @staticmethod
    def _prepare_order_flags(flags: OrderFlags):
        return {
            "full_fill_only": flags.full_fill_only,
            "best_level_only": flags.best_level_only,
            "post_only": flags.post_only,
            "is_sell_side": flags.is_sell_side,
            "is_market_order": flags.is_market_order,
            "to_ecosystem_book": flags.to_ecosystem_book,
            "external_funds": flags.external_funds
        }
