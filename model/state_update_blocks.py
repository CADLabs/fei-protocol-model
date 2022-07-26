"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.accounting as accounting
import model.parts.price_processes as price_processes
import model.parts.pcv_management as pcv_management
import model.parts.liquidity_pools as liquidity_pools
import model.parts.pcv_yield as pcv_yield
import model.parts.money_markets as money_markets
import model.parts.system_metrics as system_metrics

from model.utils import update_from_signal, accumulate_from_signal, update_timestamp


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
            "pcv_metrics": system_metrics.policy_pcv_metrics,
        },
        variables: {
            key: update_from_signal(key)
            for key in [
                "stable_backing_ratio",
                "stable_pcv_ratio",
                "collateralization_ratio",
                "protocol_equity",
                "pcv_yield_rate",
            ]
        },
    },
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
            **{key: accumulate_from_signal(key) for key in ["liquidity_pool_trading_fees"]},
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
            ]
        },
    },
    {
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
                # TODO Decide if and where we accrue User Deposit yield
                # "fei_money_market_user_deposit": update_from_signal("fei_money_market_user_deposit"),
                "fei_money_market_pcv_deposit",
                "pcv_yield",
            ]
        },
    },
    {
        description: """
            PCV Yield Management - Withdraw Yield Policy
        """,
        policies: {
            "policy_withdraw_yield": pcv_yield.policy_withdraw_yield,
            # "policy_reinvest_yield": pcv_yield.policy_reinvest_yield,
        },
        variables: {
            key: update_from_signal(key)
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
            # Disable execution of Policy by setting relevant target System Parameter to `None`
            "target_stable_pcv": pcv_management.policy_pcv_rebalancing_target_stable_pcv,
            "target_stable_backing": pcv_management.policy_pcv_rebalancing_target_stable_backing,
        },
        # NOTE PCV asset value implicitly updated every period even if no rebalancing performed
        variables: {
            key: update_from_signal(key)
            for key in [
                "stable_idle_pcv_deposit",
                "volatile_idle_pcv_deposit",
                "stable_yield_bearing_pcv_deposit",
                "volatile_yield_bearing_pcv_deposit",
            ]
        },
    },
]
