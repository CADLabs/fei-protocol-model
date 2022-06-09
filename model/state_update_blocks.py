"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.price_processes as price_processes
import model.parts.pcv_management as pcv_management
import model.parts.liquidity_pools as liquidity_pools

from model.utils import update_from_signal


state_update_blocks = [
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
            "fei_pcv_deposit_liquidity_pool_balance": update_from_signal(
                "fei_pcv_deposit_liquidity_pool_balance"
            ),
            "volatile_asset_pcv_deposit_liquidity_pool_balance": update_from_signal(
                "volatile_asset_pcv_deposit_liquidity_pool_balance"
            ),
            "liquidity_pool_fei_source_sink": update_from_signal(
                "liquidity_pool_fei_source_sink"
            ),
            "fei_minted_redeemed": update_from_signal("fei_minted_redeemed"),
        },
    },
    {
        "description": """
            PCV Rebalancing
        """,
        "policies": {
            "pcv_rebalancing": pcv_management.policy_pcv_rebalancing,
        },
        "variables": {
            "stable_asset_pcv_idle_balance": pcv_management.update_stable_asset_idle_pcv_from_rebalance,
            "stable_asset_pcv_deposit_yield_bearing_balance": pcv_management.update_stable_asset_yield_bearing_pcv_from_rebalance,
            "volatile_asset_pcv_idle_balance": pcv_management.update_volatile_asset_idle_pcv_from_rebalance,
            "volatile_asset_pcv_deposit_yield_bearing_balance": pcv_management.update_volatile_asset_yield_bearing_pcv_from_rebalance,
            "total_stable_asset_pcv_balance": pcv_management.update_total_stable_asset_pcv_balance,
            "total_volatile_asset_pcv_balance": pcv_management.update_total_volatile_asset_pcv_balance,
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
