"""Liquidity Pools
"""

from model.utils import approx_eq
from model.system_parameters import Parameters
from model.types import (
    APR,
    PCVDeposit,
    UserDeposit,
)

import math


def policy_constant_function_market_maker(
    params: Parameters, substep, state_history, previous_state
):
    # Parameters
    dt = params["dt"]
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

    # Calculate protocol's share of the total liquidity pool liquidity
    protocol_liquidity_share = fei_liquidity_pool_pcv_deposit.balance / current_fei_balance

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
    effective_yield_rate: APR = trading_fees / liquidity_pool_tvl * 365 / dt

    # Update PCV Deposit LP balance
    volatile_liquidity_pool_pcv_deposit.set_balance(
        volatile_asset_balance * protocol_liquidity_share, volatile_asset_price
    )
    fei_liquidity_pool_pcv_deposit.set_balance(fei_balance * protocol_liquidity_share, fei_price)

    # Update User Deposit LP balance
    volatile_liquidity_pool_user_deposit.set_balance(
        volatile_asset_balance * (1 - protocol_liquidity_share), volatile_asset_price
    )
    fei_liquidity_pool_user_deposit.set_balance(
        fei_balance * (1 - protocol_liquidity_share), fei_price
    )

    # Update Deposit LP yield rates
    volatile_liquidity_pool_pcv_deposit.yield_rate = effective_yield_rate
    fei_liquidity_pool_pcv_deposit.yield_rate = effective_yield_rate
    volatile_liquidity_pool_user_deposit.yield_rate = effective_yield_rate
    fei_liquidity_pool_user_deposit.yield_rate = effective_yield_rate

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


def update_volatile_liquidity_pool_user_deposit(
    params: Parameters,
    substep,
    state_history,
    previous_state,
    policy_input,
):
    """
    TODO This policy is still WIP.

    Despite fei_balance_delta always being zero, currently the liquidity pool invariant calculation updates the volatile asset balance. TBC if this update is consistent.
    """
    # Policy Inputs
    updated_fei_liquidity_pool_user_deposit = policy_input["fei_liquidity_pool_user_deposit"]

    # State Variables
    liquidity_pool_invariant = previous_state["liquidity_pool_invariant"]
    volatile_liquidity_pool_user_deposit: UserDeposit = previous_state[
        "volatile_liquidity_pool_user_deposit"
    ]
    current_fei_liquidity_pool_user_deposit: UserDeposit = previous_state[
        "fei_liquidity_pool_user_deposit"
    ]
    fei_liquidity_pool_pcv_deposit: UserDeposit = previous_state["fei_liquidity_pool_pcv_deposit"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    fei_balance = current_fei_liquidity_pool_user_deposit.balance
    volatile_asset_balance = volatile_liquidity_pool_user_deposit.balance

    fei_balance_delta = updated_fei_liquidity_pool_user_deposit.balance - fei_balance

    if fei_balance_delta > 0:
        dr, ds, dv = add_liquidity(
            reserve_balance=volatile_asset_balance,
            supply_balance=fei_balance,
            voucher_balance=liquidity_pool_invariant
            * fei_balance
            / fei_liquidity_pool_pcv_deposit.balance,
            tokens=fei_balance_delta,
            value=fei_balance_delta,
        )
        assert fei_balance_delta == ds
        volatile_asset_balance_delta = dr
    elif fei_balance_delta < 0:
        dr, ds, dv = remove_liquidity(
            reserve_balance=volatile_asset_balance,
            supply_balance=fei_balance,
            voucher_balance=liquidity_pool_invariant
            * fei_balance
            / fei_liquidity_pool_pcv_deposit.balance,
            tokens=fei_balance_delta,
            value=fei_balance_delta,
        )
        assert fei_balance_delta == ds
        volatile_asset_balance_delta = dr
    else:
        return "volatile_liquidity_pool_user_deposit", volatile_liquidity_pool_user_deposit

    # TODO Appropriately increase or decrease volatile asset balance
    # TODO Update invariant appropriately using dv
    volatile_liquidity_pool_user_deposit.deposit(volatile_asset_balance_delta, volatile_asset_price)

    return "volatile_liquidity_pool_user_deposit", volatile_liquidity_pool_user_deposit


def add_liquidity(reserve_balance, supply_balance, voucher_balance, tokens, value):
    """
    Example:
    new_reserve = (1 + alpha)*reserve_balance
    new_supply = (1 + alpha)*supply_balance
    new_vouchers = (1 + alpha)*voucher_balance
    """
    if voucher_balance <= 0:
        dr = value
        ds = tokens
        dv = tokens
        return (dr, ds, dv)

    alpha = value / reserve_balance

    dr = alpha * reserve_balance
    ds = alpha * supply_balance
    dv = alpha * voucher_balance

    return (dr, ds, dv)


def remove_liquidity(reserve_balance, supply_balance, voucher_balance, tokens):
    """
    Example:
    new_reserve = (1 - alpha)*reserve_balance
    new_supply = (1 - alpha)*supply_balance
    new_liquidity_tokens = (1 - alpha)*liquidity_token_balance
    """
    alpha = tokens / voucher_balance

    dr = -alpha * reserve_balance
    ds = -alpha * supply_balance
    dv = -alpha * voucher_balance

    return (dr, ds, dv)
