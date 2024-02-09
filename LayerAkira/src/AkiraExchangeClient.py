import logging
from dataclasses import dataclass
from typing import Tuple, Dict, List, Union, TypeVar

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call, SimulatedTransaction, SentTransactionResponse
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.serialization.factory import serializer_for_outputs

from LayerAkira.src.AkiraFormatter import AkiraFormatter
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.Requests import Withdraw
from LayerAkira.src.common.StarknetEntities import AccountExecutor, StarknetSmartContract
from LayerAkira.src.common.common import Result

T = TypeVar("T")


@dataclass
class OrderTradeInfo:
    filled_amount: int
    last_traded_px: int
    num_trades_happened: int


class AkiraExchangeClient:
    """Client to interact with LayerAkira smart contract on Starknet"""

    def __init__(self, client: FullNodeClient, akira_addr: ContractAddress,
                 erc_to_addr: Dict[ERC20Token, ContractAddress]):
        self._client = client
        self.account_executor = AccountExecutor(client)
        self._akira_addr = akira_addr
        self.akira: StarknetSmartContract = None
        self._formatter = AkiraFormatter(erc_to_addr)
        self._erc_to_addr = erc_to_addr
        self._name_to_deser = {}

    async def init(self):
        self.akira = StarknetSmartContract(await Contract.from_address(self._akira_addr.as_int(), self._client))
        contract = self.akira.contract
        if hasattr(contract.data.parsed_abi, 'interfaces'):
            for v in contract.data.parsed_abi.interfaces.values():
                for name, f in v.items.items():
                    self._name_to_deser[name] = serializer_for_outputs(f.outputs).deserialize
        for k, v in contract.data.parsed_abi.functions.items():
            self._name_to_deser[k] = serializer_for_outputs(v.outputs).deserialize

    async def get_withdraw_steps(self, block='latest') -> Result[int]:
        return await self._call('get_withdraw_steps', block)

    async def get_fee_recipient(self, block='latest') -> Result[ContractAddress]:
        r = await self._call('get_fee_recipient', block)
        if r.data is not None: r.data = ContractAddress(r.data)
        return r

    async def wait_for_recipient(self, tx_hash: int, check_interval=2, retries=100):
        return await self._client.wait_for_tx(tx_hash, check_interval=check_interval, retries=retries)

    async def get_latest_gas_price(self, block='latest') -> Result[int]:
        return await self._call('get_latest_gas_price', block)

    async def balanceOf(self, addr: ContractAddress, token: ERC20Token, block='latest') -> Result[int]:
        return await self._call('balanceOf', block, addr.as_int(), self._erc_to_addr[token].as_int())

    async def balancesOf(self, addrs: List[ContractAddress], tokens: List[ERC20Token], block='latest') -> Result[
        List[List[int]]]:
        return await self._call('balancesOf', block, [x.as_int() for x in addrs],
                                [self._erc_to_addr[x].as_int() for x in tokens])

    async def total_supply(self, token: ERC20Token, block='latest') -> Result[int]:
        return await self._call('total_supply', block, self._erc_to_addr[token].as_int())

    async def get_signer(self, trader: ContractAddress, block='latest') -> Result[ContractAddress]:
        res = await self._call('get_signer', block, trader.as_int())
        if res.data is not None: res.data = ContractAddress(res.data)
        return res

    async def bind_signer(self, account: Account, pub_key: ContractAddress, max_fee: int, nonce=None,
                          on_succ_send=True):
        call = self.akira.prepare_calldata('bind_to_signer', pub_key.as_int())
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def deposit(self, account: Account, receiver: ContractAddress, token: ERC20Token, amount: int, max_fee: int,
                      nonce=None,
                      on_succ_send=True):
        call = self.akira.prepare_calldata('deposit', receiver.as_int(), self._erc_to_addr[token].as_int(), amount)
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def request_onchain_withdraw(self, account: Account, w: Withdraw, max_fee: int, nonce=None,
                                       on_succ_send=True):
        call = self.akira.prepare_calldata('request_onchain_withdraw', self._formatter.prepare_withdraw(w)['withdraw'])
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def apply_onchain_withdraw(self, account: Account, token: ERC20Token, key: int, max_fee: int, nonce=None,
                                     on_succ_send=True):
        call = self.akira.prepare_calldata('apply_onchain_withdraw', self._erc_to_addr[token].as_int(), key)
        return await self._common(call, account, max_fee, nonce, on_succ_send)

    async def get_signers(self, traders: List[ContractAddress], block='latest') -> Result[List[ContractAddress]]:
        if len(traders) == 0: return Result([])
        res = await self._call('get_signers', block, [trader.as_int() for trader in traders])
        if res.data is not None: res.data = [ContractAddress(c) for c in res.data]
        return res

    async def get_nonce(self, trader: ContractAddress, block='latest') -> Result[int]:
        return await self._call('get_nonce', block, trader.as_int())

    async def get_nonces(self, traders: List[ContractAddress], block='latest') -> Result[List[int]]:
        if len(traders) == 0: return Result([])
        return await self._call('get_nonces', block, [trader.as_int() for trader in traders])

    async def is_withdrawal_request_completed(self, w_hash: int, block='latest') -> Result[bool]:
        return await self._call('is_request_completed', block, w_hash)

    async def is_withdrawal_requests_completed(self, w_hash: List[int], block='latest') -> Result[List[bool]]:
        if len(w_hash) == 0: return Result([])
        return await self._call('is_requests_completed', block, w_hash)

    async def get_safe_trades_info(self, order_hashes: List[int], block='latest') -> Result[List[OrderTradeInfo]]:
        res = await self._call('get_safe_trades_info', block, order_hashes=order_hashes)
        if res.data is not None:
            res.data = [OrderTradeInfo(d['filled_amount'], d['last_traded_px'], d['num_trades_happened']) for d in
                        res.data]
        return res

    async def get_unsafe_trades_info(self, order_hashes: List[int], block='latest'):
        res = await self._call('get_unsafe_trades_info', block, order_hashes=order_hashes)
        if res.data is not None:
            res.data = [OrderTradeInfo(d['filled_amount'], d['last_traded_px'], d['num_trades_happened']) for d in
                        res.data]
        return res

    async def have_sufficient_amount_to_route(self, router_address: ContractAddress, block='latest'):
        return await self._call('have_sufficient_amount_to_route', block, router_address.as_int())

    async def _common(self, call, account, max_fee, nonce, on_succ_send=False, skip_sim=False):
        if skip_sim:
            return await self._execute(call, account, max_fee, nonce, on_succ_send, True)
        succ, res = await self._execute(call, account, max_fee, nonce, False, False)
        if not succ or not on_succ_send: return succ, res
        return await self._execute(call, account, max_fee, nonce, on_succ_send, True)

    async def _call(self, method_name, block, *args, **kwargs):
        try:
            return Result(self._name_to_deser[method_name](
                await self.akira.call(self.akira.prepare_calldata(method_name, *args, **kwargs), block=block))[0])
        except Exception as e:
            return Result(data=None, error_type=e, error=e.__str__())

    async def _execute(self, call: Call, account: Account, max_fee, nonce, on_succ_send=True, skip_sim=False) -> Tuple[
        bool, Union[SimulatedTransaction, SentTransactionResponse]]:
        if not skip_sim:
            succ, res = await self.account_executor.simulate_tx(call, account, True, True, nonce=nonce,
                                                                max_fee=max_fee, block_number='pending')
            if not succ:
                logging.error(f'Failed to simulate call to exchange {res}')
                return False, res
        if on_succ_send:
            return True, await self.account_executor.execute_tx(call, account, nonce, max_fee)
        return True, res
