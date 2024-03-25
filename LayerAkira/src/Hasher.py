from typing import Dict, Union

from poseidon_py.poseidon_hash import poseidon_hash_many
from starknet_py.cairo.data_types import StructType
from starknet_py.serialization import serializer_for_payload

from LayerAkira.src.AkiraFormatter import AkiraFormatter
from LayerAkira.src.common.Requests import Withdraw, CancelRequest, Order, IncreaseNonce


class SnHasher:
    """Mirrors hashing of sn function"""

    def __init__(self, formatter: AkiraFormatter, defined_structs: Dict[str, StructType]):
        self._formatter = formatter
        self._w_serialize = serializer_for_payload(
            defined_structs['kurosawa_akira::WithdrawComponent::Withdraw'].types).serialize
        self._o_serialize = serializer_for_payload(defined_structs['kurosawa_akira::Order::Order'].types).serialize
        self._n_serialize = serializer_for_payload(
            defined_structs['kurosawa_akira::NonceComponent::IncreaseNonce'].types).serialize
        self._c_serialize = lambda x: [x.maker.as_int(), x.order_hash if x.order_hash is not None else 0, x.salt]

    def hash(self, obj: Union[Withdraw, CancelRequest, Order, IncreaseNonce]) -> int:
        if isinstance(obj, Withdraw):
            data = self._w_serialize(self._formatter.prepare_withdraw(obj)['withdraw'])
        elif isinstance(obj, Order):
            data = self._o_serialize(self._formatter.prepare_order(obj)['order'])
        elif isinstance(obj, IncreaseNonce):
            data = self._n_serialize(self._formatter.prepare_increase_nonce(obj)['increase_nonce'])
        elif isinstance(obj, CancelRequest):
            data = self._c_serialize(obj)
        else:
            raise Exception(f"Unknown object type {obj} {type(obj)}")
        return poseidon_hash_many(data)
