import logging
from typing import Dict, Optional, List, Union

from aiohttp import ClientSession
from starknet_py.hash.utils import message_signature
from starknet_py.utils.typed_data import TypedData

from LayerAkira.src.Hasher import SnHasher
from LayerAkira.src.OrderSerializer import SimpleOrderSerializer
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.Requests import Withdraw, Order, CancelRequest, OrderFlags, STPMode, IncreaseNonce, Quantity, \
    Constraints
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import random_int
from LayerAkira.src.common.Responses import ReducedOrderInfo, OrderInfo, TableLevel, Snapshot, Table, FakeRouterData, \
    UserInfo, BBO, \
    OrderStatus, OrderStateInfo
from LayerAkira.src.common.common import Result


def get_typed_data(message: int, chain_id: int, name="LayerAkira Exchange", version="0.0.1"):
    return TypedData.from_dict(
        {"domain": {"name": name, "chainId": chain_id, "version": version},
         "types": {
             "StarkNetDomain": [{"name": "name", "type": "felt"},
                                {"name": "chainId", "type": "felt"}, {"name": "version", "type": "felt"}],
             "Message": [{"name": "message", "type": "felt"}],
         }, "primaryType": "Message", "message": {"message": message}})


class AsyncApiHttpClient:
    """
    Stateless Http client for interaction with LayerAkira exchange
    """

    def __init__(self, sn_hasher: SnHasher,
                 erc_to_addr: Dict[ERC20Token, ContractAddress],
                 exchange_http_host='http://localhost:8080',
                 verbose=False):
        """

        :param sn_hasher: hasher that responsible for obtaining poseidon hash for specific requests
        :param erc_to_addr:  mapping of erc symbol to its address in chain
        :param exchange_http_host:
        :param verbose:
        """
        self._http = ClientSession()
        self._http_host = exchange_http_host
        self._hasher: SnHasher = sn_hasher
        self._erc_to_addr: Dict[ERC20Token, ContractAddress] = erc_to_addr
        self._addr_to_erc: Dict[ContractAddress, ERC20Token] = {v: k for k, v in erc_to_addr.items()}
        self._order_serder = SimpleOrderSerializer(self._erc_to_addr)
        self._verbose = verbose

    async def close(self):
        await self._http.close()

    async def issue_jwt(self, signer: ContractAddress, pk: str, account: ContractAddress, chain_id: int) -> Result[str]:
        url = f'{self._http_host}/sign/request_sign_data?user={signer}&account={account}'
        msg = await self._get_query(url)
        if msg.data is None: return msg

        url = f'{self._http_host}/sign/auth'
        msg_hash = get_typed_data(msg.data, chain_id).message_hash(account.as_int())
        return await self._post_query(url, {'msg': msg.data,
                                            'signature': list(message_signature(msg_hash, int(pk, 16)))})

    async def query_gas_price(self, jwt: str) -> Result[int]:
        return await self._get_query(f'{self._http_host}/gas/price', jwt)

    async def get_order(self, acc: ContractAddress, jwt: str, order_hash: int, mode: int = 1) -> Result[
        Union[OrderInfo, ReducedOrderInfo]]:
        """

        :param acc:
        :param jwt:
        :param order_hash:
        :param mode: 1 for full data, 2 for reduced data
        :return:
        """
        url = f'{self._http_host}/user/order?order_hash={order_hash}&trading_account={acc}&mode={mode}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        return Result(self._parse_order_response(resp.data, mode))

    async def get_orders(self, acc: ContractAddress, jwt: str, mode: int = 1, limit=20, offset=0) -> \
            Result[List[Union[ReducedOrderInfo, OrderInfo]]]:
        url = f'{self._http_host}/user/orders?mode={mode}&trading_account={acc}&limit={limit}&offset={offset}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        return Result([self._parse_order_response(x, mode) for x in resp.data])

    async def get_bbo(self, jwt: str, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[BBO]:
        url = f'{self._http_host}/book/bbo?base={self._erc_to_addr[base]}' \
              f'&quote={self._erc_to_addr[quote]}&to_ecosystem_book={int(ecosystem_book)}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp

        def retrieve_lvl(data: Dict): return TableLevel(data['price'], data['volume']) if len(data) > 0 else None

        return Result(BBO(retrieve_lvl(resp.data['bid']), retrieve_lvl(resp.data['ask']), 0))

    async def get_snapshot(self, jwt: str, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[
        Snapshot]:
        url = f'{self._http_host}/book/snapshot?base={self._erc_to_addr[base]}' \
              f'&quote={self._erc_to_addr[quote]}&to_ecosystem_book={int(ecosystem_book)}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        levels = resp.data['levels']
        return Result(Snapshot(
            Table([TableLevel(x[0], x[1]) for x in levels['bids']], [TableLevel(x[0], x[1]) for x in levels['asks']]),
            levels['msg_id'])
        )

    async def increase_nonce(self, pk: str, jwt: str, maker: ContractAddress, new_nonce: int, gas_fee: GasFee):
        req = IncreaseNonce(maker, new_nonce, gas_fee, random_int(), (0, 0))
        req.sign = message_signature(self._hasher.hash(req), int(pk, 16))
        data = {'maker': req.maker.as_str(), 'sign': req.sign,
                'new_nonce': new_nonce,
                'salt': req.salt, 'gas_fee': {
                'fee_token': self._erc_to_addr[gas_fee.fee_token].as_str(),
                'max_gas_price': gas_fee.max_gas_price,
                'conversion_rate': gas_fee.conversion_rate,
                'gas_per_action': gas_fee.gas_per_action
            }
                }
        return await self._post_query(f'{self._http_host}/increase_nonce', data, jwt)

    async def cancel_order(self, pk: str, jwt: str, maker: ContractAddress, order_hash: Optional[int]) -> Result[int]:
        """
        :param pk: private key of signer for trading account
        :param jwt: jwt token
        :param maker: trading account
        :param order_hash: if order_hash is None or 0, the request treated as cancel_all
        :return: poseidon hash of request
        """
        if order_hash is None: order_hash = 0
        req = CancelRequest(maker, order_hash, random_int(), (0, 0))
        req.sign = message_signature(self._hasher.hash(req), int(pk, 16))
        return await self._post_query(
            f'{self._http_host}/cancel_order' if order_hash != 0 else f'{self._http_host}/cancel_all',
            {'maker': req.maker.as_str(), 'sign': req.sign, 'order_hash': order_hash, 'salt': req.salt}, jwt)

    async def withdraw(self, pk: str, jwt: str, maker: ContractAddress, token: ERC20Token, amount: int,
                       gas_fee: GasFee) -> Result[int]:
        req = Withdraw(maker, token, amount, random_int(), (0, 0), gas_fee, maker)

        req.sign = message_signature(self._hasher.hash(req), int(pk, 16))
        data = {'maker': req.maker.as_str(), 'sign': req.sign, 'token': self._erc_to_addr[req.token].as_str(),
                'salt': req.salt, 'receiver': req.receiver.as_str(),
                'amount': req.amount, 'gas_fee': {
                'fee_token': self._erc_to_addr[gas_fee.fee_token].as_str(),
                'max_gas_price': gas_fee.max_gas_price,
                'conversion_rate': gas_fee.conversion_rate,
                'gas_per_action': gas_fee.gas_per_action
            }
                }
        return await self._post_query(f'{self._http_host}/withdraw', data, jwt)

    async def query_listen_key(self, jwt: str) -> Result[str]:
        return await self._get_query(f'{self._http_host}/user/listen_key', jwt)

    async def place_order(self, jwt: str, order: Order) -> Result[int]:
        return await self._post_query(f'{self._http_host}/place_order', self._order_serder.serialize(order), jwt)

    async def query_fake_router_data(self, jwt: str, order: Order) -> Result[FakeRouterData]:
        """

        :param jwt:  jwt token
        :param order: Order that fake router would sign
        :return: return data for order that should be inserted

        Flow ->
            1) user sending unsigned order, fake router sign it and return FakeRouterData
            2) user fill order with this data and sign this order and place order to exchange
        """
        res = await self._post_query(f'{self._http_host}/router_sign', self._order_serder.serialize(order), jwt)
        if res.data is None: return res
        return Result(FakeRouterData(res.data['taker_pbips'], ContractAddress(res.data['fee_recipient']),
                                     res.data['max_taker_pbips'], ContractAddress(res.data['router_signer']),
                                     0, tuple(res.data['router_signature'])))

    async def get_trading_acc_info(self, acc: ContractAddress, jwt: str) -> Result[UserInfo]:
        url = f'{self._http_host}/user/user_info?trading_account={acc}'
        info = await self._get_query(url, jwt)
        if info.data is None: return info
        info = info.data
        fees_d = {}
        balances = {}
        for pair, fees in info['fees']:
            fees_d[TradedPair(self._addr_to_erc[ContractAddress(pair[0])],
                              self._addr_to_erc[ContractAddress(pair[1])])] = fees

        for token, total, locked in info['balances']:
            balances[self._addr_to_erc[ContractAddress(token)]] = (total, locked)

        return Result(UserInfo(info['nonce'], fees_d, balances))

    async def _get_query(self, url, jwt: Optional[str] = None):
        if self._verbose: logging.info(f'GET {url}')
        res = await self._http.get(url, headers={'Authorization': jwt} if jwt is not None else {})
        if self._verbose: logging.info(f'Response {await res.json()} {res.status}')
        resp = await res.json()
        if 'result' in resp: return Result(resp['result'])
        return Result(None, resp['code'], resp['error'])

    async def _post_query(self, url, data, jwt: Optional[str] = None):
        if self._verbose: logging.info(f'POST {url} and data {data}')
        res = await self._http.post(url, json=data, headers={'Authorization': jwt} if jwt is not None else {})
        if self._verbose: logging.info(f'Response {await res.json()} {res.status}')
        resp = await res.json()
        if 'result' in resp: return Result(resp['result'])
        return Result(None, resp['code'], resp['error'])

    def _parse_order_response(self, d: Dict, mode):
        state_info = OrderStateInfo(
            d['state']['filled_base_amount'],
            d['state']['filled_quote_amount'],
            d['state']['cur_number_of_swaps'],
            OrderStatus(d['state']['status']),
            d['state']['limit_price']
        )
        if mode == 2:
            return ReducedOrderInfo(
                ContractAddress(d['maker']),
                d['hash'],
                state_info,
                d['price'],
                TradedPair(self._addr_to_erc[ContractAddress(d['ticker'][0])],
                           self._addr_to_erc[ContractAddress(d['ticker'][1])]),
                Quantity(d['qty']['base_qty'], d['qty']['quote_qty'], 0),
                OrderFlags(*[bool(x) for x in d['flags']]),
                STPMode(d['stp']),
                d['expiration_time']
            )
        elif mode == 1:
            trade_fee, router_fee, gas_fee = d['fee']['trade_fee'], d['fee']['router_fee'], d['fee']['gas_fee']
            return OrderInfo(
                Order(
                    ContractAddress(d['maker']),
                    d['price'],
                    Quantity(d['qty']['base_qty'], d['qty']['quote_qty'], d['qty']['base_asset']),
                    TradedPair(self._addr_to_erc[ContractAddress(d['ticker'][0])],
                               self._addr_to_erc[ContractAddress(d['ticker'][1])]),
                    OrderFee(
                        FixedFee(ContractAddress(trade_fee['recipient']), trade_fee['maker_pbips'],
                                 trade_fee['taker_pbips']),
                        FixedFee(ContractAddress(router_fee['recipient']), router_fee['maker_pbips'],
                                 router_fee['taker_pbips']),
                        GasFee(gas_fee['gas_per_action'], self._addr_to_erc[ContractAddress(gas_fee['fee_token'])],
                               gas_fee['max_gas_price'],
                               tuple(gas_fee['conversion_rate']))
                    ),
                    Constraints(
                        d['constraints']['number_of_swaps_allowed'],
                        d['constraints']['duration_valid'],
                        d['constraints']['created_at'],
                        STPMode(d['constraints']['stp']),
                        d['constraints']['nonce'],
                        d['constraints']['min_receive_amount'],
                        ContractAddress(d['constraints']['router_signer']),
                    ),
                    d['salt'],
                    OrderFlags(*[bool(x) for x in d['flags']]),
                    (0, 0),
                    (0, 0),
                    d['version']
                ),
                state_info
            )
