withdraw_type = {
    "StarkNetDomain": [
        {
            "name": "name",
            "type": "felt"
        },
        {
            "name": "version",
            "type": "felt"
        },
        {
            "name": "chainId",
            "type": "felt"
        }
    ],
    "Withdraw": [
        {
            "name": "maker",
            "type": "felt"
        },
        {
            "name": "token",
            "type": "felt"
        },
        {
            "name": "amount",
            "type": "u256"
        },
        {
            "name": "salt",
            "type": "felt"
        },
        {
            "name": "gas_fee",
            "type": "GasFee"
        },
        {
            "name": "receiver",
            "type": "felt"
        },
        {
            "name": "exchange",
            "type": "felt"
        },
        {
            "name": "sign_scheme",
            "type": "felt"
        }
    ],
    "u256": [
        {
            "name": "low",
            "type": "felt"
        },
        {
            "name": "high",
            "type": "felt"
        }
    ],
    "GasFee": [
        {
            "name": "gas_per_action",
            "type": "felt"
        },
        {
            "name": "fee_token",
            "type": "felt"
        },
        {
            "name": "max_gas_price",
            "type": "u256"
        },
        {
            "name": "r0",
            "type": "u256"
        },
        {
            "name": "r1",
            "type": "u256"
        }
    ]
}

order_type = {
    "StarkNetDomain": [
        {
            "name": "name",
            "type": "felt"
        },
        {
            "name": "version",
            "type": "felt"
        },
        {
            "name": "chainId",
            "type": "felt"
        }
    ],
    "Order": [
        {
            "name": "maker",
            "type": "felt"
        },
        {
            "name": "price",
            "type": "u256"
        },
        {
            "name": "qty",
            "type": "Quantity"
        },
        {
            "name": "base",
            "type": "felt"
        },
        {
            "name": "quote",
            "type": "felt"
        },
        {
            "name": "fee",
            "type": "OrderFee"
        },
        {
            "name": "constraints",
            "type": "Constraints"
        },
        {
            "name": "salt",
            "type": "felt"
        },
        {
            "name": "flags",
            "type": "OrderFlags"
        },
        {
            "name": "exchange",
            "type": "felt"
        },
        {
            "name": "source",
            "type": "felt"
        },
        {
            "name": "sign_scheme",
            "type": "felt"
        }
    ],
    "u256": [
        {
            "name": "low",
            "type": "felt"
        },
        {
            "name": "high",
            "type": "felt"
        }
    ],
    "FixedFee": [
        {
            "name": "recipient",
            "type": "felt"
        },
        {
            "name": "maker_pbips",
            "type": "felt"
        },
        {
            "name": "taker_pbips",
            "type": "felt"
        },
        {
            "name": "apply_to_receipt_amount",
            "type": "bool"
        }
    ],
    "Constraints": [
        {
            "name": "number_of_swaps_allowed",
            "type": "felt"
        },
        {
            "name": "duration_valid",
            "type": "felt"
        },
        {
            "name": "created_at",
            "type": "felt"
        },
        {
            "name": "stp",
            "type": "felt"
        },
        {
            "name": "nonce",
            "type": "felt"
        },
        {
            "name": "min_receive_amount",
            "type": "u256"
        },
        {
            "name": "router_signer",
            "type": "felt"
        }
    ],
    "Quantity": [
        {
            "name": "base_qty",
            "type": "u256"
        },
        {
            "name": "quote_qty",
            "type": "u256"
        },
        {
            "name": "base_asset",
            "type": "u256"
        }
    ],
    "GasFee": [
        {
            "name": "gas_per_action",
            "type": "felt"
        },
        {
            "name": "fee_token",
            "type": "felt"
        },
        {
            "name": "max_gas_price",
            "type": "u256"
        },
        {
            "name": "r0",
            "type": "u256"
        },
        {
            "name": "r1",
            "type": "u256"
        }
    ],
    "OrderFee": [
        {
            "name": "trade_fee",
            "type": "FixedFee"
        },
        {
            "name": "router_fee",
            "type": "FixedFee"
        },
        {
            "name": "gas_fee",
            "type": "GasFee"
        }
    ],
    "OrderFlags": [
        {
            "name": "full_fill_only",
            "type": "bool"
        },
        {
            "name": "best_level_only",
            "type": "bool"
        },
        {
            "name": "post_only",
            "type": "bool"
        },
        {
            "name": "is_sell_side",
            "type": "bool"
        },
        {
            "name": "is_market_order",
            "type": "bool"
        },
        {
            "name": "to_ecosystem_book",
            "type": "bool"
        },
        {
            "name": "external_funds",
            "type": "bool"
        }
    ]
}

cancel_type = {
    "StarkNetDomain": [
        {
            "name": "name",
            "type": "felt"
        },
        {
            "name": "version",
            "type": "felt"
        },
        {
            "name": "chainId",
            "type": "felt"
        }
    ],
    "CancelOrder": [
        {
            "name": "maker",
            "type": "felt"
        },
        {
            "name": "order_hash",
            "type": "felt"
        },
        {
            "name": "salt",
            "type": "felt"
        }
    ]
}

cancel_all_type = {
    "StarkNetDomain": [
        {
            "name": "name",
            "type": "felt"
        },
        {
            "name": "version",
            "type": "felt"
        },
        {
            "name": "chainId",
            "type": "felt"
        }
    ],
    "Ticker": [
        {
            "name": "base",
            "type": "felt"
        },
        {
            "name": "quote",
            "type": "felt"
        },
        {
            "name": "to_ecosystem_book",
            "type": "bool"
        },
    ],
    "CancelAllOrders": [
        {
            "name": "maker",
            "type": "felt"
        },
        {
            "name": "salt",
            "type": "felt"
        },
        {
            "name": "ticker",
            "type": "Ticker"
        },

    ]
}
cancel_all_onchain_type = {
    "StarkNetDomain": [
        {
            "name": "name",
            "type": "felt"
        },
        {
            "name": "version",
            "type": "felt"
        },
        {
            "name": "chainId",
            "type": "felt"
        }
    ],
    "OnchainCancelAll": [
        {
            "name": "maker",
            "type": "felt"
        },
        {
            "name": "new_nonce",
            "type": "felt"
        },
        {
            "name": "gas_fee",
            "type": "GasFee"
        },
        {
            "name": "sign_scheme",
            "type": "felt"
        }
    ],
    "u256": [
        {
            "name": "low",
            "type": "felt"
        },
        {
            "name": "high",
            "type": "felt"
        }
    ],
    "GasFee": [
        {
            "name": "gas_per_action",
            "type": "felt"
        },
        {
            "name": "fee_token",
            "type": "felt"
        },
        {
            "name": "max_gas_price",
            "type": "u256"
        },
        {
            "name": "r0",
            "type": "u256"
        },
        {
            "name": "r1",
            "type": "u256"
        }
    ]
}
