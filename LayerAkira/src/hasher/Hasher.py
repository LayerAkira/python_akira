from dataclasses import dataclass
from typing import Dict, Union

from starknet_py.utils.typed_data import TypedData

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.Requests import Withdraw, CancelRequest, Order, IncreaseNonce, Snip9OrderMatch
from LayerAkira.src.hasher.utils import withdraw_typed_data, get_order_typed_data, increase_nonce_typed_data, \
    cancel_typed_data, execute_outside_call_typed_data


@dataclass
class AppDomain:
    chain_id: int
    name: str = "LayerAkira Exchange"
    version: str = "0.0.1"


class SnTypedPedersenHasher:
    """Mirrors hashing of sn function for our objects"""

    def __init__(self, erc_to_addr: Dict[ERC20Token, ContractAddress], domain: AppDomain,
                 core: ContractAddress, executor: ContractAddress):
        self._erc_to_addr = erc_to_addr
        self._domain = domain
        self._core = core
        self._executor = executor

    def hash(self, obj: Union[Withdraw, CancelRequest, Order, IncreaseNonce]) -> int:
        if isinstance(obj, Withdraw):
            data = withdraw_typed_data(obj, self._erc_to_addr, self._domain, self._core)
        elif isinstance(obj, Order):
            data = get_order_typed_data(obj, self._erc_to_addr, self._domain, self._executor)
        elif isinstance(obj, IncreaseNonce):
            data = increase_nonce_typed_data(obj, self._erc_to_addr, self._domain)
            return data.message_hash(obj.maker.as_int())
        elif isinstance(obj, CancelRequest):
            data = cancel_typed_data(obj, self._erc_to_addr, self._domain)
        elif isinstance(obj, Snip9OrderMatch):
            data = execute_outside_call_typed_data(obj, self._domain, obj.outside_execute.version)
        else:
            raise Exception(f"Unknown object type {obj} {type(obj)}")

        if isinstance(obj, Snip9OrderMatch):
            d = TypedData.from_dict(data).message_hash(obj.maker.as_int())
            return d
        else:
            data = TypedData.from_dict(data)
            return data.message_hash(obj.maker.as_int())
