import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple, Dict, List, Union, TypeVar, Any

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, SimulatedTransaction, SentTransactionResponse, \
    ResourceBoundsMapping
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.serialization.factory import serializer_for_outputs

from LayerAkira.src.AkiraFormatter import AkiraFormatter
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.Requests import Withdraw
from LayerAkira.src.common.StarknetEntities import AccountExecutor, StarknetSmartContract
from LayerAkira.src.common.common import Result
from LayerAkira.src.abi import core_abi, router_abi, executor_abi

T = TypeVar("T")


@dataclass
class OrderTradeInfo:
    filled_base_amount: int
    filled_quote_amount: int
    last_traded_px: int
    num_trades_happened: int
    as_taker_completed: bool


class AkiraExchangeClient:
    """Client to interact with LayerAkira smart contract on Starknet"""

    # TODO here:
    def __init__(self, client: FullNodeClient,
                 core_address: ContractAddress,
                 executor_address: ContractAddress,
                 router_address: ContractAddress,
                 erc_to_addr: Dict[ERC20Token, ContractAddress],
                 account_executor: AccountExecutor = None):
        self.client = client

        self.core_address = core_address
        self.executor_address = executor_address
        self.router_address = router_address
        self.core = StarknetSmartContract(Contract(self.core_address.as_int(), core_abi, self.client, cairo_version=1))
        self.router = StarknetSmartContract(
            Contract(self.router_address.as_int(), router_abi, self.client, cairo_version=1))
        self.executor = StarknetSmartContract(
            Contract(self.executor_address.as_int(), executor_abi, self.client, cairo_version=1))

        if account_executor is None:
            self._account_executor = AccountExecutor(client)
        else:
            self._account_executor = account_executor
        self._formatter = AkiraFormatter(erc_to_addr)
        self._erc_to_addr = erc_to_addr
        self._name_to_deser: Dict[int, Dict[Any]] = defaultdict(lambda: {})

    async def init(self):
        for contract in [self.core.contract, self.router.contract, self.executor.contract]:
            addr = contract.address
            if hasattr(contract.data.parsed_abi, 'interfaces'):
                for v in contract.data.parsed_abi.interfaces.values():
                    for name, f in v.items.items():
                        self._name_to_deser[addr][name] = serializer_for_outputs(f.outputs).deserialize
            for k, v in contract.data.parsed_abi.functions.items():
                self._name_to_deser[addr][k] = serializer_for_outputs(v.outputs).deserialize

    async def get_fee_recipient(self, block='latest') -> Result[str]:
        r = await self._call(self.core, 'get_fee_recipient', block)
        if r.data is not None: r.data = hex(r.data)
        return r

    async def wait_for_recipient(self, tx_hash: int, check_interval=2, retries=100):
        return await self.client.wait_for_tx(tx_hash, check_interval=check_interval, retries=retries)

    async def balanceOf(self, addr: ContractAddress, token: ERC20Token, block='latest') -> Result[int]:
        return await self._call(self.core, 'balanceOf', block, addr.as_int(), self._erc_to_addr[token].as_int())

    async def balancesOf(self, addrs: List[ContractAddress], tokens: List[ERC20Token], block='latest') -> Result[
        List[List[int]]]:
        return await self._call(self.core, 'balancesOf', block, [x.as_int() for x in addrs],
                                [self._erc_to_addr[x].as_int() for x in tokens])

    async def total_supply(self, token: ERC20Token, block='latest') -> Result[int]:
        return await self._call(self.core, 'total_supply', block, self._erc_to_addr[token].as_int())

    async def get_signer(self, trader: ContractAddress, block='latest') -> Result[ContractAddress]:
        res = await self._call(self.core, 'get_signer', block, trader.as_int())
        if res.data is not None: res.data = ContractAddress(res.data)
        return res

    async def get_signers(self, traders: List[ContractAddress], block='latest') -> Result[List[ContractAddress]]:
        if len(traders) == 0: return Result([])
        res = await self._call(self.core, 'get_signers', block, [trader.as_int() for trader in traders])
        if res.data is not None: res.data = [ContractAddress(c) for c in res.data]
        return res

    async def get_nonce(self, trader: ContractAddress, block='latest') -> Result[int]:
        return await self._call(self.core, 'get_nonce', block, trader.as_int())

    async def get_nonces(self, traders: List[ContractAddress], block='latest') -> Result[List[int]]:
        if len(traders) == 0: return Result([])
        return await self._call(self.core, 'get_nonces', block, [trader.as_int() for trader in traders])

    async def is_withdrawal_request_completed(self, w_hash: int, block='latest') -> Result[bool]:
        return await self._call(self.core, 'is_request_completed', block, w_hash)

    async def is_withdrawal_requests_completed(self, w_hash: List[int], block='latest') -> Result[List[bool]]:
        if len(w_hash) == 0: return Result([])
        return await self._call(self.core, 'is_requests_completed', block, w_hash)

    async def get_ecosystem_trades_info(self, order_hashes: List[int], block='latest') -> Result[List[OrderTradeInfo]]:
        res = await self._call(self.executor, 'get_ecosystem_trades_info', block, order_hashes=order_hashes)
        if res.data is not None:
            res.data = [OrderTradeInfo(d['filled_base_amount'], d['filled_quote_amount'],
                                       d['last_traded_px'], d['num_trades_happened'],
                                       d['as_taker_completed']) for d in
                        res.data]
        return res

    async def have_sufficient_amount_to_route(self, router_address: ContractAddress, block='latest'):
        return await self._call(self.router, 'have_sufficient_amount_to_route', block, router_address.as_int())

    async def get_withdraw_steps(self, block='pending') -> Result[int]:
        return await self._call(self.core, 'get_withdraw_steps', block)

    async def _common(self, call, account, max_fee, nonce, on_succ_send=False, skip_sim=False):
        if skip_sim:
            return await self._execute(call, account, max_fee, nonce, on_succ_send, True)
        succ, res = await self._execute(call, account, max_fee, nonce, False, False)
        if not succ or not on_succ_send: return succ, res
        return await self._execute(call, account, max_fee, nonce, on_succ_send, True)

    async def get_latest_gas_price(self, block='pending') -> Result[int]:
        return await self._call(self.core, 'get_latest_gas_price', block)

    async def bind_signer(self, account: Account, pub_key: ContractAddress,
                          max_fee: ResourceBoundsMapping,
                          nonce=None,
                          on_succ_send=True):
        call = self.core.prepare_calldata('bind_to_signer', pub_key.as_int())
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def deposit(self, account: Account, receiver: ContractAddress, token: ERC20Token, amount: int,
                      max_fee: ResourceBoundsMapping,
                      nonce=None,
                      on_succ_send=True):
        call = self.core.prepare_calldata('deposit', receiver.as_int(), self._erc_to_addr[token].as_int(), amount)
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def approve_executor(self, account: Account, max_fee: ResourceBoundsMapping, nonce=None, on_succ_send=True):
        call = self.core.prepare_calldata('grant_access_to_executor')
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def request_onchain_withdraw(self, account: Account, w: Withdraw,
                                       max_fee: ResourceBoundsMapping,
                                       nonce=None,
                                       on_succ_send=True):
        call = self.core.prepare_calldata('request_onchain_withdraw', self._formatter.prepare_withdraw(w)['withdraw'])
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def apply_onchain_withdraw(self, account: Account, token: ERC20Token, key: int,
                                     max_fee: ResourceBoundsMapping,
                                     nonce=None,
                                     on_succ_send=True):
        call = self.core.prepare_calldata('apply_onchain_withdraw', self._erc_to_addr[token].as_int(), key)
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def _call(self, contract: StarknetSmartContract, method_name, block, *args, **kwargs):
        try:
            return Result(self._name_to_deser[contract.address][method_name](
                await contract.call(contract.prepare_calldata(method_name, *args, **kwargs), block=block))[0])
        except Exception as e:
            return Result(data=None, error_type=e, error=e.__str__())

    async def _execute(self, call: Call, account: Account, max_fee, nonce, on_succ_send=True, skip_sim=False) -> Tuple[
        bool, Union[SimulatedTransaction, SentTransactionResponse]]:
        if not skip_sim:
            succ, res = await self._account_executor.simulate_tx(call, account, True, True, nonce=nonce,
                                                                 max_fee=max_fee, block_number='pending')
            if not succ:
                logging.error(f'Failed to simulate call to exchange {res}')
                return False, res
        if on_succ_send:
            return await self._account_executor.execute_tx(call, account, nonce, max_fee)
        return True, res
