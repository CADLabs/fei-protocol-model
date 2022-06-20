"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.accounting as accounting
import model.parts.price_processes as price_processes
import model.parts.pcv_management as pcv_management
import model.parts.liquidity_pools as liquidity_pools
import model.parts.pcv_yield as pcv_yield
import model.parts.money_markets as money_markets

from model.utils import update_from_signal, accumulate_from_signal, update_timestamp


state_update_blocks = [
    {
        "description": """
            Assorted accounting
        """,
        "policies": {
            "accounting": accounting.policy_accounting,
        },
        "variables": {
            "timestamp": update_timestamp,
            "total_protocol_owned_fei": update_from_signal("total_protocol_owned_fei"),
            "total_user_circulating_fei": update_from_signal("total_user_circulating_fei"),
            "total_fei_supply": update_from_signal("total_fei_supply"),
        },
    },
    {
        "description": """
            Price Processes
        """,
        "policies": {},
        "variables": {
            "fei_price": price_processes.update_fei_price,
            "stable_asset_price": price_processes.update_stable_asset_price,
            "volatile_asset_price": price_processes.update_volatile_asset_price,
        },
    },
    {
        "description": """
            FEI-X Liquidity Pool
        """,
        "policies": {
            "cfmm": liquidity_pools.policy_constant_function_market_maker,
        },
        "variables": {
            "liquidity_pool_fei_source_sink": update_from_signal("liquidity_pool_fei_source_sink"),
            "fei_minted_redeemed": update_from_signal("fei_minted_redeemed"),
            "liquidity_pool_tvl": update_from_signal("liquidity_pool_tvl"),
            "volatile_deposit_liquidity_pool": liquidity_pools.update_volatile_deposit_liquidity_pool,
            "fei_deposit_liquidity_pool": liquidity_pools.update_fei_deposit_liquidity_pool,
            "liquidity_pool_invariant": update_from_signal("liquidity_pool_invariant"),
            "liquidity_pool_impermanent_loss": update_from_signal(
                "liquidity_pool_impermanent_loss"
            ),
            "liquidity_pool_trading_fees": accumulate_from_signal("liquidity_pool_trading_fees"),
        },
    },
    {
        "description": """"
            FEI-X Money Market
        """,
        "policies": {
            "money_market": money_markets.policy_money_market,
        },
        "variables": {
            "fei_deposit_money_market": update_from_signal("fei_deposit_money_market"),
            "fei_money_market_borrowed": update_from_signal("fei_money_market_borrowed"),
            "fei_money_market_utilization": update_from_signal("fei_money_market_utilization"),
            "fei_money_market_borrow_rate": update_from_signal("fei_money_market_borrow_rate"),
            "fei_money_market_supply_rate": update_from_signal("fei_money_market_supply_rate"),
        },
    },
    {
        "description": """
            PCV Yield Accrual
        """,
        "policies": {
            "policy_accrue_yield": pcv_yield.policy_yield_accrual,
        },
        "variables": {
            "stable_deposit_yield_bearing": update_from_signal("stable_deposit_yield_bearing"),
            "volatile_deposit_yield_bearing": update_from_signal("volatile_deposit_yield_bearing"),
        },
    },
    {
        "description": """
            PCV Yield Management - Withdraw Yield Policy
        """,
        "policies": {
            "policy_withdraw_yield": pcv_yield.policy_withdraw_yield,
        },
        "variables": {
            "stable_deposit_idle": update_from_signal("stable_deposit_idle"),
            "volatile_deposit_idle": update_from_signal("volatile_deposit_idle"),
            "stable_deposit_yield_bearing": update_from_signal("stable_deposit_yield_bearing"),
            "volatile_deposit_yield_bearing": update_from_signal("volatile_deposit_yield_bearing"),
        },
    },
    # TODO Set up state update block initialization
    # {
    #     "description": """
    #         PCV Yield Management - Reinvest Yield Policy
    #         Toggle between Withdraw Yield Policy and Reinvest Yield Policy
    #         using yield_withdrawal_period and yield_reinvest_period parameters.
    #     """,
    #     "include_if": ["yield_reinvest_period"],
    #     "policies": {
    #         "policy_reinvest_yield": pcv_yield.policy_reinvest_yield,
    #     },
    #     "variables": {
    #         "stable_deposit_yield_bearing": update_from_signal("stable_deposit_yield_bearing"),
    #         "volatile_deposit_yield_bearing": update_from_signal("volatile_deposit_yield_bearing"),
    #     },
    # },
    {
        "description": """
            PCV Rebalancing
        """,
        "policies": {
            "pcv_rebalancing": pcv_management.policy_pcv_rebalancing_target_stable_backing,
        },
        "variables": {
            # NOTE PCV asset value implicitly updated every period even if no rebalancing performed
            "stable_deposit_idle": update_from_signal("stable_deposit_idle"),
            "volatile_deposit_idle": update_from_signal("volatile_deposit_idle"),
            "stable_deposit_yield_bearing": update_from_signal("stable_deposit_yield_bearing"),
            "volatile_deposit_yield_bearing": update_from_signal("volatile_deposit_yield_bearing"),
            "total_stable_asset_pcv_balance": pcv_management.update_total_stable_asset_pcv_balance,
            "total_volatile_asset_pcv_balance": pcv_management.update_total_volatile_asset_pcv_balance,
            "total_protocol_owned_fei": pcv_management.update_total_protocol_owned_fei,
        },
    },
    {
        "description": """
            PCV Accounting
        """,
        "policies": {"pcv_accounting": pcv_management.policy_pcv_accounting},
        "variables": {
            "total_pcv": update_from_signal("total_pcv"),
            "total_stable_asset_pcv": update_from_signal("total_stable_asset_pcv"),
            "total_volatile_asset_pcv": update_from_signal("total_volatile_asset_pcv"),
            "stable_backing_ratio": update_from_signal("stable_backing_ratio"),
            "collateralization_ratio": update_from_signal("collateralization_ratio"),
            "protocol_equity": update_from_signal("protocol_equity"),
        },
    },
]
