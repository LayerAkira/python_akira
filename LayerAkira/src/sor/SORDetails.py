from dataclasses import dataclass

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.FeeTypes import FixedFee, GasFee
from LayerAkira.src.common.Requests import Quantity, SignScheme, Order, SorContext


@dataclass
class SORDetails:
    lead_qty: Quantity  # forecasted quantity by the user
    last_qty: Quantity  # forecasted quantity by the user, ignored in case of exact sell
    trade_fee: FixedFee  # same as in Order
    router_fee: FixedFee  # same as in Order
    integrator_fee: FixedFee
    apply_to_receipt_amount:bool
    gas_fee: GasFee  # same as in Order
    created_at: int  # u32 field, representing creation timestamp
    source: str  # felt252 field, same as in Order
    allow_nonatomic: bool  # determines if execution can be split or must be atomic
    to_ecosystem_book: bool  # same as in Order
    duration_valid: int  # u32 field representing how long the order is valid
    nonce: int  # u32 field, same as in Order
    external_funds: bool  # same as in Order
    router_signer: ContractAddress  # same as in Order
    salt: int  # felt252 field, same as in Order
    sign_scheme: SignScheme
    number_of_swaps_allowed: int  # u16 field, using int in Python
    min_receive_amount: int  # u256 field, for the ending leg of the trade
    max_spend_amount: int  # u256 field, for the beginning leg of the trade

    @staticmethod
    def build_from(order: Order) -> 'SORDetails':
        sor_ctx: SorContext = order.sor_ctx
        return SORDetails(
            lead_qty=order.qty,
            last_qty=sor_ctx.last_qty,
            trade_fee=sor_ctx.order_fee.trade_fee,
            router_fee=sor_ctx.order_fee.router_fee,
            integrator_fee=sor_ctx.order_fee.integrator_fee,
            apply_to_receipt_amount=sor_ctx.order_fee.apply_to_receipt_amount,
            gas_fee=sor_ctx.order_fee.gas_fee,
            created_at=order.constraints.created_at,
            source=order.source,
            allow_nonatomic=sor_ctx.allow_non_atomic,
            to_ecosystem_book=order.flags.to_ecosystem_book,
            duration_valid=order.constraints.duration_valid,
            nonce=order.constraints.nonce,
            external_funds=order.flags.external_funds,
            router_signer=order.constraints.router_signer,
            salt=order.salt,
            sign_scheme=order.sign_scheme,
            number_of_swaps_allowed=order.constraints.number_of_swaps_allowed,
            min_receive_amount=sor_ctx.min_receive_amount,
            max_spend_amount=sor_ctx.max_spend_amount,

        )
