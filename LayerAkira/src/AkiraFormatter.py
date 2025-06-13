from typing import Dict, List, Tuple

from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import FixedFee, GasFee
from LayerAkira.src.common.Requests import Order, OrderFlags, IncreaseNonce, Withdraw, MinimalTakerOrderInfo
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.sor.SORDetails import SORDetails


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
                'sign_scheme': withdraw.sign_scheme.value
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
                    'integrator_fee': self._prepare_fixed_fee(order.fee.integrator_fee),
                    'apply_to_receipt_amount': order.fee.apply_to_receipt_amount,
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
            'taker_pbips': fixed_fee.taker_pbips
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

    def prepare_place_sor_order(
            self,
            orchestrate_order: MinimalTakerOrderInfo,
            path: List[MinimalTakerOrderInfo],
            router_signature: Tuple[int, int],
            details: SORDetails
    ):

        return {
            'orchestrate_order': self._prepare_simple_order(orchestrate_order),
            'path': [self._prepare_simple_order(order) for order in path],
            'router_signature': router_signature,
            'details': {
                'lead_qty': self._prepare_quantity(details.lead_qty),
                'last_qty': self._prepare_quantity(details.last_qty),
                'trade_fee': self._prepare_fixed_fee(details.trade_fee),
                'router_fee': self._prepare_fixed_fee(details.router_fee),
                'integrator_fee': self._prepare_fixed_fee(details.integrator_fee),
                'apply_to_receipt_amount': details.apply_to_receipt_amount,
                'gas_fee': self._prepare_gas_fee(details.gas_fee),

                'created_at': details.created_at,
                'source': details.source,
                'allow_nonatomic': details.allow_nonatomic,
                'to_ecosystem_book': details.to_ecosystem_book,
                'duration_valid': details.duration_valid,
                'nonce': details.nonce,
                'external_funds': details.external_funds,
                'router_signer': details.router_signer.as_int(),
                'salt': details.salt,
                'sign_scheme': details.sign_scheme.value,
                'number_of_swaps_allowed': details.number_of_swaps_allowed,
                'min_receive_amount': details.min_receive_amount,
                'max_spend_amount': details.max_spend_amount,
            }
        }

    def _prepare_simple_order(self, order: MinimalTakerOrderInfo):
        return {
            'price': order.price,
            'base_asset': order.base_asset,  # assuming base_asset is already an integer
            'ticker': self._prepare_ticker(order.ticker),
            'is_sell_side': order.is_sell_side,
        }

    @staticmethod
    def _prepare_quantity(qty):
        return {'base_qty': qty.base_qty, 'quote_qty': qty.quote_qty,
                'base_asset': qty.base_asset}

    def _prepare_ticker(self, ticker):
        return self._erc_to_addr[ticker.base].as_int(), self._erc_to_addr[ticker.quote].as_int()

