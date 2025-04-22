import asyncio
import json
import logging
from asyncio import exceptions
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Callable, Awaitable, List, Any, Union

import websockets

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.Responses import TableLevel, BBO, Snapshot, Table, Trade, ExecReport, OrderStatus, \
    OrderMatcherResult, CancelAllReport, FailProcessingReport, TxHashRollupReport
from LayerAkira.src.common.common import precise_to_price_convert


class Stream(str, Enum):
    TRADE = 'trade'
    FILLS = 'fills'  # execution report stream
    BBO = 'bbo'  # best bid best offer stream
    BOOK_DELTA = 'snap'  # update of book stream


class WsClient:
    """
        Simple websocket client that allow to subscribe to streams of LayerAkira exchange
        Only one callback per unique subscription is supported
    """

    # If None message emitted -> disconnection happened
    ClientCallback = Callable[[Optional[Union[BBO, Snapshot, Trade, ExecReport, CancelAllReport]]], Awaitable[None]]

    @dataclass
    class Job:
        idx: int
        request: Dict
        response: Dict
        event: asyncio.Event

    def __init__(self, erc_to_decimals: Dict[ERC20Token, int],
                 q_listen_key_cb: Callable[[ContractAddress], Awaitable[str]],
                 exchange_wss_host='http://localhost:8888/ws', timeout=5, verbose=False):
        """

        :param q_listen_key_cb: callback that query listen key to auth websocket connection, returns listen key
        :param exchange_wss_host:
        :param timeout: after this specified amount of time subscription response is treated with timeout
        :param verbose:
        """
        self._verbose = verbose
        self._exchange_wss_host = exchange_wss_host
        self._query_listen_key = q_listen_key_cb
        self._jobs: Dict[int, WsClient.Job] = {}
        self._subscribers: Dict[int, Callable[[Optional[Any]], Awaitable[None]]] = {}
        self._timeout = timeout
        self._idx = 0
        self.ws = None
        self._running = False
        self._terminated = False
        self._erc_to_decimals = erc_to_decimals

    async def run_stream_listener(self, signer: ContractAddress, restart=False, cooldown_sec=5,
                                  **kwargs):
        """

        :param signer: The main account for which jwt token was issued on exchange
        :param restart: should webscoket reconnect if disconnect/exception happens
        :param cooldown_sec: cooldown before reconnect
        :param kwargs: additional params for websockets.connect
        :return:
        Note on reconnect pending requests are cancelled as well as subscriptions
        For subscribers the event with None emitted
        """

        async def job():
            try:
                listen_key = (await self._query_listen_key(signer))
                if listen_key is None:
                    logging.warning('Failed to query listen key')
                    return
                if self._verbose: logging.info(f'Connecting {self._exchange_wss_host}')
                async with websockets.connect(
                        uri=f'{self._exchange_wss_host}?listenKey={listen_key}&signer={signer.as_str()}',
                        **kwargs) as ws:
                    self.ws = ws
                    if self._verbose: logging.info(f'Connected to {self._exchange_wss_host}')
                    async for message in ws:
                        if self._verbose: logging.info(f'Received exchange packet {message}')
                        await self._handle_websocket_message(json.loads(message))
            except websockets.ConnectionClosedError as e:
                logging.exception(f'websockets.ConnectionClosedError: {e}')
            except Exception as e:
                logging.exception(f'Exception error different from connection closed error {e}')
            return

        self._running = True
        self._terminated = False
        while self._running:
            if self._verbose: logging.info('Starting stream listener')
            await job()
            self.ws = None
            for _, v in self._jobs.items():
                v.event.set()
                v.response = None
            for _, cb in self._subscribers.items():
                asyncio.create_task(cb(None))
            self._subscribers.clear()

            if not restart: break

            await asyncio.sleep(cooldown_sec)
        if self._verbose:
            logging.info('Stream listener stopped')
        self._terminated = True

    async def stop_stream_listener(self) -> bool:
        self._running = False
        if self.ws is not None:
            await self.ws.close()
            return True
        return self._terminated

    async def _handle_websocket_message(self, d: Dict):
        idx = d.get('id', None)
        if idx is not None:
            if idx not in self._jobs:
                logging.warning(f'Unknown response {idx} {d}')
                return
            self._jobs[idx].event.set()
            self._jobs[idx].response = d
            return
        stream = d.get('stream', None)
        if stream is None:
            logging.warning(f'Unknown stream {stream} for packet  {d}')
            return
        if stream in [Stream.BBO, Stream.TRADE, Stream.BOOK_DELTA]:
            b, q = d['pair']['base'], d['pair']['quote']
            pair = TradedPair(ERC20Token(b), ERC20Token(q))
            stream_id = (hash((stream, hash(pair), d['ecosystem'])))
            data = self._parse_md(d, Stream(stream))
            if data is not None:
                await self._subscribers[stream_id](data)
        elif stream == Stream.FILLS:
            stream_id = hash((Stream.FILLS.value, ContractAddress(d['client'])))
            data = self._parse_md(d, Stream(stream))
            if data is not None:
                await self._subscribers[stream_id](data)
        else:
            logging.warning(f'Unknown packet {d}')

    async def subscribe_book(self, stream: Stream, traded_pair: TradedPair, ecosystem_book: bool, cb: ClientCallback) -> \
            Optional[Dict]:
        """

        :param stream: Stream to subscribe for
        :param traded_pair
        :param ecosystem_book
        :param cb:
        :return: result of subscription
        """
        self._idx += 1
        req = {
            'action': 'subscribe', 'id': self._idx,
            'stream': stream.value, 'ticker': {'base': traded_pair.base, 'quote': traded_pair.quote,
                                               'ecosystem_book': ecosystem_book}}
        stream_id = (hash((stream.value, hash(traded_pair), ecosystem_book)))
        return await self._subscribe(cb, req, stream_id, self._idx)

    async def subscribe_fills(self, acc: ContractAddress, cb: ClientCallback) -> Optional[Dict]:
        """

        :param acc: Trading account for whose fill subscription (not signer must be the signer for trading account)
        :param cb:
        :return: result of subscription
        """
        self._idx += 1
        req = {'action': 'subscribe', 'id': self._idx, 'stream': f'{Stream.FILLS.value}_{acc}'}
        stream_id = (hash((Stream.FILLS.value, acc.as_int())))
        return await self._subscribe(cb, req, stream_id, self._idx)

    async def _subscribe(self, cb, req, stream_id: int, idx: int):
        if self.ws is None:
            return None
        if stream_id in self._jobs:
            logging.warning(f'Duplicate stream for request {req}, only one callback per stream')
            return None
        req = self.Job(idx, req, {}, asyncio.Event())
        self._jobs[idx] = req
        self._subscribers[stream_id] = cb
        msg = json.dumps(req.request)
        if self._verbose: logging.info(f'Sending websocket request {msg}')
        await self.ws.send(msg)
        try:
            await asyncio.wait_for(req.event.wait(), self._timeout)
        except exceptions.TimeoutError() as e:
            self._subscribers.pop(stream_id)
            self._jobs.pop(req.idx)
            logging.warning(f'Timeout for query {req} {e}')
            return None

        data = self._jobs.pop(req.idx)
        return data.response

    def _parse_md(self, data: Dict, stream: Stream):
        if 'pair' in data:
            pair = TradedPair(ERC20Token(data['pair']['base']), ERC20Token(data['pair']['quote']))
            b_decimals, q_decimals = self._erc_to_decimals[pair.base], self._erc_to_decimals[pair.quote]

        d = data['result']
        if stream == Stream.BBO:
            def retrieve_lvl(data: List):
                return TableLevel(precise_to_price_convert(data[0], q_decimals),
                                  precise_to_price_convert(data[1], b_decimals), data[2]) if len(data) > 0 else None

            return BBO(retrieve_lvl(d['bid']), retrieve_lvl(d['ask']), d['time'], pair)
        elif stream == Stream.BOOK_DELTA:
            return Snapshot(
                Table([TableLevel(
                    precise_to_price_convert(x[0], q_decimals),
                    precise_to_price_convert(x[1], b_decimals),
                    x[2]) for x in d['bids']],
                    [TableLevel(
                        precise_to_price_convert(x[0], q_decimals),
                        precise_to_price_convert(x[1], b_decimals),
                        x[2]) for x in d['asks']]), int(d['msg_id']), pair,
                d['time'], d.get('msg_ids_start', 0), d.get('msg_ids_end', 0)
            )
        elif stream == Stream.TRADE:
            return Trade(precise_to_price_convert(d['price'], q_decimals),
                         precise_to_price_convert(d['base_qty'], b_decimals),
                         d['is_sell_side'],
                         d['time'], pair)
        elif stream == Stream.FILLS:
            try:
                if 'hash' in d:
                    return ExecReport(ContractAddress(data['client']), pair,
                                      precise_to_price_convert(d['fill_price'], q_decimals),
                                      precise_to_price_convert(d['fill_base_qty'], b_decimals),
                                      precise_to_price_convert(d['fill_quote_qty'], q_decimals),
                                      precise_to_price_convert(d['acc_base_qty'], b_decimals),
                                      precise_to_price_convert(d['acc_quote_qty'], q_decimals),
                                      int(d['hash'], 16),
                                      d['is_sell_side'],
                                      OrderStatus(d['status']),
                                      OrderMatcherResult(d['matcher_result']),
                                      d.get('source', None)
                                      )
                elif 'report_type' in d:
                    return FailProcessingReport(ContractAddress(data['client']), d['report_type'],
                                                int(d['req_hash'], 16), int(d['entity_hash'], 16),
                                                d.get('error_code_orderbook', None))
                elif 'tx_hash' in d:
                    return TxHashRollupReport(
                        tx_hash=int(d['tx_hash'], 16),
                        order_hash=int(d['order_hash'], 16),
                        client=ContractAddress(data['client']),
                        source=d['source'],
                        old_tx_hash=int(d.get('old_tx_hash'), 16) if d.get('old_tx_hash') is not None else None,
                    )
                else:

                    return CancelAllReport(ContractAddress(data['client']), int(d['cancel_ticker_hash'], 16),
                                           TradedPair(ERC20Token(data['pair']['base']),
                                                      ERC20Token(data['pair']['quote'])))
            except Exception as e:
                logging.exception(f'Failed to parse due {e} this\n: {data}')
            raise e
