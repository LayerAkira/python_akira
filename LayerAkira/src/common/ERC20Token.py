class ERC20Token(str):
    __slots__ = ()

    @property
    def value(self) -> str:
        """support old semantics"""
        return str(self)


TEST_TOKENS = [ERC20Token("AUSDC"), ERC20Token("AUSDT"), ERC20Token("AETH")]
