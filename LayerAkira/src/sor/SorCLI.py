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
            SorPair(ERC20Token("STRK"), ERC20Token("AUSDC"), ERC20Token("STRK"), ERC20Token("AUSDC")),
            SorPair(ERC20Token("AUSDC"), ERC20Token("AUSDT"), ERC20Token("AUSDC"), ERC20Token("AUSDT"))
        ]
    ),
    "aeth_p": SorPath(
        name="aeth_circle",
        description="AETH -> AUSDC -> AUSDT",
        pairs=[
            SorPair(ERC20Token("AETH"), ERC20Token("AUSDC"), ERC20Token("AETH"), ERC20Token("AUSDC")),
            SorPair(ERC20Token("AUSDC"), ERC20Token("AUSDT"), ERC20Token("AUSDC"), ERC20Token("AUSDT"))
        ]
    ),
    "test_p": SorPath(
        name="test_circle",
        description="AUSDC -> AETH -> AUSDT",
        pairs=[
            SorPair(ERC20Token("AUSDC"), ERC20Token("AETH"), ERC20Token("AETH"), ERC20Token("AUSDC")),
            SorPair(ERC20Token("AETH"), ERC20Token("AUSDT"), ERC20Token("AETH"), ERC20Token("AUSDT"))
        ]
    ),
    "test_p02": SorPath(
        name="test02_circle",
        description="AETH -> AUSDC -> AUSDT",
        pairs=[
            SorPair(ERC20Token("AETH"), ERC20Token("AUSDC"), ERC20Token("AETH"), ERC20Token("AUSDC")),
            SorPair(ERC20Token("AUSDC"), ERC20Token("AUSDT"), ERC20Token("AUSDC"), ERC20Token("AUSDT"))
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

    async def _validate_input_args(self, args: List[str], path: SorPath) -> Tuple[bool, str]:
        """Validate input arguments for SOR taker order"""
        if len(args) < 3:
            return False, "Usage: place_sor_taker_order <path_name> <qty> <price1> [price2] [price3] <last_qty>"
            
        prices = [price for price in args[2:2+len(path.pairs)]]
        if len(prices) != len(path.pairs):
            return False, f"Expected {len(path.pairs)} prices for path, got {len(prices)}"
            
        if len(args) < 3 + len(path.pairs):
            return False, "Missing last_qty parameter"
            
        return True, ""

    async def _create_path_info(self, path: SorPath, prices: List[str]) -> List[MinimalTakerOrderInfo]:
        """Create path info with prices for each pair"""
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
        return path_info

    async def _create_sor_context(self, path_info: List[MinimalTakerOrderInfo], 
                                last_pair: SorPair, last_token: ERC20Token,
                                last_qty_value: int, min_receive_amount: int) -> SorContext:
        """Create SOR context for the order"""
        is_base = (last_token == last_pair.base_token)
        b = last_qty_value if is_base else 0
        q = 0 if is_base else last_qty_value
        bt = last_pair.base_token

        return SorContext(
            path=path_info,
            order_fee=None,
            allow_non_atomic=False,
            min_receive_amount=min_receive_amount,
            max_spend_amount=0,
            last_qty=Quantity(b, q, 10 ** self._token_to_decimals[bt])
        )

    async def place_sor_taker_order(self, client: JointHttpClient, trading_account: ContractAddress,
                                  args: List[str], gas_fee_steps: Dict[str, Dict[bool, int]]):
        """Place a SOR taker order using a predefined path"""
        path_name = args[0]
        if path_name not in SOR_PATHS:
            print(f"Unknown path: {path_name}. Use 'list_sor_paths' to see available paths.")
            return None

        path = SOR_PATHS[path_name]
        
        # Validate input arguments
        is_valid, error_msg = await self._validate_input_args(args, path)
        if not is_valid:
            print(error_msg)
            return None

        # Process first pair quantities
        first_pair = path.pairs[0]
        qty_first = precise_to_price_convert(args[1], self._token_to_decimals[first_pair.token_in])
        lb, lq = (qty_first, 0) if first_pair.token_in == first_pair.base_token else (0, qty_first)
        
        # Extract prices
        prices = [price for price in args[2:2+len(path.pairs)]]
        
        # Process last pair quantities
        last_pair = path.pairs[-1]
        last_token = last_pair.token_out
        last_qty_value = precise_to_price_convert(args[2 + len(path.pairs)], self._token_to_decimals[last_token])
        
        # Create path info
        path_info = await self._create_path_info(path, prices)
        
        # Get fee parameters
        first_ticker = TradedPair(first_pair.base_token, first_pair.quote_token)

        side = "SELL" if first_pair.token_in == first_pair.base_token else "BUY"

        (ecosystem, external,
         min_receive_amount, apply_to_receipt_amount, gas_fee) = await self._prepare_taker_order_params(
            first_ticker, side,
            client, trading_account, gas_fee_steps)
        
        # Create SOR context
        sor_context = await self._create_sor_context(
            path_info[1:], last_pair, last_token, last_qty_value, min_receive_amount)

        return await client.place_order(trading_account,
                                        first_ticker,
                                        path_info[0].price,
                                        lb, lq,
                                        side,
                                        "MARKET",
                                        False, True, False,
                                        ecosystem,
                                        trading_account,
                                        gas_fee,
                                        stp=0,
                                        external_funds=external,
                                        min_receive_amount=min_receive_amount,
                                        apply_fixed_fees_to_receipt=apply_to_receipt_amount,
                                        snip_9=True,
                                        caller=SNIP_9_ANY_CALLER,
                                        sor_context=sor_context
                                        )

    async def _prepare_taker_order_params(self, token: TradedPair, side,
                                          client: JointHttpClient, trading_account: ContractAddress,
                                        gas_fee_steps: Dict[str, Dict[bool, int]]) -> Tuple:
        ecosystem = False
        external = True
        min_receive_amount = 0

        apply_to_receipt_amount = False
        gas_token = token.base if side == 'BUY' else token.quote
        if gas_token != ERC20Token("STRK"):
            rate = await client.get_conversion_rate(trading_account, gas_token)
            fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, rate.data)
        else:
            fee = GasFee(gas_fee_steps['swap'][ecosystem], gas_token, client.gas_price, (1, 1))

        return (ecosystem, external,
                min_receive_amount, apply_to_receipt_amount, fee) 