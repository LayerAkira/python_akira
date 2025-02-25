from LayerAkira.src.common.ContractAddress import ContractAddress

ZERO_ADDRESS = ContractAddress(0)
TEST_TOKEN_APPROVE_SELECTOR = "0x0219209e083275171774dab1df80982e9df2096516f06319c5c6d71ae0a8480c"
TOKEN_APPROVE_SELECTOR = "0x016cc063b8338363cf388ce7fe1df408bf10f16cd51635d392e21d852fafb683"
PLACE_TAKER_ORDER_SELECTOR = "0x00bb3dd10d3b0070a8bc931f1104806bf5e2d717c6e961d8d258bed8a7a108ab"

ERC20ABI = [
            {
                "name": "Uint256",
                "size": 2,
                "type": "struct",
                "members": [
                    {
                        "name": "low",
                        "type": "felt",
                        "offset": 0
                    },
                    {
                        "name": "high",
                        "type": "felt",
                        "offset": 1
                    }
                ]
            },
            {
                "data": [
                    {
                        "name": "from_",
                        "type": "felt"
                    },
                    {
                        "name": "to",
                        "type": "felt"
                    },
                    {
                        "name": "value",
                        "type": "Uint256"
                    }
                ],
                "keys": [],
                "name": "Transfer",
                "type": "event"
            },
            {
                "data": [
                    {
                        "name": "owner",
                        "type": "felt"
                    },
                    {
                        "name": "spender",
                        "type": "felt"
                    },
                    {
                        "name": "value",
                        "type": "Uint256"
                    }
                ],
                "keys": [],
                "name": "Approval",
                "type": "event"
            },
            {
                "name": "name",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "name",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "symbol",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "symbol",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "totalSupply",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "totalSupply",
                        "type": "Uint256"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "decimals",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "decimals",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "balanceOf",
                "type": "function",
                "inputs": [
                    {
                        "name": "account",
                        "type": "felt"
                    }
                ],
                "outputs": [
                    {
                        "name": "balance",
                        "type": "Uint256"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "allowance",
                "type": "function",
                "inputs": [
                    {
                        "name": "owner",
                        "type": "felt"
                    },
                    {
                        "name": "spender",
                        "type": "felt"
                    }
                ],
                "outputs": [
                    {
                        "name": "remaining",
                        "type": "Uint256"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "permittedMinter",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "minter",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "initialized",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "res",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "get_version",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "version",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "get_identity",
                "type": "function",
                "inputs": [],
                "outputs": [
                    {
                        "name": "identity",
                        "type": "felt"
                    }
                ],
                "stateMutability": "view"
            },
            {
                "name": "initialize",
                "type": "function",
                "inputs": [
                    {
                        "name": "init_vector_len",
                        "type": "felt"
                    },
                    {
                        "name": "init_vector",
                        "type": "felt*"
                    }
                ],
                "outputs": []
            },
            {
                "name": "transfer",
                "type": "function",
                "inputs": [
                    {
                        "name": "recipient",
                        "type": "felt"
                    },
                    {
                        "name": "amount",
                        "type": "Uint256"
                    }
                ],
                "outputs": [
                    {
                        "name": "success",
                        "type": "felt"
                    }
                ]
            },
            {
                "name": "transferFrom",
                "type": "function",
                "inputs": [
                    {
                        "name": "sender",
                        "type": "felt"
                    },
                    {
                        "name": "recipient",
                        "type": "felt"
                    },
                    {
                        "name": "amount",
                        "type": "Uint256"
                    }
                ],
                "outputs": [
                    {
                        "name": "success",
                        "type": "felt"
                    }
                ]
            },
            {
                "name": "approve",
                "type": "function",
                "inputs": [
                    {
                        "name": "spender",
                        "type": "felt"
                    },
                    {
                        "name": "amount",
                        "type": "Uint256"
                    }
                ],
                "outputs": [
                    {
                        "name": "success",
                        "type": "felt"
                    }
                ]
            },
            {
                "name": "increaseAllowance",
                "type": "function",
                "inputs": [
                    {
                        "name": "spender",
                        "type": "felt"
                    },
                    {
                        "name": "added_value",
                        "type": "Uint256"
                    }
                ],
                "outputs": [
                    {
                        "name": "success",
                        "type": "felt"
                    }
                ]
            },
            {
                "name": "decreaseAllowance",
                "type": "function",
                "inputs": [
                    {
                        "name": "spender",
                        "type": "felt"
                    },
                    {
                        "name": "subtracted_value",
                        "type": "Uint256"
                    }
                ],
                "outputs": [
                    {
                        "name": "success",
                        "type": "felt"
                    }
                ]
            },
            {
                "name": "permissionedMint",
                "type": "function",
                "inputs": [
                    {
                        "name": "recipient",
                        "type": "felt"
                    },
                    {
                        "name": "amount",
                        "type": "Uint256"
                    }
                ],
                "outputs": []
            },
            {
                "name": "permissionedBurn",
                "type": "function",
                "inputs": [
                    {
                        "name": "account",
                        "type": "felt"
                    },
                    {
                        "name": "amount",
                        "type": "Uint256"
                    }
                ],
                "outputs": []
            }
        ]