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
            "liquidity_pool_fei_source_sink": update_from_signal(
                "liquidity_pool_fei_source_sink"
            ),
            "fei_minted_redeemed": update_from_signal("fei_minted_redeemed"),
            "liquidity_pool_tvl": update_from_signal("liquidity_pool_tvl"),
            "volatile_deposit_liquidity_pool": liquidity_pools.update_volatile_deposit_liquidity_pool,
            "fei_deposit_liquidity_pool": liquidity_pools.update_fei_deposit_liquidity_pool,
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
            "stable_deposit_idle": pcv_management.update_stable_deposit_idle,
            "stable_deposit_yield_bearing": pcv_management.update_stable_deposit_yield_bearing,
            "volatile_deposit_idle": pcv_management.update_volatile_deposit_idle,
            "volatile_deposit_yield_bearing": pcv_management.update_volatile_deposit_yield_bearing,
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
