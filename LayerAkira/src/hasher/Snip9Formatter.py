from typing import Dict

from LayerAkira.src.AkiraExchangeClient import AkiraExchangeClient
from LayerAkira.src.AkiraFormatter import AkiraFormatter
from LayerAkira.src.ERC20Client import ERC20Client
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.Requests import Order, Snip9OrderMatch, Call
from LayerAkira.src.hasher.utils import get_event_selector


class Snip9Formatter:
    def __init__(self,
                 akira: AkiraExchangeClient,
                 erc_to_addr: Dict[ERC20Token, ContractAddress],
                 ):
        self._akira = akira
        self._erc20_client = ERC20Client(self._akira.client)
        self._erc_to_addr = erc_to_addr
        self._akira_formatter = AkiraFormatter(erc_to_addr)

    def get_snip9_order_match(self, order: Order) -> Snip9OrderMatch:
        if order.snip9_calldata.maker != order.maker:
            raise ValueError(f'Snip9 incorrect signer should be {order.maker}')
        subcalls = []
        for (addr, amount), _ in order.snip9_calldata.get_multicall(set(self._erc_to_addr.values()),
                                                                    self._akira.core_address,
                                                                    self._akira.executor_address):
            if addr == self._akira.core_address:
                subcalls.append(Call(addr.as_int(), get_event_selector('grant_access_to_executor'), []))
            else:
                call = self._erc20_client.token_contract.prepare_calldata('approve',
                                                                          self._akira.executor_address.as_int(),
                                                                          amount)
                call.to_addr = addr.as_int()
                subcalls.append(Call(call.to_addr, call.selector, call.calldata))

        call = self._akira.executor.prepare_calldata('placeTakerOrder',
                                                     self._akira_formatter.prepare_order(order)['order'],
                                                     order.router_sign,
                                                     )

        snip9_order_match = Snip9OrderMatch(
            order.maker,
            subcalls,
            Call(call.to_addr, call.selector, call.calldata),
            order.snip9_calldata,
        )

        return snip9_order_match
