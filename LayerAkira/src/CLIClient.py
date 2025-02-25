import asyncio
import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple
from typing import Optional

import toml
from aioconsole import ainput
from starknet_py.hash.utils import message_signature
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from LayerAkira.src.AkiraExchangeClient import AkiraExchangeClient
from LayerAkira.src.HttpClient import AsyncApiHttpClient
from LayerAkira.src.JointHttpClient import JointHttpClient
from LayerAkira.src.WsClient import WsClient, Stream
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import precise_to_price_convert
from LayerAkira.src.hasher.Hasher import SnTypedPedersenHasher
from LayerAkira.src.common.Requests import SpotTicker


def GAS_FEE_ACTION(gas: int, fix_steps):
    return GasFee(fix_steps, ERC20Token.STRK, gas, (1, 1))


@dataclass
class ERC20Spec:
    symbol: ERC20Token
    address: ContractAddress
    decimals: int


@dataclass
class CLIConfig:
    node: str
    core_address: ContractAddress
    executor_address: ContractAddress
    router_address: ContractAddress
    http: str
    wss: str
    tokens: List[ERC20Spec]
    chain_id: StarknetChainId
    gas_fee_steps: Dict[str, Dict[bool, int]]
    gas_multiplier: float
    verbose: bool
    trading_account: Tuple[ContractAddress, ContractAddress, str]


def parse_cli_cfg(file_path: str):
    data = toml.load(file_path)
    tokens = []
    for token_data in data.get('ERC20', []):
        token = ERC20Spec(symbol=ERC20Token(token_data['symbol']),
                          address=ContractAddress(token_data['address']), decimals=token_data['decimals'])
        tokens.append(token)

    steps = {}
    for d in data['gas_action']:
        if d['action'] not in steps: steps[d['action']] = {}
        steps[d['action']][d['ecosystem']] = d['steps']
    acc = ContractAddress(data['trading_account']['account_address'])
    pub = ContractAddress(data['trading_account']['public_key'])
    pk = data['trading_account']['private_key']
    return CLIConfig(data['node_url'], ContractAddress(data['core_address']),
                     ContractAddress(data['executor_address']),
                     ContractAddress(data['router_address']),
                     data['http'], data['wss'], tokens,
                     StarknetChainId.SEPOLIA if data['is_testnet']
                     else StarknetChainId.MAINNET, steps,
                     data['gas_oracle_skew_multiplier'], data['verbose'], (acc, pub, pk))


