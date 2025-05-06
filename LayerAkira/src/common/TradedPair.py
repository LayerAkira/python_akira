from dataclasses import dataclass

from LayerAkira.src.common.ERC20Token import ERC20Token


@dataclass
class TradedPair:
    base: ERC20Token
    quote: ERC20Token

    def __hash__(self):
        return hash((self.base, self.quote))
