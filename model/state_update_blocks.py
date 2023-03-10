"""# State Update Blocks
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.accounting as accounting
import model.parts.price_processes as price_processes
import model.parts.pcv_management as pcv_management
import model.parts.liquidity_pools as liquidity_pools
import model.parts.pcv_yield as pcv_yield
import model.parts.money_markets as money_markets
import model.parts.system_metrics as system_metrics
import model.parts.fei_savings_deposit as fei_savings_deposit
import model.parts.fei_capital_allocation as fei_capital_allocation
import model.parts.peg_stability_module as peg_stability_module

from model.utils import update_from_signal, update_timestamp


# State Update Block keys for convenience:
enabled = "enabled"
description = "description"
policies = "policies"
variables = "variables"

state_update_blocks = [
    {
        description: """
            Simulation Accounting
        """,
        policies: {},
        variables: {
            "timestamp": update_timestamp,
        },
    },
    {
        description: """
            FEI Accounting
        """,
        policies: {
            "fei_accounting": accounting.policy_fei_accounting,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                "total_protocol_owned_fei",
                "total_user_circulating_fei",
                "total_fei_supply",
            ]
        },
    },
    {
        description: """
            PCV Accounting
        """,
        policies: {
            "pcv_accounting": accounting.policy_pcv_accounting,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                "total_stable_asset_pcv_balance",
                "total_volatile_asset_pcv_balance",
                "total_stable_asset_pcv",
                "total_volatile_asset_pcv",
                "total_pcv",
            ]
        },
    },
    {
        description: """
            System Metrics
        """,
        policies: {
            "system_metrics": system_metrics.policy_system_metrics,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                # PCV System Metrics
                "stable_backing_ratio",
                "stable_pcv_ratio",
                "collateralization_ratio",
                # NOTE: Uncomment Below as part of working exercise in Quiz Notebook 1
                # "reserve_ratio",
                "pcv_yield_rate",
                # Protocol System Metrics
                "protocol_equity",
                "protocol_revenue",
            ]
        },
    },
    # NOTE: Uncomment Below as part of working exercise in Quiz Notebook 1
    # {
    #     description: """
    #         Update Reserve Ratio Toy PSUB
    #     """,
    #     policies: {},
    #     variables: {
    #         "reserve_ratio": reserve_ratio.update_reserve_ratio,
    #     },
    # },
    {
        description: """
            Price Processes
        """,
        policies: {},
        variables: {
            "fei_price": price_processes.update_fei_price,
            "stable_asset_price": price_processes.update_stable_asset_price,
            "volatile_asset_price": price_processes.update_volatile_asset_price,
        },
    },
    {
        description: """
            FEI-X Liquidity Pool
        """,
        policies: {
            "market_maker": liquidity_pools.policy_constant_function_market_maker,
        },
        variables: {
            **{
                key: update_from_signal(key)
                for key in [
                    "liquidity_pool_fei_source_sink",
                    "fei_minted_redeemed",
                    # NOTE Total liquidity pool metrics including both protocol- and user-supplied liquidity
                    "liquidity_pool_tvl",
                    "liquidity_pool_invariant",
                    "liquidity_pool_impermanent_loss",
                    "liquidity_pool_trading_fees",
                    # PCV Deposit and User Deposit updates
                    "fei_liquidity_pool_pcv_deposit",
                    "volatile_liquidity_pool_pcv_deposit",
                    "fei_liquidity_pool_user_deposit",
                    "volatile_liquidity_pool_user_deposit",
                ]
            },
            # **{key: accumulate_from_signal(key) for key in ["liquidity_pool_trading_fees"]},
        },
    },
    {
        enabled: True,
        description: """
            Peg Stability Module Minting / Redemption
        """,
        policies: {"peg_stability_module": peg_stability_module.policy_peg_stability_module},
        variables: {
            key: update_from_signal(key, optional_update=True)
            for key in [
                "psm_mint_redeem_fees",
                # List of all possible PSM PCV Deposits, with one PSM enabled at a time
                "stable_idle_pcv_deposit",
                "volatile_idle_pcv_deposit",
                "volatile_yield_bearing_pcv_deposit",
            ]
        },
    },
    {
        description: """"
            FEI-X Money Market
        """,
        policies: {
            "money_market": money_markets.policy_money_market,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                "fei_money_market_pcv_deposit",
                "fei_money_market_user_deposit",
                "fei_money_market_borrowed",
                "fei_money_market_utilization",
                "fei_money_market_borrow_rate",
                "fei_money_market_supply_rate",
                "volatile_asset_risk_metric",
                "volatile_asset_risk_metric_min",
                "volatile_asset_risk_metric_max",
                "volatile_asset_price_mean",
            ]
        },
    },
    {
        enabled: True,
        description: """
            PCV Yield Accrual
        """,
        policies: {
            "policy_accrue_yield": pcv_yield.policy_yield_accrual,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                "stable_yield_bearing_pcv_deposit",
                "volatile_yield_bearing_pcv_deposit",
                "fei_money_market_pcv_deposit",
                "pcv_yield",
            ]
        },
    },
    {
        enabled: True,
        description: """
            PCV Yield Management - Withdraw Yield Policy
        """,
        policies: {
            # NOTE Only one Policy should be enabled at a time using the relevant System Parameters
            "policy_withdraw_yield": pcv_yield.policy_withdraw_yield,
            "policy_reinvest_yield": pcv_yield.policy_reinvest_yield,
        },
        variables: {
            key: update_from_signal(key, optional_update=True)
            for key in [
                "stable_idle_pcv_deposit",
                "volatile_idle_pcv_deposit",
                "stable_yield_bearing_pcv_deposit",
                "volatile_yield_bearing_pcv_deposit",
            ]
        },
    },
    {
        description: """
            PCV Rebalancing
        """,
        policies: {
            # NOTE Only one Policy should be enabled at a time using the relevant System Parameters
            "target_stable_backing": pcv_management.policy_pcv_rebalancing_target_stable_backing,
            "target_stable_pcv": pcv_management.policy_pcv_rebalancing_target_stable_pcv,
        },
        # NOTE PCV asset value implicitly updated every period even if no rebalancing performed
        variables: {
            key: update_from_signal(key, optional_update=True)
            for key in [
                "stable_idle_pcv_deposit",
                "volatile_idle_pcv_deposit",
                "stable_yield_bearing_pcv_deposit",
                "volatile_yield_bearing_pcv_deposit",
            ]
        },
    },
    {
        description: """
            FEI Savings Deposit
        """,
        policies: {
            "fei_savings_deposit": fei_savings_deposit.policy_fei_savings_deposit,
        },
        variables: {
            **{key: update_from_signal(key) for key in ["fei_savings_rate"]},
            **{
                "fei_savings_user_deposit": fei_savings_deposit.update_fei_savings_deposit_yield_rate
            },
        },
    },
    {
        description: """
            User-circulating FEI Capital Allocation Model Weight Update
        """,
        policies: {
            # Perform weight updates using exogenous dirichlet stochastic process:
            # "capital_allocation_exogenous_weight_update": fei_capital_allocation.policy_fei_capital_allocation_exogenous_weight_update,
            "capital_allocation_endogenous_weight_update": fei_capital_allocation.policy_fei_capital_allocation_endogenous_weight_update,
        },
        variables: {key: update_from_signal(key) for key in ["capital_allocation_target_weights"]},
    },
    {
        description: """
            User-circulating FEI Capital Allocation Model Deposit Rebalancing
        """,
        policies: {
            "capital_allocation_deposit_rebalance": fei_capital_allocation.policy_fei_capital_allocation_rebalancing,
        },
        variables: {
            **{
                key: update_from_signal(key)
                for key in [
                    "capital_allocation_rebalance_matrix",
                    "capital_allocation_rebalance_remainder",
                ]
            },
            **{
                key: update_from_signal(key, optional_update=True)
                for key in [
                    "capital_allocation_rebalance_matrix",
                    "capital_allocation_rebalance_remainder",
                    # FEI User Deposits
                    "fei_money_market_user_deposit",
                    "fei_savings_user_deposit",
                    "fei_idle_user_deposit",
                    # Liquidity Pool updates
                    "liquidity_pool_liquidity_tokens",
                    "liquidity_pool_invariant",
                    "fei_liquidity_pool_user_deposit",
                    "volatile_liquidity_pool_user_deposit",
                ]
            },
        },
    },
]

state_update_blocks = [block for block in state_update_blocks if block.get("enabled", True)]
