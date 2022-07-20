"""Liquidity Pools
"""

from model.utils import approx_eq
from model.system_parameters import Parameters
from model.types import (
    PCVDeposit,
    UserDeposit,
)

import math


def policy_constant_function_market_maker(
    params: Parameters, substep, state_history, previous_state
):
    # Parameters
    liquidity_pool_trading_fee = params["liquidity_pool_trading_fee"]

    # State Variables
    fei_liquidity_pool_pcv_deposit: PCVDeposit = previous_state["fei_liquidity_pool_pcv_deposit"]
    volatile_liquidity_pool_pcv_deposit: PCVDeposit = previous_state[
        "volatile_liquidity_pool_pcv_deposit"
    ]
    fei_liquidity_pool_user_deposit: UserDeposit = previous_state["fei_liquidity_pool_user_deposit"]
    volatile_liquidity_pool_user_deposit: UserDeposit = previous_state[
        "volatile_liquidity_pool_user_deposit"
    ]
    k = previous_state["liquidity_pool_invariant"]
    fei_price = previous_state["fei_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # Liquidity Pool Imbalance
    # TODO Consider refactoring this policy to move re-usable liquidity pool logic into its own function
    fei_balance = math.sqrt(k * volatile_asset_price / fei_price)
    volatile_asset_balance = math.sqrt(k * fei_price / volatile_asset_price)

    current_fei_balance = (
        fei_liquidity_pool_pcv_deposit.balance + fei_liquidity_pool_user_deposit.balance
    )
    fei_source_sink = current_fei_balance - fei_balance

    current_volatile_asset_balance = (
        volatile_liquidity_pool_pcv_deposit.balance + volatile_liquidity_pool_user_deposit.balance
    )
    volatile_asset_source_sink = current_volatile_asset_balance - volatile_asset_balance

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
        trading_fees_balance = liquidity_pool_trading_fee * abs(volatile_asset_source_sink)
        volatile_asset_balance += trading_fees_balance
        trading_fees = trading_fees_balance * volatile_asset_price
    else:
        # Liquidity pool is a sink for FEI
        # Aggregate trading fees collected on incoming FEI
        trading_fees_balance = liquidity_pool_trading_fee * abs(fei_source_sink)
        fei_balance += trading_fees_balance
        trading_fees = trading_fees_balance * fei_price

    k = fei_balance * volatile_asset_balance
    liquidity_pool_tvl = fei_balance * fei_price + volatile_asset_balance * volatile_asset_price
    price_ratio = state_history[0][0]["volatile_asset_price"] / volatile_asset_price
    impermanent_loss = 2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1

    # Calculate protocol's share of the total liquidity pool liquidity
    protocol_liquidity_share = fei_liquidity_pool_pcv_deposit.balance / current_fei_balance

    # Update PCV Deposit LP balance
    fei_liquidity_pool_pcv_deposit.set_balance(fei_balance * protocol_liquidity_share, fei_price)
    volatile_liquidity_pool_pcv_deposit.set_balance(
        volatile_asset_balance * protocol_liquidity_share, volatile_asset_price
    )

    # Update User Deposit LP balance
    fei_liquidity_pool_user_deposit.set_balance(
        fei_balance * (1 - protocol_liquidity_share), fei_price
    )
    volatile_liquidity_pool_user_deposit.set_balance(
        volatile_asset_balance * (1 - protocol_liquidity_share), volatile_asset_price
    )

    return {
        "liquidity_pool_fei_source_sink": fei_source_sink,
        # Assumes any FEI released into circulating supply is redeemed
        "fei_minted_redeemed": -fei_source_sink,
        "liquidity_pool_invariant": k,
        "liquidity_pool_tvl": liquidity_pool_tvl,
        "liquidity_pool_impermanent_loss": impermanent_loss,
        "liquidity_pool_trading_fees": trading_fees,
        # PCV Deposit and User Deposit updates
        "fei_liquidity_pool_pcv_deposit": fei_liquidity_pool_pcv_deposit,
        "volatile_liquidity_pool_pcv_deposit": volatile_liquidity_pool_pcv_deposit,
        "fei_liquidity_pool_user_deposit": fei_liquidity_pool_user_deposit,
        "volatile_liquidity_pool_user_deposit": volatile_liquidity_pool_user_deposit,
    }
