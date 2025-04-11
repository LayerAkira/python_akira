import logging
from typing import Dict, Optional, List, Union, Tuple, Callable

from aiohttp import ClientSession
from starknet_py.utils.typed_data import TypedData

from LayerAkira.src.hasher.Hasher import SnTypedPedersenHasher
from LayerAkira.src.OrderSerializer import SimpleOrderSerializer, serialize_gas_fee
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.Requests import Withdraw, Order, CancelRequest, OrderFlags, STPMode, IncreaseNonce, Quantity, \
    Constraints, SpotTicker, SignScheme
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import random_int, precise_to_price_convert, precise_from_price_to_str_convert
from LayerAkira.src.common.Responses import ReducedOrderInfo, OrderInfo, TableLevel, Snapshot, Table, RouterDetails, \
    UserInfo, BBO, \
    OrderStatus, OrderStateInfo
from LayerAkira.src.common.common import Result


def get_typed_data(message: int, chain_id: int, name="LayerAkira Exchange", version="0.0.1"):
    challenge = (
        'Sign in to LayerAkira',
        "\tChallenge:",
        hex(message)
    )
    return TypedData.from_dict(
        {"domain": {"name": name, "version": version, "chainId": hex(chain_id)},
         "types": {
             "StarkNetDomain": [{"name": "name", "type": "felt"},
                                {"name": "version", "type": "felt"}, {"name": "chainId", "type": "felt"}],
             "Message": [{"name": "welcome", "type": "string"},
                         {"name": "to", "type": "string"},
                         {"name": "exchange", "type": "string"}],
         }, "primaryType": "Message",
         "message": {'welcome': challenge[0], 'to': challenge[1], 'exchange': challenge[2]}})