class CLIClient:
    """
    First what user need is to
    1) bind_to_signer -> binds public key of account address on layer akira smart contract
    2) approve exchange for tokens -> so exchange can transfer erc tokens on user invoking deposit
    3) execute deposits
    ....
    after this user can interact with API
    1) issue jwt token
    2) query gas -> for some trading activities user need specify max gas he willing to spend

    ....
    there is some presets command that one can use
    """

    def __init__(self, cli_cfg_path: str):
        self.cli_cfg = parse_cli_cfg(cli_cfg_path)

    async def start(self, domain):
        node_client = FullNodeClient(node_url=self.cli_cfg.node)
        erc_to_addr = {token.symbol: token.address for token in self.cli_cfg.tokens}
        contract_client = AkiraExchangeClient(node_client, self.cli_cfg.core_address,
                                              self.cli_cfg.executor_address, self.cli_cfg.router_address,
                                              erc_to_addr)
        await contract_client.init()

        sn_hasher = SnTypedPedersenHasher(erc_to_addr, domain, self.cli_cfg.core_address,
                                          self.cli_cfg.executor_address)
        self._erc_to_decimals = {token.symbol: token.decimals for token in self.cli_cfg.tokens}
        api_client = AsyncApiHttpClient(sn_hasher, lambda msg_hash, pk: message_signature(msg_hash, pk),
                                        self._erc_to_decimals, self.cli_cfg.http,
                                        verbose=self.cli_cfg.verbose)

        self.exchange_client = JointHttpClient(node_client, api_client, contract_client,
                                               self.cli_cfg.core_address,
                                               self.cli_cfg.executor_address,
                                               erc_to_addr,
                                               self._erc_to_decimals,
                                               self.cli_cfg.chain_id,
                                               self.cli_cfg.gas_multiplier,
                                               verbose=self.cli_cfg.verbose)

        await self.exchange_client.init()

        async def sub_consumer(d):
            logging.info(f'Subscription emitted {d}')

        async def handle_websocket_req(command: str, args: List[str]):
            if command == 'start_ws':
                asyncio.create_task(ws.run_stream_listener(ContractAddress(args[0]), True))
                return True
            elif command == 'subscribe_fills':
                print(await ws.subscribe_fills(ContractAddress(args[0]), sub_consumer))
                return True
            elif command == 'subscribe_book':
                print(await ws.subscribe_book(Stream(args[0]), TradedPair(ERC20Token(args[1]), ERC20Token(args[2])),
                                              bool(int(args[3])),
                                              sub_consumer))
                return True
            return False

        async def issue_listen_key(signer: ContractAddress):
            return (await self.exchange_client.query_listen_key(signer)).data

        ws = WsClient(self._erc_to_decimals, issue_listen_key, self.cli_cfg.wss, verbose=self.cli_cfg.verbose)
        trading_account = self.cli_cfg.trading_account[0]
        presets_commands = [
            ['set_account', self.cli_cfg.trading_account],
            # ['bind_to_signer', []],  # binds trading account to public key, can be invoked onlu once for trading account
            ['r_auth', []],  # issue jwt token

            ['display_chain_info', []],  # print chain info
            ['query_gas', []],  # query gas price
            ['user_info', []],  # query and ecosystem in Client user info from exchange
            ['start_ws', [self.cli_cfg.trading_account[1]]],
            ['sleep', []],
            ['subscribe_book', ['trade', 'ETH', 'USDC', '1']],
            ['subscribe_book', ['bbo', 'ETH', 'USDC', '1']],
            ['subscribe_book', ['snap', 'ETH', 'USDC', '1']],
            ['subscribe_fills', [self.cli_cfg.trading_account[0]]],
            #
            # ['approve_exchange', ['STRK', '1000']],
            # ['approve_exchange', ['USDC', '10000000000000']],
            # ['deposit', ['ETH', '0.0000000001']],
            # ['deposit', ['STRK', '1']],
            # ['request_withdraw_on_chain', ['USDC', '10']],
            # ['apply_onchain_withdraw', ['USDC', '0x267d006ca778631a91d85ef80b5d5b25aeacd9d989896b9ccf5a6ac760f1f69']],
            #
            # ['get_book', ['ETH/USDC', '1']],
            #
            # ['get_order', ['42']],
            # ['get_orders', ['1', '20', '0']],
            # #
            # # ['withdraw', ['USDC', '4']],
            # ['cancel_all', []],
            # ['refresh_chain_info', []],
            # ['user_info', []],

            # ['place_order', ['ETH/STRK', '250000', '0', '0.175000', 'SELL', 'LIMIT', '1', '0', '0', 'ROUTER', 0,
            #                  'INTERNAL', 0]],
            # ['place_order',
            #  ['ETH/USDC', '258403', '0', '0.516806', 'BUY', 'MARKET', '0', '0', '0', 'ROUTER', '0', 'INTERNAL',
            #   '0']],
            # ['place_order',
            #  ['ETH/USDC', '249803.1', '0', '0.250000', 'BUY', 'LIMIT', '1', '0', '0', 'ROUTER', '0', 'INTERNAL',
            #   '0']],
            # ['place_order',
            #  ['ETH/USDC', '244003', '0', '0.488006', 'SELL', 'MARKET', '0', '0', '0', 'ROUTER', '0', 'INTERNAL',
            #   '0']],

        ]

        for command, args in presets_commands:
            try:
                if self.cli_cfg.verbose: logging.info(f'Executing {command} {args}')
                if not await handle_websocket_req(command, args):
                    print(await self.handle_request(self.exchange_client, command, args, trading_account,
                                                    self.cli_cfg.gas_fee_steps))
            except Exception as e:
                logging.exception(e)
        while True:
            try:
                request = await ainput(">>> ")
                args = request.split()
                if self.cli_cfg.verbose: logging.info(f'Executing {args[0].strip()} {args[1:]}')
                if not await handle_websocket_req(args[0].strip(), args[1:]):
                    print(await self.handle_request(self.exchange_client, args[0].strip(), args[1:], trading_account,
                                                    self.cli_cfg.gas_fee_steps))
            except Exception as e:
                logging.exception(e)

    async def handle_request(self, client: JointHttpClient, command: str, args: List[str],
                             trading_account: Optional[ContractAddress],
                             gas_fee_steps: Dict[str, Dict[bool, int]]):
        async def wait_tx_receipt(tx_hash: str):
            is_succ, reciept_or_err = await client.akira._account_executor.wait_for_tx(tx_hash, 2, 60)
            if not is_succ:
                logging.warning(f'Failed to wait for receipt for {tx_hash} due {reciept_or_err}')
            return reciept_or_err

        if command.startswith('sleep'):
            return await asyncio.sleep(5)

        if command.startswith('query_gas'):
            return await client.query_gas_price(trading_account)

        elif command.startswith('set_account'):
            await client.handle_new_keys(ContractAddress(args[0]), ContractAddress(args[1]), args[2])

        elif command.startswith('display_chain_info'):
            return await client.display_chain_info(trading_account)

        elif command.startswith('approve_exchange'):
            tx_hash = await client.approve_exchange(trading_account, ERC20Token(args[0]), args[1])
            if tx_hash is not None: await wait_tx_receipt(tx_hash)
            return tx_hash

        elif command.startswith('deposit'):
            tx_hash = await client.deposit_on_exchange(trading_account, ERC20Token(args[0]), args[1])
            if tx_hash is not None: await wait_tx_receipt(tx_hash)
            return tx_hash
        elif command.startswith('approve_executor'):
            tx_hash = await client.approve_executor(trading_account)
            if tx_hash is not None: await wait_tx_receipt(tx_hash)
            return tx_hash

        elif command.startswith('refresh_chain_info'):
            return await client.refresh_onchain_balances_and_nonce_and_signer(trading_account)

        elif command.startswith('request_withdraw_on_chain'):
            res = await client.request_withdraw_on_chain(trading_account, ERC20Token(args[0]), args[1])
            if res is None: return
            await wait_tx_receipt(res[1])
            return res[0]

        elif command.startswith('apply_onchain_withdraw'):
            tx_hash = await client.apply_onchain_withdraw(trading_account, ERC20Token(args[0]), int(args[1], 16))
            if tx_hash is not None: await wait_tx_receipt(tx_hash)
            return tx_hash

        elif command.startswith('bind_to_signer'):
            tx_hash = await client.bind_to_signer(trading_account)
            if tx_hash is not None: await wait_tx_receipt(tx_hash)
            return tx_hash

        elif command.startswith('r_auth'):
            return await client.issue_jwt(trading_account)

        elif command.startswith('user_info'):
            return await client.get_trading_acc_info(trading_account)

        elif command.startswith('get_orders'):
            return await client.get_orders(trading_account, int(args[0]), int(args[1]), int(args[2]))

        elif command.startswith('get_order'):
            return await client.get_order(trading_account, int(args[0], 16 if args[0].startswith('0x') else 10))

        elif command.startswith('get_bbo'):
            b, q = args[0].split('/')
            b, q, is_ecosystem_book = ERC20Token(b), ERC20Token(q), bool(int(args[1]))
            return await client.get_bbo(trading_account, b, q, is_ecosystem_book)

        elif command.startswith('get_book'):
            b, q = args[0].split('/')
            b, q, is_ecosystem_book = ERC20Token(b), ERC20Token(q), bool(int(args[1]))
            return await client.get_snapshot(trading_account, b, q, is_ecosystem_book)

        elif command.startswith('place_order'):
            ticker, px, qty_base, qty_quote, side, type, post_only, full_fill, best_lvl, ecosystem, stp, external, min_receive_amount, apply_to_receipt_amount, gas_token = args
            min_receive_amount = str(min_receive_amount)
            base, quote = ticker.split('/')
            base, quote = ERC20Token(base), ERC20Token(quote)
            ecosystem = ecosystem == 'ECOSYSTEM'
            external = external == 'EXTERNAL'
            px = precise_to_price_convert(px, self._erc_to_decimals[quote])
            qty_base = precise_to_price_convert(qty_base, self._erc_to_decimals[base])
            qty_quote = precise_to_price_convert(qty_quote, self._erc_to_decimals[quote])
            min_receive_amount = precise_to_price_convert(min_receive_amount,
                                                          self._erc_to_decimals[base] if side == 'BUY'
                                                          else self._erc_to_decimals[quote])
            apply_to_receipt_amount = False if apply_to_receipt_amount.strip() == 'F_FEE_ON_SPEND' else True
            gas_token = ERC20Token(gas_token)
            if gas_token != ERC20Token.STRK:
                rate = await client.get_conversion_rate(trading_account, gas_token)
                fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, rate.data)
            else:
                fee = GAS_FEE_ACTION(client.gas_price, gas_fee_steps['swap'][ecosystem])
            return await client.place_order(trading_account, TradedPair(base, quote),
                                            px, qty_base, qty_quote, side, type, bool(int(post_only)),
                                            bool(int(full_fill)),
                                            bool(int(best_lvl)), ecosystem, trading_account,
                                            fee,
                                            stp=int(stp), external_funds=external,
                                            min_receive_amount=min_receive_amount,
                                            apply_fixed_fees_to_receipt=apply_to_receipt_amount
                                            )

        elif command.startswith('place_snip9_taker_order'):
            ticker, px, qty_base, side, type, min_receive_amount = args
            min_receive_amount = str(min_receive_amount)
            base, quote = ticker.split('/')
            base, quote = ERC20Token(base), ERC20Token(quote)
            ecosystem = False
            external = True
            px = precise_to_price_convert(px, self._erc_to_decimals[quote])
            qty_base = precise_to_price_convert(qty_base, self._erc_to_decimals[base])
            qty_quote = precise_to_price_convert("0", self._erc_to_decimals[quote])
            min_receive_amount = precise_to_price_convert(min_receive_amount,
                                                          self._erc_to_decimals[base] if side == 'BUY'
                                                          else self._erc_to_decimals[quote])
            apply_to_receipt_amount = True
            gas_token = base if side == 'BUY' else quote
            if gas_token != ERC20Token.STRK:
                rate = await client.get_conversion_rate(trading_account, gas_token)
                fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, rate.data)
            else:
                fee = GAS_FEE_ACTION(client.gas_price, gas_fee_steps['swap'][ecosystem])

            snip_9_calldata = self._get_snip9_calldata()
            return await client.place_order(trading_account, TradedPair(base, quote),
                                            px, qty_base, qty_quote, side, type,
                                            False, False, False,
                                            ecosystem, trading_account,
                                            fee,
                                            stp=0, external_funds=external,
                                            min_receive_amount=min_receive_amount,
                                            apply_fixed_fees_to_receipt=apply_to_receipt_amount,
                                            snip_9_calldata=snip_9_calldata
                                            )

        elif command.startswith('cancel_order'):
            return await client.cancel_order(trading_account, trading_account,
                                             int(args[0], 16 if args[0].startswith('0x') else 10))

        elif command.startswith('cancel_all'):
            ticker, ecosystem = args
            base, quote = ticker.split('/')
            base, quote = ERC20Token(base), ERC20Token(quote)
            ecosystem = ecosystem == 'ECOSYSTEM'
            return await client.cancel_all_orders(trading_account, trading_account,
                                                  SpotTicker(TradedPair(base, quote), ecosystem))

        elif command.startswith('increase_nonce'):
            return await client.increase_nonce(trading_account, trading_account, int(args[0]),
                                               GAS_FEE_ACTION(client.gas_price, gas_fee_steps['nonce'][True]))


        elif command.startswith('withdraw'):
            erc = ERC20Token(args[0])
            amount = precise_to_price_convert(args[1], self._erc_to_decimals[erc])
            return await client.withdraw(trading_account, trading_account, erc, amount,
                                         GAS_FEE_ACTION(client.gas_price, gas_fee_steps['withdraw'][True]))

        elif command.startswith('query_listen_key'):
            return await client.query_listen_key(trading_account)
        else:
            print(f'Unknown command {command} with args {args}')
