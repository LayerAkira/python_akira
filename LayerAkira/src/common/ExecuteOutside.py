from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, Set, Dict, Union, List

from starknet_py.serialization import Uint256Serializer

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token

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
        calls = [format_human_readable_call(call, allowed_erc, core, executor) for call in self.calls]
        if len([call for call in calls if call[0][0] == core]) > 1:
            return [(None, 'Duplicate call to approve executor')]
        return calls


class OutsideExecutionVersion(Enum):
    UNSUPPORTED = "0"
    V1 = "1"
    V2 = "2"


def format_human_readable_call(
        call: HumanReadableCall, allowed_addresses: Set[ContractAddress],
        core: ContractAddress,
        executor: ContractAddress,
) -> Tuple[Optional[Tuple[ContractAddress, Optional[int]]], Optional[str]]:
    # V`to`
    if call.to not in allowed_addresses and call.to != core:
        raise ValueError(f'Address {call.to} is not whitelisted in snip9')

    # `selector`
    if call.selector != "approve" and (call.to == core and call.selector != 'grant_access_to_executor'):
        raise ValueError(f'Selector {call.selector} is not whitelisted in snip9')
    if call.to == core:
        if not (len(call.args) == 0 and len(call.kwargs) == 0):
            raise ValueError('Grant access to executor have no args')
        return (call.to, None), None

    # mutual exclusivity of `args` and `kwargs`
    if bool(call.args) == bool(call.kwargs):  # Both defined or both empty
        raise ValueError('Args and kwargs are exclusive in snip9')

    # `args` format
    if call.args:
        if len(call.args) != 2:
            raise ValueError(f'Approve must have exactly 2 arguments in snip9')
        recipient, amount = ContractAddress(call.args[0]), call.args[1]
        if isinstance(amount, str):
            amount = int(amount, 16 if amount.startswith('0x') else 10)
    elif len(call.kwargs) != 2:
        raise ValueError(f'Approve must have exactly 2 arguments in snip9')
    else:
        recipient, amount = ContractAddress(call.kwargs.get('recipient', 0)), call.kwargs.get('amount', '0')
        if isinstance(amount, str):
            amount = int(amount, 16 if amount.startswith('0x') else 10)

    if recipient != executor:
        raise ValueError(f'Approve recipient is not exchange {executor}')
    if amount == 0:
        raise ValueError(f'Amount cannot be 0 in snip9')
    return (call.to, amount), None


def stp_enum_value(stp) -> dict:
    from LayerAkira.src.common.Requests import STPMode
    if stp == STPMode.NONE:
        return {"NONE": {}}
    elif stp == STPMode.EXPIRE_TAKER:
        return {"EXPIRE_TAKER": {}}
    elif stp == STPMode.EXPIRE_MAKER:
        return {"EXPIRE_MAKER": {}}
    elif stp == STPMode.EXPIRE_BOTH:
        return {"EXPIRE_BOTH": {}}
    else:
        raise ValueError(f"Unknown STPMode: {stp}")


def build_order_calldata(order, erc_to_address: Dict[ERC20Token, ContractAddress]) -> dict:
    u256_serde = Uint256Serializer()
    return {
        "maker": order.maker.as_str(),
        "price": u256_serde.serialize(order.price),
        "qty": {
            "base_qty": u256_serde.serialize(order.qty.base_qty),
            "quote_qty": u256_serde.serialize(order.qty.quote_qty),
            "base_asset": u256_serde.serialize(order.qty.base_asset),
        },
        "ticker": {
            0: erc_to_address[order.ticker.base],
            1: erc_to_address[order.ticker.quote],
        },
        "fee": {
            "trade_fee": {
                "recipient": order.fee.trade_fee.recipient,
                "maker_pbips": order.fee.trade_fee.maker_pbips,
                "taker_pbips": order.fee.trade_fee.taker_pbips,
                "apply_to_receipt_amount": order.fee.trade_fee.apply_to_receipt_amount,
            },
            "router_fee": {
                "recipient": order.fee.router_fee.recipient,
                "maker_pbips": order.fee.router_fee.maker_pbips,
                "taker_pbips": order.fee.router_fee.taker_pbips,
                "apply_to_receipt_amount": order.fee.router_fee.apply_to_receipt_amount,
            },
            "gas_fee": {
                "gas_per_action": order.fee.gas_fee.gas_per_action,
                "fee_token": erc_to_address[order.fee.gas_fee.fee_token],
                "max_gas_price": u256_serde.serialize(order.fee.gas_fee.max_gas_price),
                "conversion_rate": {
                    0: u256_serde.serialize(order.fee.gas_fee.conversion_rate[0]),
                    1: u256_serde.serialize(order.fee.gas_fee.conversion_rate[1]),
                },
            },
        },
        "constraints": {
            "number_of_swaps_allowed": order.constraints.number_of_swaps_allowed,
            "duration_valid": order.constraints.duration_valid,
            "created_at": order.constraints.created_at,
            "stp": stp_enum_value(order.constraints.stp),
            "nonce": order.constraints.nonce,
            "min_receive_amount": u256_serde.serialize(order.constraints.min_receive_amount),
            "router_signer": order.constraints.router_signer,
        },
        "salt": order.salt,
        "flags": {
            "full_fill_only": order.flags.full_fill_only,
            "best_level_only": order.flags.best_level_only,
            "post_only": order.flags.post_only,
            "is_sell_side": order.flags.is_sell_side,
            "is_market_order": order.flags.is_market_order,
            "to_ecosystem_book": order.flags.to_ecosystem_book,
            "external_funds": order.flags.external_funds,
        },
        "source": order.source,
        "sign_scheme": order.sign_scheme.value if order.sign_scheme else 0,
    }
