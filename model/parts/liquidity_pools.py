from model.state_variables import StateVariables
from model.utils import approx_eq
import math

from model.types import (
    PCVDeposit,
)


def policy_constant_function_market_maker(params, substep, state_history, previous_state):
    # State Variables
    fei_deposit_liquidity_pool: PCVDeposit = previous_state["fei_deposit_liquidity_pool"]
    k = previous_state["liquidity_pool_invariant"]
    liquidity_pool_tvl = previous_state["liquidity_pool_tvl"]
    fei_price = previous_state["fei_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # Liquidity Pool Imbalance
    previous_fei_balance = fei_deposit_liquidity_pool.balance
    fei_balance = math.sqrt(k * volatile_asset_price / fei_price)
    volatile_asset_balance = math.sqrt(k * fei_price / volatile_asset_price)
    fei_source_sink = previous_fei_balance - fei_balance

    liquidity_pool_tvl = fei_balance * fei_price + volatile_asset_balance * volatile_asset_price

    assert approx_eq(
        fei_balance * volatile_asset_balance, k, abs_tol=1e-2
    ), "Constant product invariant broken"

    return {
        "fei_balance": fei_balance,
        "volatile_asset_balance": volatile_asset_balance,
        "liquidity_pool_fei_source_sink": fei_source_sink,
        # Assumes any FEI released into circulating supply is redeemed
        "fei_minted_redeemed": -fei_source_sink,
        "liquidity_pool_tvl": liquidity_pool_tvl,
    }


def update_volatile_deposit_liquidity_pool(
    params, substep, state_history, previous_state, policy_input
):
    # Policy Inputs
    volatile_asset_balance = policy_input["volatile_asset_balance"]

    # State Variables
    volatile_deposit_liquidity_pool: PCVDeposit = previous_state["volatile_deposit_liquidity_pool"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    volatile_deposit_liquidity_pool.balance = volatile_asset_balance
    volatile_deposit_liquidity_pool.asset_value = volatile_asset_balance * volatile_asset_price

    return "volatile_deposit_liquidity_pool", volatile_deposit_liquidity_pool


def update_fei_deposit_liquidity_pool(params, substep, state_history, previous_state, policy_input):
    # Policy Inputs
    fei_balance = policy_input["fei_balance"]

    # State Variables
    fei_deposit_liquidity_pool: PCVDeposit = previous_state["fei_deposit_liquidity_pool"]
    fei_price = previous_state["fei_price"]

    # State Update
    fei_deposit_liquidity_pool.balance = fei_balance
    fei_deposit_liquidity_pool.asset_value = fei_balance * fei_price

    return "fei_deposit_liquidity_pool", fei_deposit_liquidity_pool
