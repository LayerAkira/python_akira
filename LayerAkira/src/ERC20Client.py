import logging
from typing import Tuple, Union

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, SimulatedTransaction, SentTransactionResponse, \
    ResourceBoundsMapping
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.serialization.factory import serializer_for_payload

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.StarknetEntities import AccountExecutor, StarknetSmartContract
from LayerAkira.src.common.common import Result
from LayerAkira.src.common.constants import ERC20ABI


class ERC20Client:
    """Client that allows to interact with specified erc20 token"""

    def __init__(self, client: FullNodeClient, token_addr: ContractAddress = ContractAddress(0)):
        self._client = client
        self._account_executor = AccountExecutor(client)
        self._token_addr = token_addr

        self._name_to_deser = {}
        self.token_contract: StarknetSmartContract = StarknetSmartContract(
            Contract(self._token_addr.as_int(), ERC20ABI, self._client, cairo_version=0))
        contract = self.token_contract.contract
        for k, v in contract.data.parsed_abi.functions.items():
            self._name_to_deser[k] = serializer_for_payload(v.outputs).deserialize

    async def balanceOf(self, addr: ContractAddress, block='pending') -> Result[int]:
        return await self._call('balanceOf', block, addr.as_int())

    async def allowance(self, owner: ContractAddress, spender: ContractAddress, block='pending') -> Result[int]:
        return await self._call('allowance', block, owner.as_int(), spender.as_int())

    async def approve(self, account: Account, spender: ContractAddress, amount: int,
                      max_fee: ResourceBoundsMapping,
                      nonce=None,
                      send_to_chain=True):
        call = self.token_contract.prepare_calldata('approve', spender.as_int(), amount)
        return await self._execute(call, account, max_fee, nonce, send_to_chain)

    async def increase_allowance(self, account: Account, spender: ContractAddress, added_amount: int,
                                 max_fee: ResourceBoundsMapping,
                                 nonce=None,
                                 send_to_chain=True):
        call = self.token_contract.prepare_calldata('increaseAllowance', spender.as_int(), added_amount)
        return await self._execute(call, account, max_fee, nonce, send_to_chain)

    async def _execute(self, call: Call, account: Account, max_fee, nonce, on_succ_send=True) -> Tuple[
        bool, Union[SimulatedTransaction, SentTransactionResponse]]:
        succ, res = await self._account_executor.simulate_tx(call, account, False, False, nonce=nonce,
                                                             max_fee=max_fee, block_number='pending')
        if not succ:
            logging.error(f'Failed to simulate call to contract {res}')
            return False, res
        if on_succ_send:
            return await self._account_executor.execute_tx(call, account, nonce, max_fee)
        return True, res

    async def _call(self, method_name, block, *args, **kwargs):
        try:
            return Result(self._name_to_deser[method_name](
                await self.token_contract.call(self.token_contract.prepare_calldata(method_name, *args, **kwargs),
                                               block=block))[0])
        except Exception as e:
            return Result(data=None, error_type=e, error=e.__str__())