class AsyncApiHttpClient:
    """
    Stateless Http client for interaction with LayerAkira exchange
    """

    def __init__(self, sn_hasher: SnTypedPedersenHasher,
                 sign_cb: Callable[[int, int], Tuple[int, int]],
                 erc_to_decimals: Dict[ERC20Token, int],
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
        self._hasher: SnTypedPedersenHasher = sn_hasher
        self._erc_to_decimals = erc_to_decimals
        self._order_serder = SimpleOrderSerializer(erc_to_decimals)
        self._verbose = verbose
        self._sign_cb = sign_cb

    async def close(self):
        await self._http.close()

    async def issue_jwt(self, signer: ContractAddress, pk: str, account: ContractAddress, chain_id: int) -> Result[str]:
        url = f'{self._http_host}/sign/request_sign_data?user={signer}&account={account}'
        msg = await self._get_query(url)
        if msg.data is None: return msg

        url = f'{self._http_host}/sign/auth'
        msg_hash = get_typed_data(int(msg.data), chain_id).message_hash(account.as_int())
        return await self._post_query(url, {'msg': msg.data,
                                            'signature': [hex(x) for x in list(self._sign_cb(msg_hash, int(pk, 16)))]})

    async def query_gas_price(self, jwt: str) -> Result[int]:
        gas_px = await self._get_query(f'{self._http_host}/gas/price', jwt)
        if gas_px.data is not None: gas_px.data = int(gas_px.data)
        return gas_px

    async def get_conversion_rate(self, token: ERC20Token, jwt: str) -> Result[Tuple[int, int]]:
        rate = await self._get_query(f'{self._http_host}/info/conversion_rate?token={token.value}', jwt)
        if rate.data is not None:
            rate.data = (precise_to_price_convert(rate.data[0], self._erc_to_decimals[ERC20Token.STRK]),
                         precise_to_price_convert(rate.data[1], self._erc_to_decimals[token]))

        return rate

    async def get_order(self, acc: ContractAddress, jwt: str, order_hash: int, active:int = 1, mode: int = 1) -> Result[
        Union[OrderInfo, ReducedOrderInfo]]:
        """

        :param acc:
        :param jwt:
        :param order_hash:
        :param mode: 1 for full data, 2 for reduced data
        :return:
        """
        url = f'{self._http_host}/user/order?order_hash={order_hash}&trading_account={acc}&mode={mode}&active={active}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        return Result(self._parse_order_response(resp.data, mode))


    async def get_order_router(self, acc: ContractAddress, jwt: str, t_acc: ContractAddress, order_hash: int, active:int = 1, mode: int = 1) -> Result[
        Union[OrderInfo, ReducedOrderInfo]]:
        url = f'{self._http_host}/user/order_router?order_hash={order_hash}&trading_account={t_acc}&mode={mode}&active={active}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        return Result(self._parse_order_response(resp.data, mode))


    async def get_orders(self, acc: ContractAddress, jwt: str, mode: int = 1, limit=20, offset=0, is_active = True) -> \
            Result[List[Union[ReducedOrderInfo, OrderInfo]]]:
        url = f'{self._http_host}/user/orders?mode={mode}&trading_account={acc}&limit={limit}&offset={offset}&is_active={bool(is_active)}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        return Result([self._parse_order_response(x, mode) for x in resp.data])

    async def get_bbo(self, jwt: str, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[BBO]:
        url = f'{self._http_host}/book/bbo?base={base}&quote={quote}&to_ecosystem_book={int(ecosystem_book)}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp

        def retrieve_lvl(data: Dict): return TableLevel(
            precise_to_price_convert(data['price'], self._erc_to_decimals[quote]),
            int(precise_to_price_convert(data['volume'], self._erc_to_decimals[base])),
            data['orders']) if len(data) > 0 else None

        return Result(BBO(retrieve_lvl(resp.data['bid']), retrieve_lvl(resp.data['ask']), 0))

    async def get_snapshot(self, jwt: str, base: ERC20Token, quote: ERC20Token, ecosystem_book: bool) -> Result[
        Snapshot]:
        url = f'{self._http_host}/book/snapshot?base={base}' \
              f'&quote={quote}&to_ecosystem_book={int(ecosystem_book)}'
        resp = await self._get_query(url, jwt)
        if resp.data is None: return resp
        levels = resp.data['levels']
        return Result(Snapshot(
            Table(
                [TableLevel(int(precise_to_price_convert(x[0], self._erc_to_decimals[quote])),
                            int(precise_to_price_convert(x[1], self._erc_to_decimals[base])), x[2]) for x in
                 levels['bids']],
                [TableLevel(int(precise_to_price_convert(x[0], self._erc_to_decimals[quote])),
                            int(precise_to_price_convert(x[1], self._erc_to_decimals[base])), x[2]) for x in
                 levels['asks']]),
            int(levels['msg_id']))
        )

    async def increase_nonce(self, pk: str, jwt: str, maker: ContractAddress, new_nonce: int, gas_fee: GasFee, sign_scheme:SignScheme):
        req = IncreaseNonce(maker, new_nonce, gas_fee, random_int(), (0, 0), sign_scheme)
        req.sign = self._sign_cb(self._hasher.hash(req), int(pk, 16))
        data = {'maker': req.maker.as_str(), 'sign': [hex(x) for x in req.sign],
                'new_nonce': new_nonce,
                'salt': hex(req.salt), 'gas_fee': serialize_gas_fee(gas_fee, self._erc_to_decimals)[1],
                'sign_scheme': req.sign_scheme.value
                }
        return await self._post_query(f'{self._http_host}/increase_nonce', data, jwt)

    async def cancel_order(self, pk: str, jwt: str, maker: ContractAddress, order_hash: int, sign_scheme:SignScheme) -> Result[int]:
        """
        :param sign_scheme:
        :param pk: private key of signer for trading account
        :param jwt: jwt token
        :param maker: trading account
        :param order_hash: hash of the order
        :return: poseidon hash of request
        """
        req = CancelRequest(maker, order_hash, None, random_int(), (0, 0), sign_scheme)
        req.sign = self._sign_cb(self._hasher.hash(req), int(pk, 16))
        return await self._post_query(
            f'{self._http_host}/cancel_order',
            {'maker': req.maker.as_str(), 'sign': [hex(x) for x in req.sign], 'order_hash': hex(order_hash), 'salt': hex(req.salt),
             'ticker': {'base': '0x0', 'quote': '0x0', 'to_ecosystem_book': True},'sign_scheme':sign_scheme.value
             }, jwt)

    async def cancel_all_orders(self, pk: str, jwt: str, maker: ContractAddress, ticker: SpotTicker,sign_scheme:SignScheme) -> Result[int]:
        """
        :param sign_scheme:
        :param pk: private key of signer for trading account
        :param jwt: jwt token
        :param maker: trading account
        :param ticker: ticker for which orders should be cancelled
        :return: poseidon hash of request
        """
        req = CancelRequest(maker, None, ticker, random_int(), (0, 0), sign_scheme)
        req.sign = self._sign_cb(self._hasher.hash(req), int(pk, 16))
        return await self._post_query(
            f'{self._http_host}/cancel_all',
            {'maker': req.maker.as_str(), 'sign': [hex(x) for x in req.sign], 'order_hash': 0, 'salt': hex(req.salt),
             'ticker': {'base': ticker.pair.base, 'quote': ticker.pair.quote,
                        'to_ecosystem_book': ticker.is_ecosystem_book},
             'sign_scheme': sign_scheme.value
             }, jwt)

    async def withdraw(self, pk: str, jwt: str, maker: ContractAddress, token: ERC20Token, amount: int,
                       gas_fee: GasFee) -> Result[int]:
        req = Withdraw(maker, token, amount, random_int(), (0, 0), gas_fee, maker, SignScheme.ECDSA)

        req.sign = self._sign_cb(self._hasher.hash(req), int(pk, 16))
        data = {'maker': req.maker.as_str(), 'sign': [hex(x) for x in req.sign], 'token': req.token,
                'salt': hex(req.salt), 'receiver': req.receiver.as_str(),
                'amount': precise_from_price_to_str_convert(req.amount, self._erc_to_decimals[req.token]),
                'gas_fee': serialize_gas_fee(gas_fee, self._erc_to_decimals)[1],
                'sign_scheme': req.sign_scheme.value
                }
        return await self._post_query(f'{self._http_host}/withdraw', data, jwt)

    async def query_listen_key(self, jwt: str) -> Result[str]:
        return await self._get_query(f'{self._http_host}/user/listen_key', jwt)

    async def place_order(self, jwt: str, order: Order) -> Result[str]:
        return await self._post_query(f'{self._http_host}/place_order', self._order_serder.serialize(order), jwt)

    async def query_router_details(self, jwt: str) -> Result[RouterDetails]:
        """

        :param jwt:  jwt token
        :return: return data for order that should be inserted for router orders
        Flow ->
            1) user sending unsigned order, it return RouterDetails
            2) user fill order with this data and sign this order and place order to exchange
        """
        res = await self._get_query(f'{self._http_host}/info/router_details', jwt)
        if res.data is None: return res
        return Result(RouterDetails(res.data['routerTakerPbips'], res.data['routerMakerPbips'],
                                    ContractAddress(res.data['routerFeeRecipient']),
                                    ContractAddress(res.data['routerSigner'])))

    async def get_trading_acc_info(self, acc: ContractAddress, jwt: str) -> Result[UserInfo]:
        url = f'{self._http_host}/user/user_info?trading_account={acc}'
        info = await self._get_query(url, jwt)
        if info.data is None: return info
        info = info.data
        fees_d = {}
        balances = {}
        for data in info['fees']:
            fees_d[TradedPair(ERC20Token(data['base']), ERC20Token(data['quote']))] = (
                int(data['fee'][0]), int(data['fee'][1]))

        for data in info['balances']:
            balances[ERC20Token(data['token'])] = (data['balance'], data['locked'])

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
        pair = TradedPair(ERC20Token(d['ticker']['base']), ERC20Token(d['ticker']['quote']))

        state_info = OrderStateInfo(
            precise_to_price_convert(d['state']['filled_base_amount'], self._erc_to_decimals[pair.base]),
            precise_to_price_convert(d['state']['filled_quote_amount'], self._erc_to_decimals[pair.quote]),
            d['state']['cur_number_of_swaps'],
            OrderStatus(d['state']['status']),
            precise_to_price_convert(d['state']['limit_price'], self._erc_to_decimals[pair.quote]) if d['state'][
                                                                                                          'limit_price'] is not None else None
        )
        if mode == 2:
            return ReducedOrderInfo(
                ContractAddress(d['maker']),
                int(d['hash'], 16),
                state_info,
                precise_to_price_convert(d['price'], self._erc_to_decimals[pair.quote]),
                pair,
                Quantity(
                    precise_to_price_convert(d['qty']['base_qty'], self._erc_to_decimals[pair.base]),
                    precise_to_price_convert(d['qty']['quote_qty'], self._erc_to_decimals[pair.quote]),
                    10 ** self._erc_to_decimals[pair.base]),
                OrderFlags(*[bool(x) for x in d['flags']]),
                STPMode(d['stp']),
                d['expiration_time'],
                d['source']
            )
        elif mode == 1:
            trade_fee, router_fee, gas_fee = d['fee']['trade_fee'], d['fee']['router_fee'], d['fee']['gas_fee']
            return OrderInfo(
                Order(
                    ContractAddress(d['maker']),
                    precise_to_price_convert(d['price'], self._erc_to_decimals[pair.quote]),
                    Quantity(
                        precise_to_price_convert(d['qty']['base_qty'], self._erc_to_decimals[pair.base]),
                        precise_to_price_convert(d['qty']['quote_qty'], self._erc_to_decimals[pair.quote]),
                        10 ** self._erc_to_decimals[pair.base]),
                    pair,
                    OrderFee(
                        FixedFee(ContractAddress(trade_fee['recipient']), trade_fee['maker_pbips'],
                                 trade_fee['taker_pbips']),
                        FixedFee(ContractAddress(router_fee['recipient']), router_fee['maker_pbips'],
                                 router_fee['taker_pbips']),
                        GasFee(gas_fee['gas_per_action'], ERC20Token(gas_fee['fee_token']),
                               precise_to_price_convert(gas_fee['max_gas_price'],
                                                        self._erc_to_decimals[ERC20Token(gas_fee['fee_token'])]),
                               tuple(float(x) for x in gas_fee['conversion_rate']))
                    ),
                    Constraints(
                        d['constraints']['number_of_swaps_allowed'],
                        d['constraints']['duration_valid'],
                        d['constraints']['created_at'],
                        STPMode(d['constraints']['stp']),
                        d['constraints']['nonce'],
                        int(d['constraints']['min_receive_amount']),
                        ContractAddress(d['constraints']['router_signer']),
                    ),
                    int(d['salt']),
                    OrderFlags(*[bool(x) for x in d['flags']]),
                    (0, 0),
                    (0, 0),
                    d['source'],
                    SignScheme(d['sign_scheme'])
                ),
                state_info
            )
