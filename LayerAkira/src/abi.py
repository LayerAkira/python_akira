core_abi = [
  {
    "type": "impl",
    "name": "ExchangeBalancebleImpl",
    "interface_name": "kurosawa_akira::ExchangeBalanceComponent::INewExchangeBalance"
  },
  {
    "type": "struct",
    "name": "core::integer::u256",
    "members": [
      {
        "name": "low",
        "type": "core::integer::u128"
      },
      {
        "name": "high",
        "type": "core::integer::u128"
      }
    ]
  },
  {
    "type": "struct",
    "name": "core::array::Span::<core::starknet::contract_address::ContractAddress>",
    "members": [
      {
        "name": "snapshot",
        "type": "@core::array::Array::<core::starknet::contract_address::ContractAddress>"
      }
    ]
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::ExchangeBalanceComponent::INewExchangeBalance",
    "items": [
      {
        "type": "function",
        "name": "total_supply",
        "inputs": [
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "balanceOf",
        "inputs": [
          {
            "name": "address",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "balancesOf",
        "inputs": [
          {
            "name": "addresses",
            "type": "core::array::Span::<core::starknet::contract_address::ContractAddress>"
          },
          {
            "name": "tokens",
            "type": "core::array::Span::<core::starknet::contract_address::ContractAddress>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<core::array::Array::<core::integer::u256>>"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_wrapped_native_token",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_fee_recipient",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "DepositableImpl",
    "interface_name": "kurosawa_akira::DepositComponent::IDeposit"
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::DepositComponent::IDeposit",
    "items": [
      {
        "type": "function",
        "name": "deposit",
        "inputs": [
          {
            "name": "receiver",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "deposit_s",
        "inputs": [
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      }
    ]
  },
  {
    "type": "impl",
    "name": "SignableImpl",
    "interface_name": "kurosawa_akira::SignerComponent::ISignerLogic"
  },
  {
    "type": "struct",
    "name": "core::array::Span::<core::felt252>",
    "members": [
      {
        "name": "snapshot",
        "type": "@core::array::Array::<core::felt252>"
      }
    ]
  },
  {
    "type": "enum",
    "name": "core::bool",
    "variants": [
      {
        "name": "False",
        "type": "()"
      },
      {
        "name": "True",
        "type": "()"
      }
    ]
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::SignerComponent::ISignerLogic",
    "items": [
      {
        "type": "function",
        "name": "bind_to_signer",
        "inputs": [
          {
            "name": "signer",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "set_till_time_approved_scheme",
        "inputs": [
          {
            "name": "sign_scheme",
            "type": "core::felt252"
          },
          {
            "name": "expire_at",
            "type": "core::integer::u32"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "get_till_time_approved_scheme",
        "inputs": [
          {
            "name": "client",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "sign_scheme",
            "type": "core::felt252"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u32"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "check_sign",
        "inputs": [
          {
            "name": "trader",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "message",
            "type": "core::felt252"
          },
          {
            "name": "signature",
            "type": "core::array::Span::<core::felt252>"
          },
          {
            "name": "sign_scheme",
            "type": "core::felt252"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_signer",
        "inputs": [
          {
            "name": "trader",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_signers",
        "inputs": [
          {
            "name": "traders",
            "type": "core::array::Span::<core::starknet::contract_address::ContractAddress>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<core::starknet::contract_address::ContractAddress>"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_verifier_address",
        "inputs": [
          {
            "name": "sign_scheme",
            "type": "core::felt252"
          }
        ],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "WithdrawableImpl",
    "interface_name": "kurosawa_akira::WithdrawComponent::IWithdraw"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::GasFee",
    "members": [
      {
        "name": "gas_per_action",
        "type": "core::integer::u32"
      },
      {
        "name": "fee_token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "max_gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "conversion_rate",
        "type": "(core::integer::u256, core::integer::u256)"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::WithdrawComponent::Withdraw",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      },
      {
        "name": "receiver",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay",
    "members": [
      {
        "name": "block",
        "type": "core::integer::u64"
      },
      {
        "name": "ts",
        "type": "core::integer::u64"
      }
    ]
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::WithdrawComponent::IWithdraw",
    "items": [
      {
        "type": "function",
        "name": "request_onchain_withdraw",
        "inputs": [
          {
            "name": "withdraw",
            "type": "kurosawa_akira::WithdrawComponent::Withdraw"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "get_pending_withdraw",
        "inputs": [
          {
            "name": "maker",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "(kurosawa_akira::utils::SlowModeLogic::SlowModeDelay, kurosawa_akira::WithdrawComponent::Withdraw)"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_pending_withdraws",
        "inputs": [
          {
            "name": "reqs",
            "type": "core::array::Array::<(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<(kurosawa_akira::utils::SlowModeLogic::SlowModeDelay, kurosawa_akira::WithdrawComponent::Withdraw)>"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "apply_onchain_withdraw",
        "inputs": [
          {
            "name": "token",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "key",
            "type": "core::felt252"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "get_withdraw_steps",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u32"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_request_completed",
        "inputs": [
          {
            "name": "w_hash",
            "type": "core::felt252"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_requests_completed",
        "inputs": [
          {
            "name": "reqs",
            "type": "core::array::Array::<core::felt252>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<core::bool>"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "NonceableImpl",
    "interface_name": "kurosawa_akira::NonceComponent::INonceLogic"
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::NonceComponent::INonceLogic",
    "items": [
      {
        "type": "function",
        "name": "get_nonce",
        "inputs": [
          {
            "name": "maker",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u32"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_nonces",
        "inputs": [
          {
            "name": "makers",
            "type": "core::array::Span::<core::starknet::contract_address::ContractAddress>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<core::integer::u32>"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "AccsesorableImpl",
    "interface_name": "kurosawa_akira::AccessorComponent::IAccesorableImpl"
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::AccessorComponent::IAccesorableImpl",
    "items": [
      {
        "type": "function",
        "name": "get_epochs",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "(core::integer::u32, core::integer::u32)"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_owner",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_approved_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "set_owner",
        "inputs": [
          {
            "name": "new_owner",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "update_executor",
        "inputs": [
          {
            "name": "new_executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "wlist",
            "type": "core::bool"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "grant_access_to_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "invalidate_executors",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      }
    ]
  },
  {
    "type": "constructor",
    "name": "constructor",
    "inputs": [
      {
        "name": "wrapped_native_token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "fee_recipient",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "max_slow_mode_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      },
      {
        "name": "withdraw_action_cost",
        "type": "core::integer::u32"
      },
      {
        "name": "owner",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "function",
    "name": "get_withdraw_delay_params",
    "inputs": [],
    "outputs": [
      {
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "get_max_delay_params",
    "inputs": [],
    "outputs": [
      {
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "get_withdraw_hash",
    "inputs": [
      {
        "name": "withdraw",
        "type": "kurosawa_akira::WithdrawComponent::Withdraw"
      }
    ],
    "outputs": [
      {
        "type": "core::felt252"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::NonceComponent::IncreaseNonce",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "new_nonce",
        "type": "core::integer::u32"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "function",
    "name": "get_increase_nonce_hash",
    "inputs": [
      {
        "name": "increase_nonce",
        "type": "kurosawa_akira::NonceComponent::IncreaseNonce"
      }
    ],
    "outputs": [
      {
        "type": "core::felt252"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "add_signer_scheme",
    "inputs": [
      {
        "name": "verifier_address",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "transfer",
    "inputs": [
      {
        "name": "from",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "safe_mint",
    "inputs": [
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "safe_burn",
    "inputs": [
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [
      {
        "type": "core::integer::u256"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "rebalance_after_trade",
    "inputs": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "taker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "ticker",
        "type": "(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)"
      },
      {
        "name": "amount_base",
        "type": "core::integer::u256"
      },
      {
        "name": "amount_quote",
        "type": "core::integer::u256"
      },
      {
        "name": "is_maker_seller",
        "type": "core::bool"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "update_withdraw_component_params",
    "inputs": [
      {
        "name": "new_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "update_fee_recipient",
    "inputs": [
      {
        "name": "new_fee_recipient",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "update_base_token",
    "inputs": [
      {
        "name": "new_base_token",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::NonceComponent::SignedIncreaseNonce",
    "members": [
      {
        "name": "increase_nonce",
        "type": "kurosawa_akira::NonceComponent::IncreaseNonce"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_increase_nonce",
    "inputs": [
      {
        "name": "signed_nonce",
        "type": "kurosawa_akira::NonceComponent::SignedIncreaseNonce"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_increase_nonces",
    "inputs": [
      {
        "name": "signed_nonces",
        "type": "core::array::Array::<kurosawa_akira::NonceComponent::SignedIncreaseNonce>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::WithdrawComponent::SignedWithdraw",
    "members": [
      {
        "name": "withdraw",
        "type": "kurosawa_akira::WithdrawComponent::Withdraw"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_withdraw",
    "inputs": [
      {
        "name": "signed_withdraw",
        "type": "kurosawa_akira::WithdrawComponent::SignedWithdraw"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_withdraws",
    "inputs": [
      {
        "name": "signed_withdraws",
        "type": "core::array::Array::<kurosawa_akira::WithdrawComponent::SignedWithdraw>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "event",
    "name": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Mint",
    "kind": "struct",
    "members": [
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Transfer",
    "kind": "struct",
    "members": [
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "from_",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Burn",
    "kind": "struct",
    "members": [
      {
        "name": "from_",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "Mint",
        "type": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Mint",
        "kind": "nested"
      },
      {
        "name": "Transfer",
        "type": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Transfer",
        "kind": "nested"
      },
      {
        "name": "Burn",
        "type": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Burn",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::DepositComponent::deposit_component::Deposit",
    "kind": "struct",
    "members": [
      {
        "name": "receiver",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "funder",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::DepositComponent::deposit_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "Deposit",
        "type": "kurosawa_akira::DepositComponent::deposit_component::Deposit",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::SignerComponent::signer_logic_component::NewBinding",
    "kind": "struct",
    "members": [
      {
        "name": "trading_account",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "signer",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::SignerComponent::signer_logic_component::NewSignScheme",
    "kind": "struct",
    "members": [
      {
        "name": "verifier_address",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::SignerComponent::signer_logic_component::ApprovalSignScheme",
    "kind": "struct",
    "members": [
      {
        "name": "trading_account",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252",
        "kind": "key"
      },
      {
        "name": "expire_at",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::SignerComponent::signer_logic_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "NewBinding",
        "type": "kurosawa_akira::SignerComponent::signer_logic_component::NewBinding",
        "kind": "nested"
      },
      {
        "name": "NewSignScheme",
        "type": "kurosawa_akira::SignerComponent::signer_logic_component::NewSignScheme",
        "kind": "nested"
      },
      {
        "name": "ApprovalSignScheme",
        "type": "kurosawa_akira::SignerComponent::signer_logic_component::ApprovalSignScheme",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::WithdrawComponent::withdraw_component::ReqOnChainWithdraw",
    "kind": "struct",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "withdraw",
        "type": "kurosawa_akira::WithdrawComponent::Withdraw",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::WithdrawComponent::withdraw_component::Withdrawal",
    "kind": "struct",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "receiver",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "salt",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee",
        "kind": "data"
      },
      {
        "name": "direct",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::WithdrawComponent::withdraw_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "ReqOnChainWithdraw",
        "type": "kurosawa_akira::WithdrawComponent::withdraw_component::ReqOnChainWithdraw",
        "kind": "nested"
      },
      {
        "name": "Withdrawal",
        "type": "kurosawa_akira::WithdrawComponent::withdraw_component::Withdrawal",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_owner",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "new_epoch",
        "type": "core::integer::u32",
        "kind": "data"
      },
      {
        "name": "wlisted",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
    "kind": "struct",
    "members": [
      {
        "name": "executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "user",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
    "kind": "struct",
    "members": [
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "OwnerChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
        "kind": "nested"
      },
      {
        "name": "ExecutorChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
        "kind": "nested"
      },
      {
        "name": "ApprovalGranted",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
        "kind": "nested"
      },
      {
        "name": "GlobalEpoch",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::NonceComponent::nonce_component::NonceIncrease",
    "kind": "struct",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "new_nonce",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::NonceComponent::nonce_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "NonceIncrease",
        "type": "kurosawa_akira::NonceComponent::nonce_component::NonceIncrease",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::BaseTokenUpdate",
    "kind": "struct",
    "members": [
      {
        "name": "new_base_token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::FeeRecipientUpdate",
    "kind": "struct",
    "members": [
      {
        "name": "new_fee_recipient",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::WithdrawComponentUpdate",
    "kind": "struct",
    "members": [
      {
        "name": "new_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "BalancerEvent",
        "type": "kurosawa_akira::ExchangeBalanceComponent::exchange_balance_logic_component::Event",
        "kind": "nested"
      },
      {
        "name": "DepositEvent",
        "type": "kurosawa_akira::DepositComponent::deposit_component::Event",
        "kind": "nested"
      },
      {
        "name": "SignerEvent",
        "type": "kurosawa_akira::SignerComponent::signer_logic_component::Event",
        "kind": "nested"
      },
      {
        "name": "WithdrawEvent",
        "type": "kurosawa_akira::WithdrawComponent::withdraw_component::Event",
        "kind": "nested"
      },
      {
        "name": "AccessorEvent",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
        "kind": "nested"
      },
      {
        "name": "NonceEvent",
        "type": "kurosawa_akira::NonceComponent::nonce_component::Event",
        "kind": "nested"
      },
      {
        "name": "BaseTokenUpdate",
        "type": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::BaseTokenUpdate",
        "kind": "nested"
      },
      {
        "name": "FeeRecipientUpdate",
        "type": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::FeeRecipientUpdate",
        "kind": "nested"
      },
      {
        "name": "WithdrawComponentUpdate",
        "type": "kurosawa_akira::LayerAkiraCore::LayerAkiraCore::WithdrawComponentUpdate",
        "kind": "nested"
      }
    ]
  }
]

router_abi = [
  {
    "type": "impl",
    "name": "RoutableImpl",
    "interface_name": "kurosawa_akira::RouterComponent::IRouter"
  },
  {
    "type": "struct",
    "name": "core::integer::u256",
    "members": [
      {
        "name": "low",
        "type": "core::integer::u128"
      },
      {
        "name": "high",
        "type": "core::integer::u128"
      }
    ]
  },
  {
    "type": "enum",
    "name": "core::bool",
    "variants": [
      {
        "name": "False",
        "type": "()"
      },
      {
        "name": "True",
        "type": "()"
      }
    ]
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::RouterComponent::IRouter",
    "items": [
      {
        "type": "function",
        "name": "get_base_token",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "router_deposit",
        "inputs": [
          {
            "name": "router",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "coin",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "router_withdraw",
        "inputs": [
          {
            "name": "coin",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          },
          {
            "name": "receiver",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "register_router",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "add_router_binding",
        "inputs": [
          {
            "name": "signer",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "request_onchain_deregister",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "apply_onchain_deregister",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "validate_router",
        "inputs": [
          {
            "name": "message",
            "type": "core::felt252"
          },
          {
            "name": "signature",
            "type": "(core::felt252, core::felt252)"
          },
          {
            "name": "signer",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "router",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_punishment_factor_bips",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u16"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_registered",
        "inputs": [
          {
            "name": "router",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "have_sufficient_amount_to_route",
        "inputs": [
          {
            "name": "router",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "balance_of_router",
        "inputs": [
          {
            "name": "router",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "coin",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_router",
        "inputs": [
          {
            "name": "signer",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_route_amount",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "AccsesorableImpl",
    "interface_name": "kurosawa_akira::AccessorComponent::IAccesorableImpl"
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::AccessorComponent::IAccesorableImpl",
    "items": [
      {
        "type": "function",
        "name": "get_epochs",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "(core::integer::u32, core::integer::u32)"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_owner",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_approved_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "set_owner",
        "inputs": [
          {
            "name": "new_owner",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "update_executor",
        "inputs": [
          {
            "name": "new_executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "wlist",
            "type": "core::bool"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "grant_access_to_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "invalidate_executors",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay",
    "members": [
      {
        "name": "block",
        "type": "core::integer::u64"
      },
      {
        "name": "ts",
        "type": "core::integer::u64"
      }
    ]
  },
  {
    "type": "constructor",
    "name": "constructor",
    "inputs": [
      {
        "name": "max_slow_mode_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      },
      {
        "name": "min_to_route",
        "type": "core::integer::u256"
      },
      {
        "name": "owner",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "core_address",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "function",
    "name": "update_router_component_params",
    "inputs": [
      {
        "name": "new_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay"
      },
      {
        "name": "min_amount_to_route",
        "type": "core::integer::u256"
      },
      {
        "name": "new_punishment_bips",
        "type": "core::integer::u16"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "transfer_to_core",
    "inputs": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      }
    ],
    "outputs": [
      {
        "type": "core::integer::u256"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::Deposit",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "funder",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::Withdraw",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "receiver",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::RouterRegistration",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "status",
        "type": "core::integer::u8",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::Binding",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "signer",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "is_added",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::RouterMint",
    "kind": "struct",
    "members": [
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::RouterBurn",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::RouterComponent::router_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "Deposit",
        "type": "kurosawa_akira::RouterComponent::router_component::Deposit",
        "kind": "nested"
      },
      {
        "name": "Withdraw",
        "type": "kurosawa_akira::RouterComponent::router_component::Withdraw",
        "kind": "nested"
      },
      {
        "name": "RouterRegistration",
        "type": "kurosawa_akira::RouterComponent::router_component::RouterRegistration",
        "kind": "nested"
      },
      {
        "name": "Binding",
        "type": "kurosawa_akira::RouterComponent::router_component::Binding",
        "kind": "nested"
      },
      {
        "name": "RouterMint",
        "type": "kurosawa_akira::RouterComponent::router_component::RouterMint",
        "kind": "nested"
      },
      {
        "name": "RouterBurn",
        "type": "kurosawa_akira::RouterComponent::router_component::RouterBurn",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraExternalGrantor::LayerAkiraExternalGrantor::RouterComponentUpdate",
    "kind": "struct",
    "members": [
      {
        "name": "new_delay",
        "type": "kurosawa_akira::utils::SlowModeLogic::SlowModeDelay",
        "kind": "data"
      },
      {
        "name": "min_amount_to_route",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "new_punishment_bips",
        "type": "core::integer::u16",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_owner",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "new_epoch",
        "type": "core::integer::u32",
        "kind": "data"
      },
      {
        "name": "wlisted",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
    "kind": "struct",
    "members": [
      {
        "name": "executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "user",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
    "kind": "struct",
    "members": [
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "OwnerChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
        "kind": "nested"
      },
      {
        "name": "ExecutorChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
        "kind": "nested"
      },
      {
        "name": "ApprovalGranted",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
        "kind": "nested"
      },
      {
        "name": "GlobalEpoch",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraExternalGrantor::LayerAkiraExternalGrantor::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "RouterEvent",
        "type": "kurosawa_akira::RouterComponent::router_component::Event",
        "kind": "nested"
      },
      {
        "name": "RouterComponentUpdate",
        "type": "kurosawa_akira::LayerAkiraExternalGrantor::LayerAkiraExternalGrantor::RouterComponentUpdate",
        "kind": "nested"
      },
      {
        "name": "AccessorEvent",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
        "kind": "nested"
      }
    ]
  }
]

executor_abi = [
  {
    "type": "impl",
    "name": "BaseOrderTradableImpl",
    "interface_name": "kurosawa_akira::BaseTradeComponent::IBaseOrderTradeLogic"
  },
  {
    "type": "struct",
    "name": "core::integer::u256",
    "members": [
      {
        "name": "low",
        "type": "core::integer::u128"
      },
      {
        "name": "high",
        "type": "core::integer::u128"
      }
    ]
  },
  {
    "type": "enum",
    "name": "core::bool",
    "variants": [
      {
        "name": "False",
        "type": "()"
      },
      {
        "name": "True",
        "type": "()"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::OrderTradeInfo",
    "members": [
      {
        "name": "filled_base_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "filled_quote_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "last_traded_px",
        "type": "core::integer::u256"
      },
      {
        "name": "num_trades_happened",
        "type": "core::integer::u16"
      },
      {
        "name": "as_taker_completed",
        "type": "core::bool"
      },
      {
        "name": "is_sell_side",
        "type": "core::bool"
      }
    ]
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::BaseTradeComponent::IBaseOrderTradeLogic",
    "items": [
      {
        "type": "function",
        "name": "get_order_info",
        "inputs": [
          {
            "name": "order_hash",
            "type": "core::felt252"
          }
        ],
        "outputs": [
          {
            "type": "kurosawa_akira::Order::OrderTradeInfo"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_orders_info",
        "inputs": [
          {
            "name": "order_hashes",
            "type": "core::array::Array::<core::felt252>"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<kurosawa_akira::Order::OrderTradeInfo>"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "impl",
    "name": "AccsesorableImpl",
    "interface_name": "kurosawa_akira::AccessorComponent::IAccesorableImpl"
  },
  {
    "type": "interface",
    "name": "kurosawa_akira::AccessorComponent::IAccesorableImpl",
    "items": [
      {
        "type": "function",
        "name": "get_epochs",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "(core::integer::u32, core::integer::u32)"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_owner",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "is_approved_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "user",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::bool"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "set_owner",
        "inputs": [
          {
            "name": "new_owner",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "update_executor",
        "inputs": [
          {
            "name": "new_executor",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "wlist",
            "type": "core::bool"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "grant_access_to_executor",
        "inputs": [
          {
            "name": "executor",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "invalidate_executors",
        "inputs": [],
        "outputs": [],
        "state_mutability": "external"
      }
    ]
  },
  {
    "type": "constructor",
    "name": "constructor",
    "inputs": [
      {
        "name": "core_address",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "router_address",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "owner",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "function",
    "name": "get_core",
    "inputs": [],
    "outputs": [
      {
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "get_router",
    "inputs": [],
    "outputs": [
      {
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "is_wlsted_invoker",
    "inputs": [
      {
        "name": "caller",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ],
    "outputs": [
      {
        "type": "core::bool"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "function",
    "name": "update_exchange_invokers",
    "inputs": [
      {
        "name": "invoker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "enabled",
        "type": "core::bool"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Quantity",
    "members": [
      {
        "name": "base_qty",
        "type": "core::integer::u256"
      },
      {
        "name": "quote_qty",
        "type": "core::integer::u256"
      },
      {
        "name": "base_asset",
        "type": "core::integer::u256"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::FixedFee",
    "members": [
      {
        "name": "recipient",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "maker_pbips",
        "type": "core::integer::u32"
      },
      {
        "name": "taker_pbips",
        "type": "core::integer::u32"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::GasFee",
    "members": [
      {
        "name": "gas_per_action",
        "type": "core::integer::u32"
      },
      {
        "name": "fee_token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "max_gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "conversion_rate",
        "type": "(core::integer::u256, core::integer::u256)"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::OrderFee",
    "members": [
      {
        "name": "trade_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "router_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "integrator_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "apply_to_receipt_amount",
        "type": "core::bool"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      }
    ]
  },
  {
    "type": "enum",
    "name": "kurosawa_akira::Order::TakerSelfTradePreventionMode",
    "variants": [
      {
        "name": "NONE",
        "type": "()"
      },
      {
        "name": "EXPIRE_TAKER",
        "type": "()"
      },
      {
        "name": "EXPIRE_MAKER",
        "type": "()"
      },
      {
        "name": "EXPIRE_BOTH",
        "type": "()"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Constraints",
    "members": [
      {
        "name": "number_of_swaps_allowed",
        "type": "core::integer::u16"
      },
      {
        "name": "duration_valid",
        "type": "core::integer::u32"
      },
      {
        "name": "created_at",
        "type": "core::integer::u32"
      },
      {
        "name": "stp",
        "type": "kurosawa_akira::Order::TakerSelfTradePreventionMode"
      },
      {
        "name": "nonce",
        "type": "core::integer::u32"
      },
      {
        "name": "min_receive_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "router_signer",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::OrderFlags",
    "members": [
      {
        "name": "full_fill_only",
        "type": "core::bool"
      },
      {
        "name": "best_level_only",
        "type": "core::bool"
      },
      {
        "name": "post_only",
        "type": "core::bool"
      },
      {
        "name": "is_sell_side",
        "type": "core::bool"
      },
      {
        "name": "is_market_order",
        "type": "core::bool"
      },
      {
        "name": "to_ecosystem_book",
        "type": "core::bool"
      },
      {
        "name": "external_funds",
        "type": "core::bool"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Order",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "price",
        "type": "core::integer::u256"
      },
      {
        "name": "qty",
        "type": "kurosawa_akira::Order::Quantity"
      },
      {
        "name": "ticker",
        "type": "(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)"
      },
      {
        "name": "fee",
        "type": "kurosawa_akira::Order::OrderFee"
      },
      {
        "name": "constraints",
        "type": "kurosawa_akira::Order::Constraints"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "flags",
        "type": "kurosawa_akira::Order::OrderFlags"
      },
      {
        "name": "source",
        "type": "core::felt252"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "function",
    "name": "get_order_hash",
    "inputs": [
      {
        "name": "order",
        "type": "kurosawa_akira::Order::Order"
      }
    ],
    "outputs": [
      {
        "type": "core::felt252"
      }
    ],
    "state_mutability": "view"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::NonceComponent::IncreaseNonce",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "new_nonce",
        "type": "core::integer::u32"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "struct",
    "name": "core::array::Span::<core::felt252>",
    "members": [
      {
        "name": "snapshot",
        "type": "@core::array::Array::<core::felt252>"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::NonceComponent::SignedIncreaseNonce",
    "members": [
      {
        "name": "increase_nonce",
        "type": "kurosawa_akira::NonceComponent::IncreaseNonce"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_increase_nonce",
    "inputs": [
      {
        "name": "signed_nonce",
        "type": "kurosawa_akira::NonceComponent::SignedIncreaseNonce"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_increase_nonces",
    "inputs": [
      {
        "name": "signed_nonces",
        "type": "core::array::Array::<kurosawa_akira::NonceComponent::SignedIncreaseNonce>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::WithdrawComponent::Withdraw",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "amount",
        "type": "core::integer::u256"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      },
      {
        "name": "receiver",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::WithdrawComponent::SignedWithdraw",
    "members": [
      {
        "name": "withdraw",
        "type": "kurosawa_akira::WithdrawComponent::Withdraw"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_withdraw",
    "inputs": [
      {
        "name": "signed_withdraw",
        "type": "kurosawa_akira::WithdrawComponent::SignedWithdraw"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_withdraws",
    "inputs": [
      {
        "name": "signed_withdraws",
        "type": "core::array::Array::<kurosawa_akira::WithdrawComponent::SignedWithdraw>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::SignedOrder",
    "members": [
      {
        "name": "order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      },
      {
        "name": "router_sign",
        "type": "(core::felt252, core::felt252)"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_ecosystem_trades",
    "inputs": [
      {
        "name": "taker_orders",
        "type": "core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::bool)>"
      },
      {
        "name": "maker_orders",
        "type": "core::array::Array::<kurosawa_akira::Order::SignedOrder>"
      },
      {
        "name": "iters",
        "type": "core::array::Array::<(core::integer::u16, core::bool)>"
      },
      {
        "name": "oracle_settled_qty",
        "type": "core::array::Array::<core::integer::u256>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_single_execution_step",
    "inputs": [
      {
        "name": "taker_order",
        "type": "kurosawa_akira::Order::SignedOrder"
      },
      {
        "name": "maker_orders",
        "type": "core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "total_amount_matched",
        "type": "core::integer::u256"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      },
      {
        "name": "as_taker_completed",
        "type": "core::bool"
      }
    ],
    "outputs": [
      {
        "type": "core::bool"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_execution_steps",
    "inputs": [
      {
        "name": "bulk",
        "type": "core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>, core::integer::u256, core::bool)>"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ],
    "outputs": [
      {
        "type": "core::array::Array::<core::bool>"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "core::array::Span::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>",
    "members": [
      {
        "name": "snapshot",
        "type": "@core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_single_taker",
    "inputs": [
      {
        "name": "signed_taker_order",
        "type": "kurosawa_akira::Order::SignedOrder"
      },
      {
        "name": "signed_maker_orders",
        "type": "core::array::Span::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "total_amount_matched",
        "type": "core::integer::u256"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      },
      {
        "name": "as_taker_completed",
        "type": "core::bool"
      },
      {
        "name": "skip_taker_validation",
        "type": "core::bool"
      },
      {
        "name": "gas_trades_to_pay",
        "type": "core::integer::u16"
      },
      {
        "name": "transfer_taker_recieve_back",
        "type": "core::bool"
      },
      {
        "name": "allow_charge_gas_on_receipt",
        "type": "core::bool"
      }
    ],
    "outputs": [
      {
        "type": "(core::bool, core::felt252)"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_trades",
    "inputs": [
      {
        "name": "taker_order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "signed_maker_orders",
        "type": "core::array::Span::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "taker_hash",
        "type": "core::felt252"
      },
      {
        "name": "as_taker_completed",
        "type": "core::bool"
      }
    ],
    "outputs": [
      {
        "type": "(core::integer::u256, core::integer::u256)"
      }
    ],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::GasContext",
    "members": [
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "cur_gas_per_action",
        "type": "core::integer::u32"
      }
    ]
  },
  {
    "type": "function",
    "name": "finalize_router_taker",
    "inputs": [
      {
        "name": "taker_order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "taker_hash",
        "type": "core::felt252"
      },
      {
        "name": "received_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "unspent_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "trades",
        "type": "core::integer::u16"
      },
      {
        "name": "spent_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "transfer_back_received",
        "type": "core::bool"
      },
      {
        "name": "tfer_back_unspent",
        "type": "core::bool"
      },
      {
        "name": "gas_ctx",
        "type": "kurosawa_akira::Fees::GasContext"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "apply_punishment",
    "inputs": [
      {
        "name": "taker_order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "signed_maker_orders",
        "type": "core::array::Span::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "taker_hash",
        "type": "core::felt252"
      },
      {
        "name": "as_taker_completed",
        "type": "core::bool"
      },
      {
        "name": "gas_ctx",
        "type": "kurosawa_akira::Fees::GasContext"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "enum",
    "name": "kurosawa_akira::LayerAkiraBaseExecutor::LayerAkiraBaseExecutor::Step",
    "variants": [
      {
        "name": "BulkExecutionSteps",
        "type": "(core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>, core::integer::u256, core::bool)>, core::bool)"
      },
      {
        "name": "SingleExecutionStep",
        "type": "((kurosawa_akira::Order::SignedOrder, core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>, core::integer::u256, core::bool), core::bool)"
      },
      {
        "name": "EcosystemTrades",
        "type": "(core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::bool)>, core::array::Array::<kurosawa_akira::Order::SignedOrder>, core::array::Array::<(core::integer::u16, core::bool)>, core::array::Array::<core::integer::u256>)"
      },
      {
        "name": "IncreaseNonceStep",
        "type": "kurosawa_akira::NonceComponent::SignedIncreaseNonce"
      },
      {
        "name": "WithdrawStep",
        "type": "kurosawa_akira::WithdrawComponent::SignedWithdraw"
      }
    ]
  },
  {
    "type": "function",
    "name": "apply_steps",
    "inputs": [
      {
        "name": "steps",
        "type": "core::array::Array::<kurosawa_akira::LayerAkiraBaseExecutor::LayerAkiraBaseExecutor::Step>"
      },
      {
        "name": "nonce_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "withdraw_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "router_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "ecosystem_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "event",
    "name": "kurosawa_akira::BaseTradeComponent::base_trade_component::FeeReward",
    "kind": "struct",
    "members": [
      {
        "name": "recipient",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "token",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::BaseTradeComponent::base_trade_component::Punish",
    "kind": "struct",
    "members": [
      {
        "name": "router",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "taker_hash",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "maker_hash",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::BaseTradeComponent::base_trade_component::Trade",
    "kind": "struct",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "taker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "ticker",
        "type": "(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)",
        "kind": "data"
      },
      {
        "name": "router_maker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "router_taker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount_base",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "amount_quote",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "is_sell_side",
        "type": "core::bool",
        "kind": "data"
      },
      {
        "name": "is_failed",
        "type": "core::bool",
        "kind": "data"
      },
      {
        "name": "is_ecosystem_book",
        "type": "core::bool",
        "kind": "data"
      },
      {
        "name": "maker_hash",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "taker_hash",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "maker_source",
        "type": "core::felt252",
        "kind": "data"
      },
      {
        "name": "taker_source",
        "type": "core::felt252",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::BaseTradeComponent::base_trade_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "FeeReward",
        "type": "kurosawa_akira::BaseTradeComponent::base_trade_component::FeeReward",
        "kind": "nested"
      },
      {
        "name": "Punish",
        "type": "kurosawa_akira::BaseTradeComponent::base_trade_component::Punish",
        "kind": "nested"
      },
      {
        "name": "Trade",
        "type": "kurosawa_akira::BaseTradeComponent::base_trade_component::Trade",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraBaseExecutor::LayerAkiraBaseExecutor::UpdateExchangeInvoker",
    "kind": "struct",
    "members": [
      {
        "name": "invoker",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "enabled",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_owner",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
    "kind": "struct",
    "members": [
      {
        "name": "new_executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "new_epoch",
        "type": "core::integer::u32",
        "kind": "data"
      },
      {
        "name": "wlisted",
        "type": "core::bool",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
    "kind": "struct",
    "members": [
      {
        "name": "executor",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "user",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
    "kind": "struct",
    "members": [
      {
        "name": "epoch",
        "type": "core::integer::u32",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "OwnerChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::OwnerChanged",
        "kind": "nested"
      },
      {
        "name": "ExecutorChanged",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ExecutorChanged",
        "kind": "nested"
      },
      {
        "name": "ApprovalGranted",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::ApprovalGranted",
        "kind": "nested"
      },
      {
        "name": "GlobalEpoch",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::GlobalEpoch",
        "kind": "nested"
      }
    ]
  },
  {
    "type": "event",
    "name": "kurosawa_akira::LayerAkiraBaseExecutor::LayerAkiraBaseExecutor::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "BaseTradeEvent",
        "type": "kurosawa_akira::BaseTradeComponent::base_trade_component::Event",
        "kind": "nested"
      },
      {
        "name": "UpdateExchangeInvoker",
        "type": "kurosawa_akira::LayerAkiraBaseExecutor::LayerAkiraBaseExecutor::UpdateExchangeInvoker",
        "kind": "nested"
      },
      {
        "name": "AccessorEvent",
        "type": "kurosawa_akira::AccessorComponent::accessor_logic_component::Event",
        "kind": "nested"
      }
    ]
  }
]


snip9_abi = [
  {
    "type": "constructor",
    "name": "constructor",
    "inputs": [
      {
        "name": "base_executor_address",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "struct",
    "name": "core::integer::u256",
    "members": [
      {
        "name": "low",
        "type": "core::integer::u128"
      },
      {
        "name": "high",
        "type": "core::integer::u128"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Quantity",
    "members": [
      {
        "name": "base_qty",
        "type": "core::integer::u256"
      },
      {
        "name": "quote_qty",
        "type": "core::integer::u256"
      },
      {
        "name": "base_asset",
        "type": "core::integer::u256"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::FixedFee",
    "members": [
      {
        "name": "recipient",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "maker_pbips",
        "type": "core::integer::u32"
      },
      {
        "name": "taker_pbips",
        "type": "core::integer::u32"
      }
    ]
  },
  {
    "type": "enum",
    "name": "core::bool",
    "variants": [
      {
        "name": "False",
        "type": "()"
      },
      {
        "name": "True",
        "type": "()"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Fees::GasFee",
    "members": [
      {
        "name": "gas_per_action",
        "type": "core::integer::u32"
      },
      {
        "name": "fee_token",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "max_gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "conversion_rate",
        "type": "(core::integer::u256, core::integer::u256)"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::OrderFee",
    "members": [
      {
        "name": "trade_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "router_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "integrator_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "apply_to_receipt_amount",
        "type": "core::bool"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      }
    ]
  },
  {
    "type": "enum",
    "name": "kurosawa_akira::Order::TakerSelfTradePreventionMode",
    "variants": [
      {
        "name": "NONE",
        "type": "()"
      },
      {
        "name": "EXPIRE_TAKER",
        "type": "()"
      },
      {
        "name": "EXPIRE_MAKER",
        "type": "()"
      },
      {
        "name": "EXPIRE_BOTH",
        "type": "()"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Constraints",
    "members": [
      {
        "name": "number_of_swaps_allowed",
        "type": "core::integer::u16"
      },
      {
        "name": "duration_valid",
        "type": "core::integer::u32"
      },
      {
        "name": "created_at",
        "type": "core::integer::u32"
      },
      {
        "name": "stp",
        "type": "kurosawa_akira::Order::TakerSelfTradePreventionMode"
      },
      {
        "name": "nonce",
        "type": "core::integer::u32"
      },
      {
        "name": "min_receive_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "router_signer",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::OrderFlags",
    "members": [
      {
        "name": "full_fill_only",
        "type": "core::bool"
      },
      {
        "name": "best_level_only",
        "type": "core::bool"
      },
      {
        "name": "post_only",
        "type": "core::bool"
      },
      {
        "name": "is_sell_side",
        "type": "core::bool"
      },
      {
        "name": "is_market_order",
        "type": "core::bool"
      },
      {
        "name": "to_ecosystem_book",
        "type": "core::bool"
      },
      {
        "name": "external_funds",
        "type": "core::bool"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::Order",
    "members": [
      {
        "name": "maker",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "price",
        "type": "core::integer::u256"
      },
      {
        "name": "qty",
        "type": "kurosawa_akira::Order::Quantity"
      },
      {
        "name": "ticker",
        "type": "(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)"
      },
      {
        "name": "fee",
        "type": "kurosawa_akira::Order::OrderFee"
      },
      {
        "name": "constraints",
        "type": "kurosawa_akira::Order::Constraints"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "flags",
        "type": "kurosawa_akira::Order::OrderFlags"
      },
      {
        "name": "source",
        "type": "core::felt252"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      }
    ]
  },
  {
    "type": "function",
    "name": "placeTakerOrder",
    "inputs": [
      {
        "name": "order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "router_sign",
        "type": "(core::felt252, core::felt252)"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "core::array::Span::<core::felt252>",
    "members": [
      {
        "name": "snapshot",
        "type": "@core::array::Array::<core::felt252>"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::SignedOrder",
    "members": [
      {
        "name": "order",
        "type": "kurosawa_akira::Order::Order"
      },
      {
        "name": "sign",
        "type": "core::array::Span::<core::felt252>"
      },
      {
        "name": "router_sign",
        "type": "(core::felt252, core::felt252)"
      }
    ]
  },
  {
    "type": "function",
    "name": "fullfillTakerOrder",
    "inputs": [
      {
        "name": "maker_orders",
        "type": "core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "total_amount_matched",
        "type": "core::integer::u256"
      },
      {
        "name": "gas_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::Order::SimpleOrder",
    "members": [
      {
        "name": "price",
        "type": "core::integer::u256"
      },
      {
        "name": "base_asset",
        "type": "core::integer::u256"
      },
      {
        "name": "ticker",
        "type": "(core::starknet::contract_address::ContractAddress, core::starknet::contract_address::ContractAddress)"
      },
      {
        "name": "is_sell_side",
        "type": "core::bool"
      }
    ]
  },
  {
    "type": "struct",
    "name": "kurosawa_akira::SORLayerAkiraExecutor::SORDetails",
    "members": [
      {
        "name": "lead_qty",
        "type": "kurosawa_akira::Order::Quantity"
      },
      {
        "name": "last_qty",
        "type": "kurosawa_akira::Order::Quantity"
      },
      {
        "name": "trade_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "router_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "integrator_fee",
        "type": "kurosawa_akira::Fees::FixedFee"
      },
      {
        "name": "apply_to_receipt_amount",
        "type": "core::bool"
      },
      {
        "name": "gas_fee",
        "type": "kurosawa_akira::Fees::GasFee"
      },
      {
        "name": "created_at",
        "type": "core::integer::u32"
      },
      {
        "name": "source",
        "type": "core::felt252"
      },
      {
        "name": "allow_nonatomic",
        "type": "core::bool"
      },
      {
        "name": "to_ecosystem_book",
        "type": "core::bool"
      },
      {
        "name": "duration_valid",
        "type": "core::integer::u32"
      },
      {
        "name": "nonce",
        "type": "core::integer::u32"
      },
      {
        "name": "external_funds",
        "type": "core::bool"
      },
      {
        "name": "router_signer",
        "type": "core::starknet::contract_address::ContractAddress"
      },
      {
        "name": "salt",
        "type": "core::felt252"
      },
      {
        "name": "sign_scheme",
        "type": "core::felt252"
      },
      {
        "name": "number_of_swaps_allowed",
        "type": "core::integer::u16"
      },
      {
        "name": "min_receive_amount",
        "type": "core::integer::u256"
      },
      {
        "name": "max_spend_amount",
        "type": "core::integer::u256"
      }
    ]
  },
  {
    "type": "function",
    "name": "placeSORTakerOrder",
    "inputs": [
      {
        "name": "orchestrate_order",
        "type": "kurosawa_akira::Order::SimpleOrder"
      },
      {
        "name": "path",
        "type": "core::array::Array::<kurosawa_akira::Order::SimpleOrder>"
      },
      {
        "name": "router_signature",
        "type": "(core::felt252, core::felt252)"
      },
      {
        "name": "details",
        "type": "kurosawa_akira::SORLayerAkiraExecutor::SORDetails"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "function",
    "name": "fulfillSORAtomic",
    "inputs": [
      {
        "name": "makers_orders",
        "type": "core::array::Array::<(kurosawa_akira::Order::SignedOrder, core::integer::u256)>"
      },
      {
        "name": "total_amount_matched_and_len",
        "type": "core::array::Array::<(core::integer::u256, core::integer::u8)>"
      },
      {
        "name": "gas_steps",
        "type": "core::integer::u32"
      },
      {
        "name": "gas_price",
        "type": "core::integer::u256"
      },
      {
        "name": "sor_id",
        "type": "core::felt252"
      }
    ],
    "outputs": [],
    "state_mutability": "external"
  },
  {
    "type": "event",
    "name": "kurosawa_akira::SORLayerAkiraExecutor::SORLayerAkiraExecutor::Event",
    "kind": "enum",
    "variants": []
  }
]