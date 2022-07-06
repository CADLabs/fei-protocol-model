"""PCV Yield
"""

from model.types import (
    APR,
    PCVDeposit,
)


def policy_yield_accrual(params, substep, state_history, previous_state):
    """Yield Accrual Policy
    Accrue simple interest on yield-bearing PCV Deposits.
    """
    # Parameters
    dt = params["dt"]

    # State Variables
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    fei_deposit_money_market: PCVDeposit = previous_state["fei_deposit_money_market"]
    liquidity_pool_trading_fees = previous_state["liquidity_pool_trading_fees"]

    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    fei_price = previous_state["fei_price"]

    # State Update
    pcv_yield = stable_deposit_yield_bearing.accrue_yield(dt, stable_asset_price)
    pcv_yield += volatile_deposit_yield_bearing.accrue_yield(dt, volatile_asset_price)
    pcv_yield += fei_deposit_money_market.accrue_yield(dt, fei_price)
    pcv_yield += liquidity_pool_trading_fees

    return {
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
        "fei_deposit_money_market": fei_deposit_money_market,
        "pcv_yield": pcv_yield,
    }


def policy_withdraw_yield(params, substep, state_history, previous_state):
    """Withdraw Yield Policy
    Withdraw yield into idle PCV Deposit periodically.
    """

    # Parameters
    dt = params["dt"]
    yield_withdrawal_period = params["yield_withdrawal_period"]

    # State Variables
    timestep = previous_state["timestep"]
    stable_deposit_idle: PCVDeposit = previous_state["stable_deposit_idle"]
    volatile_deposit_idle: PCVDeposit = previous_state["volatile_deposit_idle"]
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    if timestep % yield_withdrawal_period / dt == 0:  # Periodic yield withdrawal
        stable_deposit_yield_bearing.transfer_yield(
            stable_deposit_idle,
            stable_deposit_yield_bearing.yield_accrued,
            stable_asset_price,
        )
        volatile_deposit_yield_bearing.transfer_yield(
            volatile_deposit_idle,
            volatile_deposit_yield_bearing.yield_accrued,
            volatile_asset_price,
        )

    return {
        "stable_deposit_idle": stable_deposit_idle,
        "volatile_deposit_idle": volatile_deposit_idle,
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
    }


def policy_reinvest_yield(params, substep, state_history, previous_state):
    """Reinvest Yield Policy
    Reinvest yield accrued periodically.
    """

    # Parameters
    dt = params["dt"]
    yield_reinvest_period = params["yield_reinvest_period"]

    # State Variables
    timestep = previous_state["timestep"]
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    if timestep % yield_reinvest_period / dt == 0:  # Periodic yield reinvestment
        stable_deposit_yield_bearing.transfer_yield(
            stable_deposit_yield_bearing,
            stable_deposit_yield_bearing.yield_accrued,
            stable_asset_price,
        )
        volatile_deposit_yield_bearing.transfer_yield(
            volatile_deposit_yield_bearing,
            volatile_deposit_yield_bearing.yield_accrued,
            volatile_asset_price,
        )

    return {
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
    }
