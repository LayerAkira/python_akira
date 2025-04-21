import logging
from dataclasses import dataclass
from typing import Tuple, Optional, Union

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, SimulatedTransaction, SentTransactionResponse, TransactionReceipt, \
    RevertedFunctionInvocation, ResourceBoundsMapping, ResourceBounds
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.transaction_errors import TransactionFailedError


@dataclass
class StarknetAccount:
    account: str
    pub_key: Optional[str] = None
    private_key: Optional[str] = None


class StarknetSmartContract:
    def __init__(self, contract: Contract):
        self.contract = contract
        self.address = contract.address
        self._full_client: FullNodeClient = contract.client

    def prepare_calldata(self, method_name: str, *args, **kwargs) -> Call:
        prepared_call = self.contract.functions[method_name].prepare_call(*args, **kwargs)
        return Call(prepared_call.to_addr, prepared_call.selector, prepared_call.calldata)

    async def call(self, call: Call, block='pending'):
        """:param block_number: Block's number or literals `"pending"` or `"latest"`"""
        return await self.contract.client.call_contract(call, block_number=block)


class AccountExecutor:

    def __init__(self, full_node: FullNodeClient):
        self.client = full_node

    async def simulate_tx(self, call: Call, account: Account, skip_validate=True, skip_fee_charge=True,
                          nonce: int = 0,
                          max_fee=ResourceBoundsMapping.init_with_zeros(), block_number='pending') -> Tuple[bool, Union[SimulatedTransaction, Exception]]:
        try:
            tx = await account.sign_invoke_v3(call, nonce=nonce, l1_resource_bounds=max_fee.l1_gas,
                                              auto_estimate=False)
            res: SimulatedTransaction = \
                (await self.client.simulate_transactions([tx], skip_validate, skip_fee_charge,
                                                         block_number=block_number))[0]
            if isinstance(res.transaction_trace.execute_invocation, RevertedFunctionInvocation):
                return False, Exception(res.transaction_trace.execute_invocation.revert_reason)
            return True, res
        except Exception as e:
            return False, e

    async def execute_tx(self, call: Call, account: Account, nonce, max_fee) -> \
            Tuple[bool, Union[SentTransactionResponse, Exception]]:
        try:
            tx = await account.sign_invoke_v3(call, nonce=nonce, l1_resource_bounds=max_fee.l1_gas)
            res: SentTransactionResponse = await self.client.send_transaction(tx)
            return True, res
        except Exception as e:
            return False, e

    async def wait_for_tx(self, tx_hash: Union[str, int], check_interval=2, retries=100) -> Tuple[
        bool, Union[TransactionReceipt, TransactionFailedError]]:
        try:
            return True, await self.client.wait_for_tx(tx_hash, check_interval=check_interval, retries=retries)
        except TransactionFailedError as e:
            return False, e
        except Exception as e:
            logging.exception(f'Exception {e}')
            raise e
