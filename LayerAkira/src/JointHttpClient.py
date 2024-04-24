import datetime
import logging
from collections import defaultdict
from typing import Dict, Tuple, Optional, DefaultDict, List, Union

from starknet_py.hash.utils import message_signature
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from LayerAkira.src.HttpClient import AsyncApiHttpClient
from LayerAkira.src.AkiraExchangeClient import AkiraExchangeClient
from LayerAkira.src.AkiraFormatter import AkiraFormatter
from LayerAkira.src.ERC20Client import ERC20Client
from LayerAkira.src.Hasher import SnHasher
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.Requests import Withdraw, Order, OrderFlags, STPMode, Quantity, Constraints
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import precise_to_price_convert, random_int
from LayerAkira.src.common.constants import ZERO_ADDRESS
from LayerAkira.src.common.Responses import ReducedOrderInfo, OrderInfo, Snapshot, UserInfo, BBO
from LayerAkira.src.common.common import Result


class JointHttpClient:
    """
     Joint Http client for LayerAkira exchange that allow to interact with erc tokens, layer akira smart contract
     and api of exchange, maintains state internally

     Use for testing purposes
    """

    def __init__(self, node_client: FullNodeClient,
                 api_http_client: AsyncApiHttpClient,
                 akira_exchange_client: AkiraExchangeClient,
                 exchange_addr: ContractAddress,
                 erc_to_addr: Dict[ERC20Token, ContractAddress],
                 token_to_decimals: Dict[ERC20Token, int],
                 chain=StarknetChainId.GOERLI,
                 gas_multiplier=1.25,
                 exchange_version=0,
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
        self._exchange_addr = exchange_addr

        self._tokens_to_addr: Dict[ERC20Token, ContractAddress] = erc_to_addr
        self._hasher: SnHasher = SnHasher(AkiraFormatter(erc_to_addr),
                                          self.akira.akira.contract.data.parsed_abi.defined_structures)

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

        self._verbose = verbose
        self._exchange_version = exchange_version

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
            res = await self._tokens_to_erc[erc].allowance(acc_addr, self._exchange_addr)
            if res.data is None:
                logging.warning(f'Fail to query allowances due {res}')
                return res
            self._addr_to_erc_approve[acc_addr][erc] = res.data

        res = await self.akira.balancesOf([acc_addr], list(self._tokens_to_erc.keys()))
        if res.data is None:
            logging.warning(f'Fail to query exchange balance due {res}')
            return res

        exchange_balances: List[Tuple[ERC20Token, Tuple[int, int]]] = list(zip(self._tokens_to_erc.keys(), res.data))

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
            await self._tokens_to_erc[k].init()

        self.fee_recipient = (await self.akira.get_fee_recipient()).data
        assert self.fee_recipient is not None

    async def query_gas_price(self, acc: ContractAddress) -> Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        result = await self._api_client.query_gas_price(jwt)
        if result.data is not None: self.gas_price = int(result.data * self._gas_multiplier)
        return result

    async def apply_onchain_withdraw(self, acc_addr: ContractAddress, token: ERC20Token, key: int) -> Optional[str]:
        account = self._address_to_account[acc_addr]
        is_succ, result = await self.akira.apply_onchain_withdraw(account, token, key, 0, None, False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return None

        is_succ, result = await self.akira.apply_onchain_withdraw(account, token, key,
                                                                  int(result.fee_estimation.overall_fee * 1.2), None,
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
                     acc_addr)

        if self._verbose:
            logging.info(f'Withdraw hash {hex(self._hasher.hash(w))}')

        is_succ, result = await self.akira.request_onchain_withdraw(account, w, 0, None, False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return

        is_succ, result = await self.akira.request_onchain_withdraw(account, w,
                                                                    int(result.fee_estimation.overall_fee * 1.2), None,
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
        is_succ, result = await self._tokens_to_erc[token].approve(account, self._exchange_addr, amount, 0, None, False)
        if not is_succ:
            logging.info(f'Failed to simulate {result}')
            return
        is_succ, result = await self._tokens_to_erc[token].approve(account, self._exchange_addr, amount,
                                                                   int(result.fee_estimation.overall_fee * 1.2), None,
                                                                   True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def deposit_on_exchange(self, acc_addr: ContractAddress, token: ERC20Token, amount: str):
        account = self._address_to_account[acc_addr]
        amount = precise_to_price_convert(amount, self._token_to_decimals[token])
        is_succ, result = await self.akira.deposit(account, ContractAddress(account.address), token, amount, 0, None,
                                                   False)
        if not is_succ:
            logging.info(f'Failed to simulate {result}')
            return
        is_succ, result = await self.akira.deposit(account, ContractAddress(account.address), token, amount,
                                                   int(result.fee_estimation.overall_fee * 1.2), None,
                                                   True)
        if is_succ:
            logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def bind_to_signer(self, acc_addr: ContractAddress):
        """
            Simple binding of trading account acc_addr to its public key on exchange.
            So public key is responsible for generating signature for required trading activities
        """
        account = self._address_to_account[acc_addr]
        is_succ, result = await self.akira.bind_signer(account, ContractAddress(account.signer.public_key), 0, None,
                                                       False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return
        is_succ, result = await self.akira.bind_signer(account, ContractAddress(account.signer.public_key),
                                                       int(result.fee_estimation.overall_fee * 1.2), None,
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

    async def get_order(self, acc: ContractAddress, order_hash: int, mode=1) -> Result[
        Union[ReducedOrderInfo, OrderInfo]]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.get_order(acc, jwt, order_hash, mode)

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

    async def place_order(self, acc: ContractAddress, ticker: TradedPair, px: int, qty_base: int, qty_quote: int,
                          side: str, type: str,
                          post_only: bool, full_fill: bool,
                          best_lvl: bool, ecosystem: bool, maker: ContractAddress, gas_fee: GasFee,
                          router_fee: Optional[FixedFee] = None, router_signer: Optional[ContractAddress] = None,
                          stp: int = 0, external_funds=False, min_receive_amount=0) -> \
            Result[int]:
        info = self._trading_acc_to_user_info[acc]

        order_flags = OrderFlags(full_fill, best_lvl, post_only, side == 'SELL', type == 'MARKET', ecosystem,
                                 external_funds=external_funds)

        order = await self._spawn_order(acc, px=px, qty_base=qty_base, qty_quote=qty_quote, maker=maker,
                                        order_flags=order_flags, ticker=ticker,
                                        fee=OrderFee(
                                            FixedFee(self.fee_recipient, *info.fees[ticker]),
                                            FixedFee(ZERO_ADDRESS, 0, 0) if router_fee is None else router_fee,
                                            gas_fee), nonce=info.nonce,
                                        base_asset=10 ** self._token_to_decimals[ticker.base],
                                        router_signer=router_signer if router_signer is not None else ZERO_ADDRESS,
                                        stp=stp, min_receive_amount=min_receive_amount
                                        )
        if order.data is None:
            logging.warning(f'Failed to spawn order {order}')
            return order
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.place_order(jwt, order.data)

    async def cancel_order(self, acc: ContractAddress, maker: ContractAddress, order_hash: Optional[int]) -> Result[
        int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.cancel_order(pk, jwt, maker, order_hash)

    async def increase_nonce(self, acc: ContractAddress, maker: ContractAddress, new_nonce: int, gas_fee: GasFee) -> \
            Result[int]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        return await self._api_client.increase_nonce(pk, jwt, maker, new_nonce, gas_fee)

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
        order = Order(kwargs['maker'], kwargs['px'],
                      Quantity(kwargs['qty_base'], kwargs['qty_quote'], kwargs['base_asset']),
                      kwargs['ticker'], kwargs['fee'],
                      Constraints(
                          2, year_seconds, cur_ts, STPMode(kwargs['stp']), kwargs['nonce'],
                          kwargs['min_receive_amount'], kwargs.get('router_signer', ZERO_ADDRESS),
                      ),
                      random_int(),
                      kwargs['order_flags'],
                      (1, 1), (0, 0), self._exchange_version
                      )
        if order.is_passive_order():
            order.fee.router_fee = FixedFee(ZERO_ADDRESS, 0, 0)
            order.router_signer = ZERO_ADDRESS

        # router taker through router, if not explicitly specified
        if not order.flags.to_ecosystem_book and not order.is_passive_order() and order.constraints.router_signer == ZERO_ADDRESS and order.flags.external_funds:
            jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
            result = await self._api_client.query_fake_router_data(jwt, order)
            if result.data is None: return result

            order.fee.trade_fee.taker_pbips = result.data.taker_pbips
            order.fee.router_fee.recipient = result.data.fee_recipient
            order.fee.router_fee.taker_pbips = result.data.max_taker_pbips
            order.fee.router_fee.maker_pbips = result.data.maker_pbips
            order.constraints.router_signer = result.data.router_signer
            order.router_sign = result.data.router_signature

        order_hash = self._hasher.hash(order)
        order.sign = list(message_signature(order_hash, int(pk, 16)))

        return Result(order)
