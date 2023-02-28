"""# Liquidity Pools Module
Implementation of a generic Liquidity Pool to model the dynamic of market condition dependent imbalances causing sourcing and sinking of FEI in the system.
"""

import numpy as np
from model.state_variables import StateVariables
from model.utils import approx_eq
from model.system_parameters import Parameters
from model.types import (
    APR,
    FEI,
    PCVDeposit,
    UserDeposit,
    VolatileAssetUnits,
)

import math
import model.parts.uniswap as uniswap


def policy_constant_function_market_maker(
    params: Parameters, substep, state_history, previous_state
):
    """## Constant Function Market Maker (CFMM) Policy
    An implementation of a Uniswap style Constant Function Market Maker.
    """
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

    # Liquidity Pool imbalance
    target_fei_balance = math.sqrt(k * volatile_asset_price / fei_price)
    target_volatile_asset_balance = math.sqrt(k * fei_price / volatile_asset_price)

    current_fei_balance = get_total_fei_balance(previous_state)
    delta_fei_balance = target_fei_balance - current_fei_balance

    current_volatile_asset_balance = get_total_volatile_asset_balance(previous_state)
    delta_volatile_asset_balance = target_volatile_asset_balance - current_volatile_asset_balance

    # Calculate protocol's share of the total liquidity pool liquidity
    protocol_liquidity_share = fei_liquidity_pool_pcv_deposit.balance / current_fei_balance

    assert approx_eq(
        target_fei_balance * target_volatile_asset_balance, k, abs_tol=1
    ), f"Constant product invariant broken: off by {target_fei_balance * target_volatile_asset_balance - k}"

    """
    Collect Uniswap V2 style trading fees
    Fees collected on incoming asset
    See https://docs.uniswap.org/whitepaper.pdf:
    (x1 - 0.003 · xin)) · y1 >= x0 · y0
    """
    trading_fees = 0
    if delta_fei_balance > 0:
        # Liquidity pool is a sink for FEI
        # Aggregate trading fees collected on incoming FEI
        trading_fees_balance = liquidity_pool_trading_fee * abs(delta_fei_balance)
        delta_fei_balance += trading_fees_balance
        trading_fees = trading_fees_balance * fei_price
    else:
        # Liquidity pool is a source of FEI
        # Aggregate trading fees collected on incoming volatile asset
        trading_fees_balance = liquidity_pool_trading_fee * abs(delta_volatile_asset_balance)
        delta_volatile_asset_balance += trading_fees_balance
        trading_fees = trading_fees_balance * volatile_asset_price

    updated_fei_balance = current_fei_balance + delta_fei_balance
    updated_volatile_asset_balance = current_volatile_asset_balance + delta_volatile_asset_balance

    k = updated_fei_balance * updated_volatile_asset_balance
    liquidity_pool_tvl = (
        updated_fei_balance * fei_price + updated_volatile_asset_balance * volatile_asset_price
    )
    price_ratio = state_history[0][0]["volatile_asset_price"] / volatile_asset_price
    impermanent_loss = 2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1
    yield_rate: APR = trading_fees / liquidity_pool_tvl * 365 / dt

    # Update PCV Deposit LP balance
    volatile_liquidity_pool_pcv_deposit.set_balance(
        updated_volatile_asset_balance * protocol_liquidity_share, volatile_asset_price
    )
    fei_liquidity_pool_pcv_deposit.set_balance(
        updated_fei_balance * protocol_liquidity_share, fei_price
    )

    # Update User Deposit LP balance
    volatile_liquidity_pool_user_deposit.set_balance(
        updated_volatile_asset_balance * (1 - protocol_liquidity_share),
        volatile_asset_price,
    )
    fei_liquidity_pool_user_deposit.set_balance(
        updated_fei_balance * (1 - protocol_liquidity_share), fei_price
    )

    # Update Deposit LP yield rates
    effective_yield_rate = max(0, yield_rate - abs(impermanent_loss))
    volatile_liquidity_pool_pcv_deposit.yield_rate = effective_yield_rate
    fei_liquidity_pool_pcv_deposit.yield_rate = effective_yield_rate
    volatile_liquidity_pool_user_deposit.yield_rate = effective_yield_rate
    fei_liquidity_pool_user_deposit.yield_rate = effective_yield_rate

    return {
        "liquidity_pool_fei_source_sink": -delta_fei_balance,
        # Assumes any FEI released into circulating supply is redeemed
        "fei_minted_redeemed": delta_fei_balance,
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


def update_fei_liquidity(
    previous_state,
    updated_fei_liquidity_pool_user_deposit: UserDeposit,
):
    """## Update FEI Liquidity
    A State Update Function that updates the relevant liquidity pool State Variables including the Volatile Asset Liquidity Pool User Deposit balance
    given a change in the FEI Liquidity Pool User Deposit balance for the purpose of adding or removing liquidity.
    """
    # State Variables
    liquidity_pool_invariant = previous_state["liquidity_pool_invariant"]
    liquidity_pool_liquidity_tokens = previous_state["liquidity_pool_liquidity_tokens"]
    volatile_liquidity_pool_user_deposit: UserDeposit = previous_state[
        "volatile_liquidity_pool_user_deposit"
    ]
    fei_liquidity_pool_user_deposit: UserDeposit = previous_state["fei_liquidity_pool_user_deposit"]

    fei_price = previous_state["fei_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    total_fei_balance = get_total_fei_balance(previous_state)
    total_volatile_asset_balance = get_total_volatile_asset_balance(previous_state)

    user_fei_balance_delta = (
        updated_fei_liquidity_pool_user_deposit.balance - fei_liquidity_pool_user_deposit.balance
    )

    assert np.isclose(
        total_volatile_asset_balance * total_fei_balance, liquidity_pool_invariant
    ), f"Constant product invariant broken: off by {total_volatile_asset_balance * total_fei_balance - liquidity_pool_invariant}"

    if user_fei_balance_delta > 0:
        dr, ds, dv = uniswap.add_liquidity(
            reserve_balance=total_volatile_asset_balance,
            supply_balance=total_fei_balance,
            voucher_balance=liquidity_pool_liquidity_tokens,
            tokens=user_fei_balance_delta,
            value=user_fei_balance_delta * fei_price / volatile_asset_price,
        )
        assert dr >= 0
        assert ds >= 0
        assert dv >= 0
        liquidity_pool_liquidity_tokens += dv
        volatile_liquidity_pool_user_deposit.deposit(dr, volatile_asset_price)
        fei_liquidity_pool_user_deposit.deposit(ds, fei_price)
    elif user_fei_balance_delta < 0:
        dr, ds, dv = uniswap.remove_liquidity(
            reserve_balance=total_volatile_asset_balance,
            supply_balance=total_fei_balance,
            voucher_balance=liquidity_pool_liquidity_tokens,
            tokens=abs(user_fei_balance_delta)
            * liquidity_pool_liquidity_tokens
            / total_fei_balance,
        )
        assert dr <= 0
        assert ds <= 0
        assert dv <= 0
        liquidity_pool_liquidity_tokens += dv
        volatile_liquidity_pool_user_deposit.withdraw(abs(dr), volatile_asset_price)
        fei_liquidity_pool_user_deposit.withdraw(abs(ds), fei_price)
    else:
        return {
            "fei_liquidity_pool_user_deposit": fei_liquidity_pool_user_deposit,
            "volatile_liquidity_pool_user_deposit": volatile_liquidity_pool_user_deposit,
            "liquidity_pool_invariant": liquidity_pool_invariant,
            "liquidity_pool_liquidity_tokens": liquidity_pool_liquidity_tokens,
        }

    liquidity_pool_invariant = get_total_fei_balance(
        previous_state
    ) * get_total_volatile_asset_balance(previous_state)

    return {
        "fei_liquidity_pool_user_deposit": fei_liquidity_pool_user_deposit,
        "volatile_liquidity_pool_user_deposit": volatile_liquidity_pool_user_deposit,
        "liquidity_pool_invariant": liquidity_pool_invariant,
        "liquidity_pool_liquidity_tokens": liquidity_pool_liquidity_tokens,
    }


def get_total_fei_balance(state: StateVariables) -> FEI:
    """## Get Total FEI Liquidity Pool Balance
    A helper function to calculate the total liquidity pool FEI balance
    as a combination of User and PCV Deposit balances.
    """
    return (
        state["fei_liquidity_pool_user_deposit"].balance
        + state["fei_liquidity_pool_pcv_deposit"].balance
    )


def get_total_volatile_asset_balance(state: StateVariables) -> VolatileAssetUnits:
    """## Get Total Volatile Asset Liquidity Pool Balance
    A helper function to calculate the total liquidity pool Volatile Asset balance
    as a combination of User and PCV Deposit balances.
    """
    return (
        state["volatile_liquidity_pool_user_deposit"].balance
        + state["volatile_liquidity_pool_pcv_deposit"].balance
    )
