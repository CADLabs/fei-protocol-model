"""Liquidity Pools
"""

from model.utils import approx_eq
from model.system_parameters import Parameters
from model.types import (
    PCVDeposit,
)

import math


def policy_constant_function_market_maker(params: Parameters, substep, state_history, previous_state):
    # Parameters
    liquidity_pool_trading_fee = params["liquidity_pool_trading_fee"]

    # State Variables
    fei_deposit_liquidity_pool: PCVDeposit = previous_state["fei_deposit_liquidity_pool"]
    volatile_deposit_liquidity_pool: PCVDeposit = previous_state["volatile_deposit_liquidity_pool"]
    k = previous_state["liquidity_pool_invariant"]
    fei_price = previous_state["fei_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # Liquidity Pool Imbalance
    # TODO [engineering] 2022-07-11: i believe it is worthwhile moving this part until Impermanent Loss calculation,
    #  to a separate function since it is highly specific and is not about fetching values from previous states and spitting out the values.
    #  Rather we calculate something entirely new. C++ creator Bjarne Stroustrup advocates for separate functions when code becomes longer than 7 lines.
    #  It would also bring the chance to add a docstring to that function, and eventually make it generic enough to easily re-use it for other
    #  liquidity pool venues. We could then think of extensions of fragmented liquidity / uniformly allocating our PCV to several liquidity pools.
    fei_balance = math.sqrt(k * volatile_asset_price / fei_price)
    volatile_asset_balance = math.sqrt(k * fei_price / volatile_asset_price)
    fei_source_sink = fei_deposit_liquidity_pool.balance - fei_balance
    volatile_asset_source_sink = volatile_deposit_liquidity_pool.balance - volatile_asset_balance

    assert approx_eq(
        fei_balance * volatile_asset_balance, k, abs_tol=1e-2
    ), "Constant product invariant broken"

    """
    Collect Uniswap V2 style trading fees
    Fees collected on incoming asset
    See https://docs.uniswap.org/whitepaper.pdf:
    (x1 - 0.003 · xin)) · y1 >= x0 · y0
    """
    trading_fees = 0
    if fei_source_sink > 0:
        # Liquidity pool is a source of FEI
        # Aggregate trading fees collected on incoming volatile asset
        trading_fees = liquidity_pool_trading_fee * abs(volatile_asset_source_sink)
        volatile_asset_balance += trading_fees
    else:
        # Liquidity pool is a sink for FEI
        # Aggregate trading fees collected on incoming FEI
        trading_fees = liquidity_pool_trading_fee * abs(fei_source_sink)
        fei_balance += trading_fees

    k = fei_balance * volatile_asset_balance
    liquidity_pool_tvl = fei_balance * fei_price + volatile_asset_balance * volatile_asset_price
    price_ratio = state_history[0][0]["volatile_asset_price"] / volatile_asset_price
    impermanent_loss = 2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1

    return {
        "fei_balance": fei_balance,
        "volatile_asset_balance": volatile_asset_balance,
        "liquidity_pool_fei_source_sink": fei_source_sink,
        # Assumes any FEI released into circulating supply is redeemed
        "fei_minted_redeemed": -fei_source_sink,
        "liquidity_pool_invariant": k,
        "liquidity_pool_tvl": liquidity_pool_tvl,
        "liquidity_pool_impermanent_loss": impermanent_loss,
        "liquidity_pool_trading_fees": trading_fees,
    }


def update_volatile_deposit_liquidity_pool(params: Parameters, substep, state_history, previous_state, policy_input):
    # Policy Inputs
    volatile_asset_balance = policy_input["volatile_asset_balance"]

    # State Variables
    volatile_deposit_liquidity_pool: PCVDeposit = previous_state["volatile_deposit_liquidity_pool"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    volatile_deposit_liquidity_pool.set_balance(volatile_asset_balance, volatile_asset_price)

    return "volatile_deposit_liquidity_pool", volatile_deposit_liquidity_pool


def update_fei_deposit_liquidity_pool(params: Parameters, substep, state_history, previous_state, policy_input):
    # Policy Inputs
    fei_balance = policy_input["fei_balance"]

    # State Variables
    fei_deposit_liquidity_pool: PCVDeposit = previous_state["fei_deposit_liquidity_pool"]
    fei_price = previous_state["fei_price"]

    # State Update
    fei_deposit_liquidity_pool.set_balance(fei_balance, fei_price)

    return "fei_deposit_liquidity_pool", fei_deposit_liquidity_pool
