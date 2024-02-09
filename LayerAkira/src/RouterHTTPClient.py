import logging
from typing import Dict, Optional

from aiohttp import ClientSession

from LayerAkira.src.BaseHTTPClient import BaseHTTPClient
from LayerAkira.src.Hasher import SnHasher
from LayerAkira.src.OrderSerializer import SimpleOrderSerializer
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, FixedFee, OrderFee
from LayerAkira.src.common.Requests import Order, OrderFlags, STPMode
from LayerAkira.src.common.Responses import ReducedOrderInfo, OrderInfo, OrderStatus
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import Result


class RouterAsyncApiHttpClient(BaseHTTPClient):

    def __init__(
            self, sn_hasher: SnHasher,
            erc_to_addr: Dict[ERC20Token, ContractAddress],
            exchange_http_host='http://localhost:7070',
            verbose=False
            ):

        self._http = ClientSession()
        self._http_host = exchange_http_host
        self._hasher: SnHasher = sn_hasher
        self._erc_to_addr: Dict[ERC20Token, ContractAddress] = erc_to_addr
        self._addr_to_erc: Dict[ContractAddress, ERC20Token] = {v: k for k, v in erc_to_addr.items()}
        self._order_serder = SimpleOrderSerializer(self._erc_to_addr)
        self._verbose = verbose

    async def close(self):
        await self._http.close()

    async def query_listen_key(self, jwt: str) -> Result[str]:
        return await self._get_query(f'{self._http_host}/user/listen_key', jwt)

    async def place_order(self, jwt: str, order: Order) -> Result[int]:
        return await self._post_query(f'{self._http_host}/place_order', self._order_serder.serialize(order), jwt)