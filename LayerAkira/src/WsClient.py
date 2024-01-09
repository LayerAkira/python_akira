import asyncio
import json
import logging
from asyncio import exceptions
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Callable, Awaitable

import websockets

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.TradedPair import TradedPair


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

    ClientCallback = Callable[[Optional[Dict]], Awaitable[None]]  # If None message emitted -> disconnection happened

    @dataclass
    class Job:
        idx: int
        request: Dict
        response: Dict
        event: asyncio.Event

    def __init__(self, q_listen_key_cb: Callable[[ContractAddress], Awaitable[str]],
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
        self._subscribers: Dict[int, Callable[[Optional[Dict]], Awaitable[None]]] = {}
        self._timeout = timeout
        self._idx = 0
        self._ws = None

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
                if self._verbose: logging.info(f'Connecting {self._exchange_wss_host}')
                async with websockets.connect(uri=self._exchange_wss_host,
                                              extra_headers={'Authorization': listen_key, 'Signer': signer.as_str()},
                                              **kwargs) as ws:
                    self._ws = ws
                    if self._verbose: logging.info(f'Connected to {self._exchange_wss_host}')
                    async for message in ws:
                        if self._verbose: logging.info(f'Received exchange packet {message}')
                        await self._handle_websocket_message(json.loads(message))
            except websockets.ConnectionClosedError as e:
                logging.exception(f'websockets.ConnectionClosedError: {e}')
            except Exception as e:
                logging.exception(f'Exception error different from connection closed error {e}')
            return

        while True:
            logging.info('Starting stream listener')
            await job()
            self._ws = None
            for _, v in self._jobs.items():
                v.event.set()
                v.response = None
            for _, cb in self._subscribers.items():
                asyncio.create_task(cb(None))
            self._subscribers.clear()

            if not restart: break

            await asyncio.sleep(cooldown_sec)

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
            b, q = d['pair'].split('-')
            pair = TradedPair(ERC20Token(b), ERC20Token(q))
            stream_id = (hash((stream, hash(pair), d['safe'])))
            await self._subscribers[stream_id](d)
        else:
            logging.warning(f'Unknown packet {d}')

    async def subscribe_book(self, stream: Stream, traded_pair: TradedPair, safe_book: bool, cb: ClientCallback) -> \
            Optional[Dict]:
        """

        :param stream: Stream to subscribe for
        :param traded_pair
        :param safe_book
        :param cb:
        :return: result of subscription
        """
        self._idx += 1
        req = {
            'action': 'subscribe', 'id': self._idx,
            'stream': stream.value, 'base': traded_pair.base.value, 'quote': traded_pair.quote.value,
            'safe_book': safe_book}
        stream_id = (hash((stream.value, hash(traded_pair), safe_book)))
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
        if self._ws is None:
            return None
        if stream_id in self._jobs:
            logging.warning(f'Duplicate stream for request {req}, only one callback per stream')
            return None
        req = self.Job(idx, req, {}, asyncio.Event())
        self._jobs[idx] = req
        self._subscribers[stream_id] = cb
        msg = json.dumps(req.request)
        if self._verbose: logging.info(f'Sending websocket request {msg}')
        await self._ws.send(msg)
        try:
            await asyncio.wait_for(req.event.wait(), self._timeout)
        except exceptions.TimeoutError() as e:
            self._subscribers.pop(stream_id)
            self._jobs.pop(req.idx)
            logging.warning(f'Timeout for query {req} {e}')
            return None

        data = self._jobs.pop(req.idx)
        return data.response
