import datetime
import logging
import time
from collections import defaultdict
from typing import Dict, Tuple, Optional, DefaultDict, List, Union

from starknet_py.hash.utils import message_signature
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import ResourceBoundsMapping
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from LayerAkira.src.AkiraExchangeClient import AkiraExchangeClient
from LayerAkira.src.ERC20Client import ERC20Client
from LayerAkira.src.HttpClient import AsyncApiHttpClient
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.ExecuteOutside import OutsideExecutionVersion, HumanReadableCall
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.Requests import SignScheme, ExecuteOutsideCall, SorContext
from LayerAkira.src.common.Requests import Withdraw, Order, OrderFlags, STPMode, Quantity, Constraints, SpotTicker
from LayerAkira.src.common.Responses import ReducedOrderInfo, OrderInfo, Snapshot, UserInfo, BBO
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import Result
from LayerAkira.src.common.common import precise_to_price_convert, random_int
from LayerAkira.src.common.constants import ZERO_ADDRESS, \
    APPROVE_SELECTOR, SNIP_9_ANY_CALLER
from LayerAkira.src.hasher.Hasher import SnTypedPedersenHasher, AppDomain
from LayerAkira.src.hasher.Snip9Formatter import Snip9Formatter


class JointHttpClient:
    """
     Joint Http client for LayerAkira exchange that allow to interact with erc tokens, layer akira smart contract
     and api of exchange, maintains state internally

     Use for testing purposes
    """

    def __init__(self, node_client: FullNodeClient,
                 api_http_client: AsyncApiHttpClient,
                 akira_exchange_client: AkiraExchangeClient,
                 core_address: ContractAddress,
                 executor_address: ContractAddress,
                 invoker_address: ContractAddress,
                 erc_to_addr: Dict[ERC20Token, ContractAddress],
                 token_to_decimals: Dict[ERC20Token, int],
                 chain=StarknetChainId.SEPOLIA,
                 gas_multiplier=1.25,
                 router_pk="",
                 verbose=False):
        """

        :param node_client:
        :param api_http_client:
        :param akira_exchange_client:
        :param exchange_addr:
        :param erc_to_addr:
        :param token_to_decimals:
        :param chain: testnet or mainnet
        :param gas_multiplier: skew parameter for gas price
        :param verbose:
        """
        self.gas_price, self.fee_recipient = 0, ZERO_ADDRESS

        self._api_client = api_http_client

        self.akira = akira_exchange_client

        self._client, self._chain, self._gas_multiplier = node_client, chain, gas_multiplier
        self._token_to_decimals = token_to_decimals
        self._executor_address = executor_address
        self._invoker_address = invoker_address
        self._core_address = core_address

        self._tokens_to_addr: Dict[ERC20Token, ContractAddress] = erc_to_addr
        self._hasher = SnTypedPedersenHasher(erc_to_addr, AppDomain(chain.value), core_address, executor_address)

        self._snip9_formatter = Snip9Formatter(akira_exchange_client, erc_to_addr)

        self._address_to_account: Dict[ContractAddress, Account] = {}
        self._tokens_to_erc: Dict[ERC20Token, ERC20Client] = {}
        self._addr_to_erc_balances: DefaultDict[ContractAddress, DefaultDict[ERC20Token, int]] = defaultdict(
            lambda: defaultdict(lambda: 0))
        self._addr_to_erc_approve: DefaultDict[ContractAddress, DefaultDict[ERC20Token, int]] = defaultdict(
            lambda: defaultdict(lambda: 0))

        self._addr_to_exchange_balances_and_nonce_and_signer: DefaultDict[
            ContractAddress, Tuple[int, DefaultDict[ERC20Token, (int, int)], ContractAddress]] = defaultdict(
            lambda: (0, defaultdict(lambda: 0), ContractAddress(ZERO_ADDRESS)))

        self._signer_key_to_pk: Dict[ContractAddress, str] = {}
        self._signer_key_to_jwt: Dict[ContractAddress, str] = {}

        self._trading_acc_to_user_info: Dict[ContractAddress, UserInfo] = defaultdict(
            lambda: UserInfo(0, defaultdict(lambda: (0, 0)), defaultdict(lambda: (0, 0))))

        self._router_pk = router_pk
        self._verbose = verbose

    async def handle_new_keys(self, acc_addr: ContractAddress, pub: ContractAddress, priv: str):
        """
            Adds account address to client and initialize it onchain info data
        """
        if acc_addr in self._address_to_account:
            logging.info(f'WARN:Account {acc_addr} already set')
        account = Account(address=acc_addr.as_int(), client=self._client,
                          key_pair=KeyPair(private_key=int(priv, 16), public_key=pub.as_int()),
                          chain=self._chain)
        self._address_to_account[acc_addr] = account
        self._signer_key_to_pk[pub] = priv
        await self.refresh_onchain_balances_and_nonce_and_signer(acc_addr)

    async def refresh_onchain_balances_and_nonce_and_signer(self, acc_addr: ContractAddress):
        for erc, token in self._tokens_to_addr.items():
            res = await self._tokens_to_erc[erc].balanceOf(acc_addr)
            if res.data is None:
                logging.warning(f'Fail to query erc balances due {res}')
                return res

            self._addr_to_erc_balances[acc_addr][erc] = res.data
            res = await self._tokens_to_erc[erc].allowance(acc_addr, self._core_address)
            if res.data is None:
                logging.warning(f'Fail to query allowances due {res}')
                return res
            self._addr_to_erc_approve[acc_addr][erc] = res.data

        res = await self.akira.balancesOf([acc_addr], list(self._tokens_to_erc.keys()))
        if res.data is None:
            logging.warning(f'Fail to query exchange balance due {res}')
            return res

        exchange_balances: List[Tuple[ERC20Token, Tuple[int, int]]] = list(zip(self._tokens_to_erc.keys(), res.data[0]))

        res = await self.akira.get_nonce(acc_addr)
        if res.data is None:
            logging.warning(f'Fail to query nonce due {res}')
            return res

        signer_d = await self.akira.get_signer(acc_addr)
        if signer_d.data is None:
            logging.warning(f'Fail to query signer due {res}')
            return signer_d
        nonce, signer = res.data, signer_d.data

        self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr] = (nonce, defaultdict(lambda: (0, 0)), signer)
        for token, amounts in exchange_balances:
            self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr][1][token] = amounts
        await self.display_chain_info(acc_addr)
        return self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr]

    async def init(self):
        for k, v in self._tokens_to_addr.items():
            self._tokens_to_erc[k] = ERC20Client(self._client, v)

        self.fee_recipient = await self.akira.get_fee_recipient()
        assert self.fee_recipient.data is not None, f'Failed to query fee recipient: {self.fee_recipient}'
        self.fee_recipient = ContractAddress(self.fee_recipient.data)

    async def query_gas_price(self, acc: ContractAddress) -> Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        result = await self._api_client.query_gas_price(jwt)
        if result.data is not None: self.gas_price = int(result.data * self._gas_multiplier)
        return result

    async def get_conversion_rate(self, acc: ContractAddress, token: ERC20Token) -> Result[Tuple[int, int]]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_conversion_rate(token, jwt)

    async def apply_onchain_withdraw(self, acc_addr: ContractAddress, token: ERC20Token, key: int) -> Optional[str]:
        account = self._address_to_account[acc_addr]
        is_succ, result = await self.akira.apply_onchain_withdraw(account, token, key,
                                                                  ResourceBoundsMapping.init_with_zeros(),
                                                                  None, False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return None

        is_succ, result = await self.akira.apply_onchain_withdraw(account, token, key,
                                                                  result.fee_estimation.to_resource_bounds(),
                                                                  None,
                                                                  True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')
            return None

    async def request_withdraw_on_chain(self, acc_addr: ContractAddress, token: ERC20Token, amount: str) -> Optional[
        Tuple[str, str]]:
        account = self._address_to_account[acc_addr]
        w_steps = await self.akira.get_withdraw_steps()
        gas_price = await self.akira.get_latest_gas_price()
        if w_steps.data is None or w_steps.data is None:
            logging.warning(f'Failed to get w_steps and gas_price due {w_steps} {gas_price}')
            return None
        amount = precise_to_price_convert(amount, self._token_to_decimals[token])
        w = Withdraw(acc_addr, token, amount, random_int(), (0, 0),
                     GasFee(w_steps.data, ERC20Token.ETH, 2 * gas_price.data, (1, 1)),
                     ## onchain requires x2 gas
                     acc_addr, SignScheme.NOT_SPECIFIED)

        if self._verbose:
            logging.info(f'Withdraw hash {hex(self._hasher.hash(w))}')

        is_succ, result = await self.akira.request_onchain_withdraw(account, w,
                                                                    ResourceBoundsMapping.init_with_zeros(),
                                                                    None, False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return

        is_succ, result = await self.akira.request_onchain_withdraw(account, w,
                                                                    result.fee_estimation.to_resource_bounds(),
                                                                    None,
                                                                    True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(self._hasher.hash(w)), hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def display_chain_info(self, acc_addr: ContractAddress) -> bool:
        if acc_addr not in self._address_to_account:
            logging.warning(f'We dont track {acc_addr}')
            return False
        print('Balances:')
        for k, v in self._addr_to_erc_balances[acc_addr].items():
            print(f'{k.name}:{v}')
        print('Approve:')
        for k, v in self._addr_to_erc_approve[acc_addr].items():
            print(f'{k.name}:{v}')
        nonce, balances, signer = self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr]
        print(f'Balances on exchange: (nonce is {nonce}, signer is {signer})')
        for k, v in balances.items():
            print(f'{k.name}:{v}')
        return True

    async def approve_exchange(self, acc_addr: ContractAddress, token: ERC20Token, amount: str):
        account = self._address_to_account[acc_addr]
        amount = precise_to_price_convert(amount, self._token_to_decimals[token])
        is_succ, result = await self._tokens_to_erc[token].approve(account, self._core_address, amount,
                                                                   ResourceBoundsMapping.init_with_zeros(),
                                                                   None, False)
        if not is_succ:
            logging.info(f'Failed to simulate {result}')
            return
        is_succ, result = await self._tokens_to_erc[token].approve(account, self._core_address, amount,
                                                                   result.fee_estimation.to_resource_bounds(), None,
                                                                   True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def deposit_on_exchange(self, acc_addr: ContractAddress, token: ERC20Token, amount: str):
        account = self._address_to_account[acc_addr]
        amount = precise_to_price_convert(amount, self._token_to_decimals[token])
        is_succ, result = await self.akira.deposit(account, ContractAddress(account.address), token, amount,
                                                   ResourceBoundsMapping.init_with_zeros(),
                                                   None,
                                                   False)
        if not is_succ:
            logging.info(f'Failed to simulate {result}')
            return
        is_succ, result = await self.akira.deposit(account, ContractAddress(account.address), token, amount,
                                                   result.fee_estimation.to_resource_bounds(),
                                                   None,
                                                   True)
        if is_succ:
            logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def approve_executor(self, acc_addr: ContractAddress):
        account = self._address_to_account[acc_addr]
        is_succ, result = await self.akira.approve_executor(account, ResourceBoundsMapping.init_with_zeros(),
                                                            None,
                                                            False)
        if not is_succ:
            logging.info(f'Failed to simulate {result}')
            return
        is_succ, result = await self.akira.approve_executor(account,
                                                            result.fee_estimation.to_resource_bounds(),
                                                            None,
                                                            True)
        if is_succ:
            logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    # approve_executor
    async def bind_to_signer(self, acc_addr: ContractAddress):
        """
            Simple binding of trading account acc_addr to its public key on exchange.
            So public key is responsible for generating signature for required trading activities
        """
        account = self._address_to_account[acc_addr]
        is_succ, result = await self.akira.bind_signer(account, ContractAddress(account.signer.public_key),
                                                       ResourceBoundsMapping.init_with_zeros(), None,
                                                       False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return
        is_succ, result = await self.akira.bind_signer(account, ContractAddress(account.signer.public_key),
                                                       result.fee_estimation.to_resource_bounds(), None,
                                                       True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def issue_jwt(self, acc: ContractAddress) -> Result[str]:
        signer = ContractAddress(self._address_to_account[acc].signer.public_key)
        pk = self._signer_key_to_pk[signer]
        jwt_result = await self._api_client.issue_jwt(signer, pk, acc, self._chain.value)
        if jwt_result.data is None: return jwt_result
        self._signer_key_to_jwt[signer] = jwt_result.data
        return jwt_result

    async def get_trading_acc_info(self, acc: ContractAddress) -> Result[UserInfo]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        result = await self._api_client.get_trading_acc_info(acc, jwt)
        if result.data is None: return result
        self._trading_acc_to_user_info[acc] = result.data

        if self._verbose:
            logging.info(f'Acc {acc}, nonce {result.data.nonce}, '
                         f'balances: {[token.name + ":" + str(b[0]) + "," + str(b[1]) for token, b in result.data.balances.items()]},'
                         f', fees:{[str(p) + ":" + str(b) for p, b in result.data.fees.items()]}')
        return result

    async def get_order(self, acc: ContractAddress, order_hash: int, active = 1, mode=1) -> Result[
        Union[ReducedOrderInfo, OrderInfo]]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_order(acc, jwt, order_hash, active, mode)

    async def get_order_router(self, acc: ContractAddress, t_acc: ContractAddress, order_hash: int, active = 1, mode=1) -> Result[
        Union[ReducedOrderInfo, OrderInfo]]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_order_router(acc, jwt, t_acc, order_hash, active, mode)

    async def get_orders(self, acc: ContractAddress, mode: int = 1, limit=20, offset=0) -> Result[
        List[Union[ReducedOrderInfo, OrderInfo]]]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_orders(acc, jwt, mode, limit, offset)

    async def get_bbo(self, acc, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[BBO]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_bbo(jwt, base, quote, ecosystem_book)

    async def get_snapshot(self, acc, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[Snapshot]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_snapshot(jwt, base, quote, ecosystem_book)

    async def place_order(self,
                          acc: ContractAddress,
                          ticker: TradedPair,
                          px: int,
                          qty_base: int,
                          qty_quote: int,
                          side: str,
                          type: str,
                          post_only: bool,
                          full_fill: bool,
                          best_lvl: bool,
                          ecosystem: bool,
                          maker: ContractAddress,
                          gas_fee: GasFee,
                          router_fee: Optional[FixedFee] = None,
                          router_signer: Optional[ContractAddress] = None,
                          stp: int = 0,
                          external_funds=False,
                          min_receive_amount=0,
                          apply_fixed_fees_to_receipt=True,
                          snip_9: bool = False,
                          caller: Optional[ContractAddress] = None,
                          sor_context: Optional[SorContext] = None,
                          ) -> \
            Result[str]:
        info = self._trading_acc_to_user_info[acc]

        order_flags = OrderFlags(full_fill, best_lvl, post_only, side == 'SELL', type == 'MARKET', ecosystem,
                                 external_funds=external_funds)

        order = await self._spawn_order(
            acc, px=px, qty_base=qty_base, qty_quote=qty_quote, maker=maker,
            order_flags=order_flags, ticker=ticker,
            fee=OrderFee(
                FixedFee(self.fee_recipient, *info.fees[ticker],
                         ),
                FixedFee(ZERO_ADDRESS, 0, 0,
                         ) if router_fee is None else router_fee,
                gas_fee,
                apply_to_receipt_amount=apply_fixed_fees_to_receipt), nonce=info.nonce if info.nonce is not None else 0,
            base_asset=10 ** self._token_to_decimals[ticker.base],
            router_signer=router_signer if router_signer is not None else ZERO_ADDRESS,
            stp=stp, min_receive_amount=min_receive_amount, snip_9=snip_9,
            sor_context=sor_context
        )
        if order.data is None:
            logging.warning(f'Failed to spawn order {order}')
            return order

        if snip_9:
            snip9_calldata = await self._spawn_snip_9_calldata(
                order=order.data,
                caller=caller
            )

            if snip9_calldata is not None:
                order.data.snip9_calldata = snip9_calldata
                await self._sign_snip_9(acc, order.data)

        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.place_order(jwt, order.data)

    async def cancel_order(self, acc: ContractAddress, maker: ContractAddress, order_hash: int,
                           sign_scheme: SignScheme.ECDSA) -> Result[
        int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.cancel_order(pk, jwt, maker, order_hash, sign_scheme)

    async def cancel_all_orders(self, acc: ContractAddress, maker: ContractAddress, ticker: SpotTicker,
                                sign_scheme=SignScheme.ECDSA) -> Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.cancel_all_orders(pk, jwt, maker, ticker, sign_scheme)

    async def increase_nonce(self, acc: ContractAddress, maker: ContractAddress, new_nonce: int, gas_fee: GasFee,
                             sign_scheme=SignScheme.ECDSA) -> \
            Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.increase_nonce(pk, jwt, maker, new_nonce, gas_fee, sign_scheme)

    async def withdraw(self, acc: ContractAddress, maker: ContractAddress, token: ERC20Token, amount: int,
                       gas_fee: GasFee) -> Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.withdraw(pk, jwt, maker, token, amount, gas_fee)

    async def query_listen_key(self, signer: ContractAddress):
        jwt = self._signer_key_to_jwt[signer]
        return await self._api_client.query_listen_key(jwt)

    async def _spawn_order(self, acc: ContractAddress, **kwargs) -> Result[Order]:
        signer_pub_key = ContractAddress(self._address_to_account[acc].signer.public_key)
        pk = self._signer_key_to_pk[signer_pub_key]
        cur_ts = int(datetime.datetime.now().timestamp())
        year_seconds = 60 * 60 * 24 * 365
        if kwargs['snip_9']:
            sign_scheme = SignScheme.DIRECT
        else:
            sign_scheme = SignScheme.ECDSA if not kwargs['order_flags'].external_funds else SignScheme.ACCOUNT
        order = Order(kwargs['maker'], kwargs['px'],
                      Quantity(kwargs['qty_base'], kwargs['qty_quote'], kwargs['base_asset']),
                      kwargs['ticker'], kwargs['fee'],
                      Constraints(
                          2, year_seconds, cur_ts, STPMode(kwargs['stp']), kwargs['nonce'],
                          kwargs['min_receive_amount'], kwargs.get('router_signer', ZERO_ADDRESS),
                      ),
                      random_int(),
                      kwargs['order_flags'],
                      (1, 1), (0, 0),
                      sign_scheme=sign_scheme,
                      sor_ctx=kwargs['sor_context'],
                      )

        order.sor_ctx.order_fee = order.fee
        if order.is_passive_order():
            order.fee.router_fee = FixedFee(ZERO_ADDRESS, 0, 0)
            order.router_signer = ZERO_ADDRESS

        # router taker through router, if not explicitly specified
        if not order.flags.to_ecosystem_book and not order.is_passive_order() and order.constraints.router_signer == ZERO_ADDRESS and order.flags.external_funds:
            jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
            result = await self._api_client.query_router_details(jwt)
            if result.data is None: return result
            order.fee.router_fee.recipient = result.data.fee_recipient
            order.fee.router_fee.taker_pbips = result.data.taker_pbips
            order.fee.router_fee.maker_pbips = result.data.maker_pbips
            order.constraints.router_signer = result.data.router_signer
            order.router_sign = (0, 0)

        order_hash = self._hasher.hash(order)
        order.sign = list(message_signature(order_hash, int(pk, 16)))

        return Result(order)

    async def _spawn_snip_9_calldata(self,
                                     order: Order,
                                     caller: ContractAddress,
                                     valid_since_now_seconds=60 * 15
                                     ) -> Optional[ExecuteOutsideCall]:
        calls = await self._spawn_snip_9_calls(
            order=order
        )
        account = self._address_to_account[order.maker]
        nonce = await account.get_outside_execution_nonce()

        signature = [0, 0]

        snip_9_calldata = ExecuteOutsideCall(
            caller=caller,
            calls=calls,
            execute_after=int(time.time()) - valid_since_now_seconds,
            execute_before=int(time.time()) + valid_since_now_seconds,
            nonce=nonce,
            signature=signature,
            maker=order.maker,
            version=OutsideExecutionVersion.V2.value
        )

        return snip_9_calldata

    async def _spawn_snip_9_calls(self,
                                  order: Order,
                                  ) -> List[HumanReadableCall]:

        calls = []

        spending_token = order.ticker.base if order.side == 'SELL' else order.ticker.quote

        if spending_token == order.ticker.base:
            if order.qty.base_qty == 0:
                qty = (order.qty.quote_qty * self._token_to_decimals[order.ticker.base]) / order.price
                spending_amount = int(qty)
            else:
                spending_amount = int(order.qty.base_qty)
        else:
            if order.qty.base_qty == 0:
                spending_amount = int(order.qty.quote_qty)
            else:
                qty = (order.qty.base_qty * order.price) / self._token_to_decimals[order.ticker.base]
                spending_amount = int(qty)

        erc_address = self._tokens_to_addr[spending_token]

        approve_call = HumanReadableCall(
            to=erc_address,
            selector=APPROVE_SELECTOR,
            args=[self._executor_address.as_str(), hex(spending_amount)],
            kwargs={}
        )

        calls.append(approve_call)

        # place_order_call_data = build_order_calldata(order, self._tokens_to_addr)
        #
        # place_order_call = HumanReadableCall(
        #     to=self._executor_address,
        #     selector=PLACE_TAKER_ORDER_SELECTOR,
        #     args=[],
        #     kwargs=place_order_call_data,
        # )
        #
        # calls.append(place_order_call)

        return calls

    async def _sign_snip_9(self, acc: ContractAddress, order: Order):

        order_hash = self._hasher.hash(order)
        router_sign = list(message_signature(order_hash, int(self._router_pk, 16)))

        snip9_order_match = self._snip9_formatter.get_snip9_order_match(order, router_sign)

        hash = self._hasher.hash(snip9_order_match)

        signer_pub_key = ContractAddress(self._address_to_account[acc].signer.public_key)
        pk = self._signer_key_to_pk[signer_pub_key]

        signature = list(message_signature(hash, int(pk, 16)))

        order.snip9_calldata.signature = signature

        # # remove placeTakerOrder
        # order.snip9_calldata.calls.pop()
