import asyncio
import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple
from typing import Optional

import toml
from aioconsole import ainput
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from LayerAkira.src.HttpClient import HttpClient, GAS_FEE_ACTION
from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.WsClient import WsClient, Stream


@dataclass
class ERC20Spec:
    symbol: ERC20Token
    address: ContractAddress
    decimals: int


@dataclass
class CLIConfig:
    node: str
    exchange_address: ContractAddress
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
        steps[d['action']][d['safe']] = d['steps']
    acc = ContractAddress(data['trading_account']['account_address'])
    pub = ContractAddress(data['trading_account']['public_key'])
    pk = data['trading_account']['private_key']
    return CLIConfig(data['node_url'], ContractAddress(data['exchange_address']), data['http'], data['wss'], tokens,
                     StarknetChainId.TESTNET if data['is_testnet'] else StarknetChainId.MAINNET, steps,
                     data['gas_oracle_skew_multiplier'], data['verbose'], (acc, pub, pk))


class CLIClient:

    @staticmethod
    async def start(cli_cfg_path: str,logs_file_path='logs.txt'):
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename=logs_file_path)

        cli_cfg = parse_cli_cfg(cli_cfg_path)
        client = FullNodeClient(node_url=cli_cfg.node)
        erc_to_addr = {token.symbol: token.address for token in cli_cfg.tokens}
        erc_to_decimals = {token.symbol: token.decimals for token in cli_cfg.tokens}
        http_client = HttpClient(client, cli_cfg.exchange_address, erc_to_addr, erc_to_decimals, cli_cfg.chain_id,
                                 cli_cfg.http,
                                 cli_cfg.gas_multiplier, verbose=cli_cfg.verbose)
        await http_client.init()

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

        async def issue_listen_key(acc: ContractAddress):
            return await http_client.query_listen_key(acc)

        ws = WsClient(issue_listen_key, cli_cfg.wss, verbose=cli_cfg.verbose)
        trading_account = cli_cfg.trading_account[0]
        presets_commands = [
            ['set_account', cli_cfg.trading_account],
            # ['bind_to_signer', []],  # binds trading account to public key, can be invoked onlu once for trading account
            ['display_chain_info', []],  # print chain info
            ['r_auth', []],  # issue jwt token
            ['query_gas', []],  # query gas price
            ['user_info', []],  # query and safe in Client user info from exchange
            ['start_ws', [cli_cfg.trading_account[1]]],
            ['subscribe_book', ['trade', 'ETH', 'USDC', '1']],
            ['subscribe_book', ['bbo', 'ETH', 'USDC', '1']],
            ['subscribe_book', ['snap', 'ETH', 'USDC', '1']],
            ['subscribe_fills', [cli_cfg.trading_account[0]]],

            # ['approve_exchange', ['ETH', '1000']],
            # ['approve_exchange', ['USDC', '10000000000000']],
            # ['deposit', ['ETH', '0.0000000001']],
            # ['deposit', ['USDC', '50']],
            # ['request_withdraw_on_chain', ['USDC', '10']],
            ['apply_onchain_withdraw', ['USDC', '0x267d006ca778631a91d85ef80b5d5b25aeacd9d989896b9ccf5a6ac760f1f69']],
            #
            # ['get_bbo', ['ETH/USDC', '1']],
            # ['get_book', ['ETH/USDC', '1']],
            #
            # ['get_order', ['42']],
            # ['get_orders', ['1', '20', '0']],
            #
            # ['withdraw', ['USDC', '4']],
            # ['place_order', ['ETH/USDC', '1945', '0.00000011', 'BUY', 'LIMIT', '1', '0', '0', 'SAFE']],
            # ['place_order', ['ETH/USDC', '1945', '0.00000011', 'SELL', 'LIMIT', '1', '0', '0', 'SAFE']],
            # ['cancel_order', ['345345']],
            # ['cancel_all', []]
            #     'withdraw 0x0541cf2823e5d004E9a5278ef8B691B97382FD0c9a6B833a56131E12232A7F0F USDC 25'
        ]

        for command, args in presets_commands:
            try:
                if cli_cfg.verbose: logging.info(f'Executing {command} {args}')
                if not await handle_websocket_req(command, args):
                    print(await CLIClient.handle_request(http_client, command, args, trading_account, cli_cfg.gas_fee_steps))
            except Exception as e:
                logging.error(e)
        while True:
            try:
                request = await ainput(">>> ")
                args = request.split()
                if cli_cfg.verbose: logging.info(f'Executing {args[0].strip()} {args[1:]}')
                if not await handle_websocket_req(args[0].strip(), args[1:]):
                    print(await CLIClient.handle_request(http_client, args[0].strip(), args[1:], trading_account,
                                                         cli_cfg.gas_fee_steps))
            except Exception as e:
                logging.error(e)

    @staticmethod
    async def handle_request(client: HttpClient, command: str, args: List[str],
                             trading_account: Optional[ContractAddress],
                             gas_fee_steps: Dict[str, Dict[bool, int]]):
        async def wait_tx_receipt(tx_hash: str):
            is_succ, reciept_or_err = await client.akira.account_executor.wait_for_tx(tx_hash, 2, 60)
            if not is_succ:
                logging.warning(f'Failed to wait for receipt for {tx_hash} due {reciept_or_err}')
            return reciept_or_err

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
            return await client.get_order(trading_account, int(args[0]))

        elif command.startswith('get_bbo'):
            b, q = args[0].split('/')
            b, q, is_safe_book = ERC20Token(b), ERC20Token(q), bool(int(args[1]))
            return await client.get_bbo(trading_account, b, q, is_safe_book)

        elif command.startswith('get_book'):
            b, q = args[0].split('/')
            b, q, is_safe_book = ERC20Token(b), ERC20Token(q), bool(int(args[1]))
            return await client.get_snapshot(trading_account, b, q, is_safe_book)

        elif command.startswith('place_order'):
            ticker, px, qty, side, type, post_only, full_fill, best_lvl, safe = args
            base, quote = ticker.split('/')
            base, quote = ERC20Token(base), ERC20Token(quote)
            safe = safe == 'SAFE'

            return await client.place_order(trading_account, TradedPair(base, quote),
                                            px, qty, side, type, bool(int(post_only)), bool(int(full_fill)),
                                            bool(int(best_lvl)), safe, trading_account,
                                            GAS_FEE_ACTION(client.gas_price, gas_fee_steps['swap'][safe]), None
                                            )

        elif command.startswith('cancel_order'):
            return await client.cancel_order(trading_account, trading_account, int(args[0]))

        elif command.startswith('cancel_all'):
            return await client.cancel_order(trading_account, trading_account, None)

        elif command.startswith('withdraw'):
            return await client.withdraw(trading_account, trading_account, ERC20Token(args[0]), args[1],
                                         GAS_FEE_ACTION(client.gas_price, gas_fee_steps['withdraw'][True]))

        elif command.startswith('query_listen_key'):
            return await client.query_listen_key(trading_account)
        else:
            print(f'Unknown command {command} with args {args}')
