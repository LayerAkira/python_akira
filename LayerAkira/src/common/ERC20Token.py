from typing import NewType

ERC20Token = NewType('ERC20Token', str)

TEST_TOKENS = [ERC20Token("AUSDC"), ERC20Token("AUSDT"), ERC20Token("AETH")]
