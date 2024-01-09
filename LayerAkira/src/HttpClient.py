import datetime
import logging
from collections import defaultdict
from dataclasses import dataclass
from random import random
from typing import Dict, Tuple, Optional, DefaultDict, List, Any

from aiohttp import ClientSession
from starknet_py.hash.utils import message_signature
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.ERC20Client import ERC20Client
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.FixedPoint import FixedPoint, precise_to_price_convert
from LayerAkira.src.Hasher import SnHasher
from LayerAkira.src.OrderSerializer import SimpleOrderSerializer
from LayerAkira.src.common.Requests import Withdraw, Order, CancelRequest, OrderFlags
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.constants import ZERO_ADDRESS
from LayerAkira.src.AkiraExchangeClient import AkiraExchangeClient
from LayerAkira.src.AkiraFormatter import AkiraFormatter


def random_int(to=100000000):
    return abs(int(random() * to))


def GAS_FEE_ACTION(gas: int, fix_steps):
    return GasFee(fix_steps, ERC20Token.ETH, FixedPoint(gas, 18), (1, 1))


class HttpClient:
    """
     Http client for LayerAkira exchange
    """

    @dataclass
    class UserInfo:
        nonce: int
        fees: DefaultDict[TradedPair, Tuple[int, int]]
        balances: DefaultDict[ERC20Token, Tuple[int, int]]

    def __init__(self, client: FullNodeClient, exchange_addr: ContractAddress,
                 tokens_to_addr: Dict[ERC20Token, ContractAddress],
                 token_to_decimals: Dict[ERC20Token, int],
                 chain=StarknetChainId.TESTNET, exchange_http_host='http://localhost:8080',
                 gas_multiplier=1.25,
                 verbose=False):
        """

        :param client:
        :param exchange_addr:
        :param tokens_to_addr:
        :param token_to_decimals:
        :param chain:
        :param exchange_http_host:
        :param exchange_wss_host:
        :param gas_multiplier:
        :param verbose:
        """
        self.gas_price, self.fee_recipient = 0, ZERO_ADDRESS
        self.akira = AkiraExchangeClient(client, exchange_addr, tokens_to_addr)

        self._client, self._http, self._chain, self._gas_multiplier = client, ClientSession(), chain, gas_multiplier
        self._token_to_decimals, self._formatter = token_to_decimals, AkiraFormatter(tokens_to_addr)
        self._exchange_addr, self._http_host = exchange_addr, exchange_http_host

        self._order_serder = SimpleOrderSerializer(tokens_to_addr)
        self.hasher: SnHasher = None
        self._tokens_to_addr: Dict[ERC20Token, ContractAddress] = tokens_to_addr
        self._addr_to_token: Dict[ContractAddress, ERC20Token] = {v: k for k, v in tokens_to_addr.items()}

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

        self._trading_acc_to_user_info: Dict[ContractAddress, HttpClient.UserInfo] = defaultdict(
            lambda: HttpClient.UserInfo(0, defaultdict(lambda: (0, 0)), defaultdict(lambda: (0, 0))))

        self._verbose = verbose

    async def init(self):
        await self.akira.init()
        self.hasher = SnHasher(AkiraFormatter(self._tokens_to_addr),
                               self.akira.akira.contract.data.parsed_abi.defined_structures)

        for k, v in self._tokens_to_addr.items():
            self._tokens_to_erc[k] = ERC20Client(self._client, v)
            await self._tokens_to_erc[k].init()

        self.fee_recipient = (await self.akira.get_fee_recipient()).data
        assert self.fee_recipient is not None

    async def query_gas_price(self, acc: ContractAddress) -> int:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        result = await self._get_query(f'{self._http_host}/gas/price', jwt)
        self.gas_price = int(result['result'] * self._gas_multiplier)  # skew on x pct
        return self.gas_price

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
        w = Withdraw(acc_addr, token, FixedPoint(amount, 0), random_int(), (0, 0),
                     GasFee(w_steps.data, ERC20Token.ETH, FixedPoint(2 * gas_price.data, 0), (1, 1)),
                     ## onchain requires x2 gas
                     acc_addr)

        if self._verbose:
            logging.info(f'Withdraw hash {hex(self.hasher.hash(w))}')

        is_succ, result = await self.akira.request_onchain_withdraw(account, w, 0, None, False)
        if not is_succ:
            logging.warning(f'Failed to simulate {result}')
            return

        is_succ, result = await self.akira.request_onchain_withdraw(account, w,
                                                                    int(result.fee_estimation.overall_fee * 1.2), None,
                                                                    True)
        if is_succ:
            if self._verbose: logging.info(f'Sent transaction {hex(result.transaction_hash)}')
            return hex(self.hasher.hash(w)), hex(result.transaction_hash)
        else:
            logging.warning(f'Failed to sent tx due {result}')

    async def handle_new_keys(self, acc_addr: ContractAddress, pub: ContractAddress, priv: str):
        if acc_addr in self._address_to_account:
            logging.info(f'WARN:Account {acc_addr} already set')
        account = Account(address=acc_addr.as_int(), client=self._client,
                          key_pair=KeyPair(private_key=priv, public_key=pub.as_int()),
                          chain=self._chain)
        self._address_to_account[acc_addr] = account
        self._signer_key_to_pk[pub] = priv
        await self.refresh_onchain_balances_and_nonce_and_signer(acc_addr)

    async def refresh_onchain_balances_and_nonce_and_signer(self, acc_addr: ContractAddress):
        for erc, token in self._tokens_to_addr.items():
            res = await self._tokens_to_erc[erc].balanceOf(acc_addr)
            if res.data is None: raise Exception(f'WARNING:FAIL to init due {res}')
            self._addr_to_erc_balances[acc_addr][erc] = res.data

            res = await self._tokens_to_erc[erc].allowance(acc_addr, self._exchange_addr)
            if res.data is None: raise Exception(f'WARNING:FAIL to init due {res}')
            self._addr_to_erc_approve[acc_addr][erc] = res.data

        res = await self.akira.balancesOf([acc_addr], list(self._tokens_to_erc.keys()))
        if res.data is None: raise Exception(f'WARNING:FAIL to init due {res}')
        exchange_balances: List[Tuple[ERC20Token, Tuple[int, int]]] = list(zip(self._tokens_to_erc.keys(), res.data))

        res = await self.akira.get_nonce(acc_addr)
        if res.data is None: raise Exception(f'WARNING:FAIL to init due {res}')
        signer_d = await self.akira.get_signer(acc_addr)
        if signer_d.data is None: raise Exception(f'WARNING:FAIL to init due {signer_d}')
        nonce, signer = res.data, signer_d.data

        self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr] = (nonce, defaultdict(lambda: (0, 0)), signer)
        for token, amounts in exchange_balances:
            self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr][1][token] = amounts
        await self.display_chain_info(acc_addr)
        return self._addr_to_exchange_balances_and_nonce_and_signer[acc_addr]

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

    async def issue_jwt(self, acc: ContractAddress) -> Optional[str]:
        signer = ContractAddress(self._address_to_account[acc].signer.public_key)
        pk = self._signer_key_to_pk[signer]
        url = f'{self._http_host}/sign/request_sign_data?user={signer}'
        if self._verbose: logging.info(f'GET request to {url}')
        msg = await self._http.get(f'{self._http_host}/sign/request_sign_data?user={signer}')
        if self._verbose: logging.info(f'Response json: {await msg.json()} and status code {msg.status}')
        msg, url = (await msg.json())['result'], f'{self._http_host}/sign/auth'

        resp = await self._post_query(url,
                                      {'msg': int(msg), 'signature': list(message_signature(int(msg), int(pk, 16)))})
        self._signer_key_to_jwt[signer] = resp['result']
        return self._signer_key_to_jwt[signer]

    async def get_trading_acc_info(self, acc: ContractAddress) -> Dict[ContractAddress, Any]:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        url = f'{self._http_host}/user/user_info?trading_account={acc}'
        info = (await self._get_query(url, jwt))['result']

        self._trading_acc_to_user_info[acc].nonce = info['nonce']
        local_info = self._trading_acc_to_user_info[acc]
        fees_d = local_info.fees

        for pair, fees in info['fees']:
            fees_d[TradedPair(self._addr_to_token[ContractAddress(pair[0])],
                              self._addr_to_token[ContractAddress(pair[1])])] = fees
        balances = local_info.balances
        for token, total, locked in info['balances']:
            balances[self._addr_to_token[ContractAddress(token)]] = (total, locked)

        self._trading_acc_to_user_info[acc] = local_info
        if self._verbose:
            logging.info(f'Acc {acc}, nonce {local_info.nonce}, '
                         f'balances: {[token.name + ":" + str(b[0]) + "," + str(b[1]) for token, b in local_info.balances.items()]},'
                         f', fees:{[str(p) + ":" + str(b) for p, b in fees_d.items()]}')
        return self._trading_acc_to_user_info[acc]

    async def get_order(self, acc: ContractAddress, order_hash: int) -> Dict:
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        url = f'{self._http_host}/user/order?order_hash={order_hash}&trading_account={acc}'
        return (await self._get_query(url, jwt))

    async def get_orders(self, acc: ContractAddress, mode: int = 1, limit=20, offset=0):
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        url = f'{self._http_host}/user/orders?mode={mode}&trading_account={acc}&limit={limit}&offset={offset}'
        return (await self._get_query(url, jwt))

    async def get_bbo(self, acc, base: ERC20Token, quote: ERC20Token, safe_book: bool):
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        url = f'{self._http_host}/book/bbo?base={self._tokens_to_addr[base]}&quote={self._tokens_to_addr[quote]}&to_safe_book={int(safe_book)}'
        return (await self._get_query(url, jwt))

    async def get_snapshot(self, acc, base: ERC20Token, quote: ERC20Token, safe_book: bool):
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        url = f'{self._http_host}/book/snapshot?base={self._tokens_to_addr[base]}&quote={self._tokens_to_addr[quote]}&to_safe_book={int(safe_book)}'
        return (await self._get_query(url, jwt))

    def spawn_order(self, acc: ContractAddress, **kwargs):
        signer_pub_key = ContractAddress(self._address_to_account[acc].signer.public_key)
        pk = self._signer_key_to_pk[signer_pub_key]
        order = Order(kwargs['maker'], FixedPoint(kwargs['px'], 0), FixedPoint(kwargs['qty'], 0),
                      kwargs['ticker'], kwargs['fee'], 2, random_int(), kwargs['nonce'],
                      kwargs['order_flags'], kwargs.get('router_signer', ZERO_ADDRESS),
                      kwargs['base_asset'], (0, 0), (0, 0), int(datetime.datetime.now().timestamp()),
                      )
        if order.is_passive_order():
            order.fee.router_fee = FixedFee(ZERO_ADDRESS, 0, 0)
            order.router_signer = ZERO_ADDRESS
        order_hash = self.hasher.hash(order)
        order.sign = list(message_signature(order_hash, int(pk, 16)))
        if not order.flags.to_safe_book and not order.is_passive_order():
            order.router_sign = list(message_signature(order_hash, int(kwargs['router_pk'], 16)))
        try:
            return self._order_serder.serialize(order)
        except Exception as e:
            logging.exception(f'Failed to serde {e}')
            return None

    async def place_order(self, acc: ContractAddress, ticker: TradedPair, px: str, qty: str, side: str, type: str,
                          post_only: bool, full_fill: bool,
                          best_lvl: bool, safe: bool, maker: ContractAddress, gas_fee: GasFee,
                          router_fee: FixedFee = None):
        px = precise_to_price_convert(px, self._token_to_decimals[ticker.quote])
        qty = precise_to_price_convert(qty, self._token_to_decimals[ticker.base])
        info = self._trading_acc_to_user_info[acc]

        order_flags = OrderFlags(full_fill, best_lvl, post_only, side == 'SELL', type == 'MARKET', safe)

        order = self.spawn_order(acc, px=px, qty=qty, maker=maker, order_flags=order_flags, ticker=ticker,
                                 fee=OrderFee(
                                     FixedFee(self.fee_recipient, *info.fees[ticker]),
                                     FixedFee(ZERO_ADDRESS, 0, 0) if safe else router_fee,
                                     gas_fee), nonce=info.nonce,
                                 base_asset=10 ** self._token_to_decimals[ticker.base]
                                 )
        if order is None:
            logging.warning(f'Failed to spawn order {order}')
            return
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]

        return await self._post_query(f'{self._http_host}/place_order', order, jwt)

    async def cancel_order(self, acc: ContractAddress, maker: ContractAddress, order_hash: Optional[int]):
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        if order_hash is None: order_hash = 0
        req = CancelRequest(maker, order_hash, random_int(), (0, 0))
        req.sign = message_signature(self.hasher.hash(req), int(pk, 16))
        return await self._post_query(
            f'{self._http_host}/cancel_order' if order_hash != 0 else f'{self._http_host}/cancel_all',
            {'maker': req.maker.as_str(), 'sign': req.sign, 'order_hash': order_hash, 'salt': req.salt}, jwt)

    async def withdraw(self, acc: ContractAddress, maker: ContractAddress, token: ERC20Token, amount: str,
                       gas_fee: GasFee):
        jwt = self._signer_key_to_jwt[ContractAddress(self._address_to_account[acc].signer.public_key)]
        pk = self._signer_key_to_pk[ContractAddress(self._address_to_account[acc].signer.public_key)]
        amount = FixedPoint(precise_to_price_convert(amount, self._token_to_decimals[token]),
                            self._token_to_decimals[token])

        req = Withdraw(maker, token, amount, random_int(), (0, 0), gas_fee, maker)

        req.sign = message_signature(self.hasher.hash(req), int(pk, 16))
        data = {'maker': req.maker.as_str(), 'sign': req.sign, 'token': self._tokens_to_addr[req.token].as_str(),
                'salt': req.salt, 'receiver': req.receiver.as_str(),
                'amount': req.amount.value, 'gas_fee': {
                'fee_token': self._tokens_to_addr[gas_fee.fee_token].as_str(),
                'max_gas_price': gas_fee.max_gas_price.value,
                'conversion_rate': gas_fee.conversion_rate,
                'gas_per_action': gas_fee.gas_per_action
            }
                }
        return await self._post_query(f'{self._http_host}/withdraw', data, jwt)

    async def query_listen_key(self, signer: ContractAddress):
        jwt = self._signer_key_to_jwt[signer]
        resp = await self._get_query(f'{self._http_host}/user/listen_key', jwt)
        return resp['result']

    async def _get_query(self, url, jwt):
        if self._verbose: logging.info(f'GET {url}')
        res = await self._http.get(url, headers={'Authorization': jwt})
        if self._verbose: logging.info(f'Response {await res.json()} {res.status}')
        return await res.json()

    async def _post_query(self, url, data, jwt=None):
        if self._verbose: logging.info(f'POST {url} and data {data}')
        res = await self._http.post(url, json=data, headers={'Authorization': jwt} if jwt is not None else {})
        if self._verbose: logging.info(f'Response {await res.json()} {res.status}')
        return await res.json()
