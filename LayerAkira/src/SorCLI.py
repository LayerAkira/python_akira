from dataclasses import dataclass
from typing import List, Tuple, Dict

from LayerAkira.src.common.ContractAddress import ContractAddress
from LayerAkira.src.common.ERC20Token import ERC20Token
from LayerAkira.src.common.FeeTypes import GasFee, OrderFee, FixedFee
from LayerAkira.src.common.Requests import SorContext, MinimalTakerOrderInfo, Quantity
from LayerAkira.src.common.TradedPair import TradedPair
from LayerAkira.src.common.common import precise_to_price_convert
from LayerAkira.src.common.constants import SNIP_9_ANY_CALLER, ZERO_ADDRESS
from LayerAkira.src.JointHttpClient import JointHttpClient


@dataclass
class SorPair:
    token_in: ERC20Token
    token_out: ERC20Token
    base_token: ERC20Token
    quote_token: ERC20Token


@dataclass
class SorPath:
    name: str
    description: str
    pairs: List[SorPair]


# Predefined SOR paths
SOR_PATHS = {
    "strk_p": SorPath(
        name="strk_circle",
        description="STRK -> AUSDC -> AUSDT",
        pairs=[
            SorPair(ERC20Token.STRK, ERC20Token.AUSDC, ERC20Token.STRK, ERC20Token.AUSDC),
            SorPair(ERC20Token.AUSDC, ERC20Token.AUSDT, ERC20Token.AUSDC, ERC20Token.AUSDT)
        ]
    ),
    "eth_p": SorPath(
        name="eth_circle",
        description="ETH -> AUSDC -> AUSDT",
        pairs=[
            SorPair(ERC20Token.ETH, ERC20Token.AUSDC, ERC20Token.ETH, ERC20Token.AUSDC),
            SorPair(ERC20Token.AUSDC, ERC20Token.AUSDT, ERC20Token.AUSDC, ERC20Token.AUSDT)
        ]
    ),
    "test_p": SorPath(
        name="eth_circle",
        description="AUSDC -> AETH -> STRK",
        pairs=[
            SorPair(ERC20Token.AUSDC, ERC20Token.AETH, ERC20Token.AETH, ERC20Token.AUSDC),
            SorPair(ERC20Token.AETH, ERC20Token.STRK, ERC20Token.AETH, ERC20Token.STRK)
        ]
    )
}


class SorCLI:
    def __init__(self, token_to_decimals: Dict[ERC20Token, int]):
        self._token_to_decimals = token_to_decimals

    def list_sor_paths(self):
        """List all available SOR paths"""
        print("Available SOR paths:")
        for name, path in SOR_PATHS.items():
            print(f"{name}: {path.description}")
        return None

    async def place_sor_taker_order(self, client: JointHttpClient, trading_account: ContractAddress,
                                  args: List[str], gas_fee_steps: Dict[str, Dict[bool, int]]):
        """Place a SOR taker order using a predefined path"""
        if len(args) < 3:
            print("Usage: place_sor_taker_order <path_name> <qty> <price1> [price2] [price3] <last_qty>")
            return None

        path_name = args[0]
        if path_name not in SOR_PATHS:
            print(f"Unknown path: {path_name}. Use 'list_sor_paths' to see available paths.")
            return None

        path = SOR_PATHS[path_name]
        qty_first = precise_to_price_convert(args[1], self._token_to_decimals[path.pairs[0].token_in])
        lb, lq = (qty_first, 0) if path.pairs[0].token_in == path.pairs[0].base_token else (0, qty_first)
        
        # Extract prices from args
        prices = [price for price in args[2:2+len(path.pairs)]]
        
        if len(prices) != len(path.pairs):
            print(f"Expected {len(path.pairs)} prices for path {path_name}, got {len(prices)}")
            return None
            
        # Get the last_qty value (should be the last argument)
        if len(args) < 3 + len(path.pairs):
            print(f"Missing last_qty parameter")
            return None
            
        # Determine last token for decimals
        last_pair = path.pairs[-1]
        last_token = last_pair.token_out
        
        # Use the correct number of decimals for the last token
        last_qty_value = precise_to_price_convert(args[2 + len(path.pairs)], self._token_to_decimals[last_token])
        
        # Create SOR path with prices
        path_info = []
        
        for i, pair in enumerate(path.pairs):
            raw_price = precise_to_price_convert(prices[i], self._token_to_decimals[pair.token_out])
            is_sell_side = pair.token_in == pair.base_token
            
            if pair.token_in != pair.base_token:
                base_decimals = self._token_to_decimals[pair.base_token]
                quote_decimals = self._token_to_decimals[pair.quote_token]
                price = (10 ** (base_decimals + quote_decimals)) // raw_price if raw_price > 0 else 0
            else:
                price = raw_price
            
            path_info.append(MinimalTakerOrderInfo(
                price=price,
                ticker=TradedPair(pair.base_token, pair.quote_token),
                is_sell_side=is_sell_side,
                base_asset=10 ** self._token_to_decimals[pair.base_token]
            ))

        # Get fee parameters for the first pair
        (ecosystem, external,
         min_receive_amount, apply_to_receipt_amount, gas_fee) = await self._prepare_taker_order_params(
            client, trading_account, gas_fee_steps)
        
        # Check if last token is base or quote in the last pair
        is_base = (last_token == last_pair.base_token)
        
        # Set b and q based on whether last token is base or quote
        b = last_qty_value if is_base else 0
        q = 0 if is_base else last_qty_value
        bt = last_pair.base_token

        # Create SOR context
        sor_context = SorContext(
            path=path_info,
            order_fee=None,
            allow_non_atomic=False,
            min_receive_amount=min_receive_amount,
            max_spend_amount=0,
            last_qty=Quantity(b, q, 10 ** self._token_to_decimals[bt])
        )

        return await client.place_order(trading_account,
                                        TradedPair(path.pairs[0].base_token, path.pairs[0].quote_token),
                                        path_info[0].price,
                                        lb, lq,
                                        "SELL" if path.pairs[0].token_in == path.pairs[0].base_token else "BUY", "MARKET",
                                        False, False, False,
                                        ecosystem, trading_account,
                                        gas_fee,
                                        stp=0, external_funds=external,
                                        min_receive_amount=min_receive_amount,
                                        apply_fixed_fees_to_receipt=apply_to_receipt_amount,
                                        snip_9=True,
                                        caller=SNIP_9_ANY_CALLER,
                                        sor_context=sor_context
                                        )

    async def _prepare_taker_order_params(self, client: JointHttpClient, trading_account: ContractAddress,
                                        gas_fee_steps: Dict[str, Dict[bool, int]]) -> Tuple:
        ecosystem = False
        external = True
        min_receive_amount = 0

        apply_to_receipt_amount = False
        gas_token = ERC20Token.STRK
        if gas_token != ERC20Token.STRK:
            rate = await client.get_conversion_rate(trading_account, gas_token)
            fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, rate.data)
        else:
            fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, (1, 1))

        return (ecosystem, external,
                min_receive_amount, apply_to_receipt_amount, fee) 