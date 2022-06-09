from model.state_variables import StateVariables
from model.utils import approx_eq
import math


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
