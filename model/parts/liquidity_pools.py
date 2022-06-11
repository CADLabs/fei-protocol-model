from model.state_variables import StateVariables
from model.utils import approx_eq
import math

from model.types import (
    Uninitialized,
    Percentage,
    APY,
    USD,
    FEI,
    VolatileAssetUnits,
    StableAssetUnits,
    PCVDeposit,
)


def policy_constant_function_market_maker(
    params, substep, state_history, previous_state
):
    # State Variables
    k = previous_state["liquidity_pool_invariant"]
    liquidity_pool_tvl = previous_state["liquidity_pool_tvl"]
    previous_fei_balance = previous_state["fei_pcv_deposit_liquidity_pool_balance"]
    fei_price = previous_state["fei_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # Liquidity Pool Imbalance
    fei_balance = math.sqrt(k * volatile_asset_price / fei_price)
    volatile_asset_balance = math.sqrt(k * fei_price / volatile_asset_price)
    fei_source_sink = previous_fei_balance - fei_balance

    liquidity_pool_tvl = (
        fei_balance * fei_price + volatile_asset_balance * volatile_asset_price
    )

    assert approx_eq(
        fei_balance * volatile_asset_balance, k, abs_tol=1e-3
    ), "Constant product invariant broken"

    return {
        "fei_pcv_deposit_liquidity_pool_balance": fei_balance,
        "volatile_asset_pcv_deposit_liquidity_pool_balance": volatile_asset_balance,
        "liquidity_pool_fei_source_sink": fei_source_sink,
        # Assumes any FEI released into circulating supply is redeemed
        "fei_minted_redeemed": -fei_source_sink,
        "liquidity_pool_tvl": liquidity_pool_tvl,
    }


def update_volatile_deposit_liquidity_pool(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update yield bearing volatile asset PCV balance
    """
    # DEBUG: placeholder dynamics
    
    volatile_deposit_state: PCVDeposit = previous_state['volatile_deposit_liquidity_pool'] 
    volatile_asset_price = previous_state["volatile_asset_price"]
    volatile_asset_lp_balance = policy_input["volatile_asset_pcv_deposit_liquidity_pool_balance"]

    new_state = PCVDeposit(
                    asset = "volatile",
                    deposit_type = "liquidity_pool", # liquidity_pool, money_market, liquidity_pool
                    balance = volatile_asset_lp_balance,
                    asset_value = volatile_asset_lp_balance * volatile_asset_price,
#                     balance = 0.0,
#                     asset_value = 0.0,
                    yield_balance = volatile_deposit_state.yield_balance,
                    yield_value = volatile_deposit_state.yield_value,
                    yield_rate = volatile_deposit_state.yield_rate
                )

    return (
        "volatile_deposit_liquidity_pool",
        new_state,
    )


def update_fei_deposit_liquidity_pool(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update yield bearing fei asset PCV balance
    """
    # DEBUG: placeholder dynamics
    
    fei_deposit_state: PCVDeposit = previous_state['fei_deposit_liquidity_pool'] 
    fei_price = previous_state["fei_price"]
    fei_asset_lp_balance = policy_input["fei_pcv_deposit_liquidity_pool_balance"]
    
    new_state = PCVDeposit(
                    asset = "fei",
                    deposit_type = "liquidity_pool", # liquidity_pool, money_market, liquidity_pool
                    balance = fei_asset_lp_balance,
                    asset_value = fei_asset_lp_balance * fei_price,
                    yield_balance = fei_deposit_state.yield_balance,
                    yield_value = fei_deposit_state.yield_value,
                    yield_rate = fei_deposit_state.yield_rate
                )

    return (
        "fei_deposit_liquidity_pool",
        new_state,
    )
