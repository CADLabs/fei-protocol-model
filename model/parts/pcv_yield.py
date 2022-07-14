"""PCV Yield
"""

from model.types import (
    APR,
    PCVDeposit,
)
from model.system_parameters import Parameters


def policy_yield_accrual(
    params: Parameters, substep, state_history, previous_state
) -> dict[str, PCVDeposit]:
    """Yield Accrual Policy
    Accrue simple interest on yield-bearing PCV Deposits.
    """
    # Parameters
    dt = params["dt"]

    # State Variables
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    fei_deposit_money_market: PCVDeposit = previous_state["fei_deposit_money_market"]

    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    fei_price = previous_state["fei_price"]

    # State Update
    stable_deposit_yield_bearing.accrue_yield(period_in_days=dt, asset_price=stable_asset_price)
    volatile_deposit_yield_bearing.accrue_yield(period_in_days=dt, asset_price=volatile_asset_price)
    fei_deposit_money_market.accrue_yield(period_in_days=dt, asset_price=fei_price)

    return {
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
        "fei_deposit_money_market": fei_deposit_money_market,
    }


def policy_withdraw_yield(
    params: Parameters, substep, state_history, previous_state
) -> dict[str, PCVDeposit]:
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
    timestep_equals_withdrawal_period = timestep % yield_withdrawal_period / dt == 0
    if timestep_equals_withdrawal_period:  # Periodic yield withdrawal
        stable_deposit_yield_bearing.transfer_yield(
            to=stable_deposit_idle,
            amount=stable_deposit_yield_bearing.yield_accrued,
            asset_price=stable_asset_price,
        )
        volatile_deposit_yield_bearing.transfer_yield(
            to=volatile_deposit_idle,
            amount=volatile_deposit_yield_bearing.yield_accrued,
            asset_price=volatile_asset_price,
        )

    return {
        "stable_deposit_idle": stable_deposit_idle,
        "volatile_deposit_idle": volatile_deposit_idle,
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
    }


def policy_reinvest_yield(
    params: Parameters, substep, state_history, previous_state
) -> dict[str, PCVDeposit]:
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
    timestep_equals_reinvest_period = timestep % yield_reinvest_period / dt == 0
    if timestep_equals_reinvest_period:  # Periodic yield reinvestment
        stable_deposit_yield_bearing.transfer_yield(
            to=stable_deposit_yield_bearing,
            amount=stable_deposit_yield_bearing.yield_accrued,
            asset_price=stable_asset_price,
        )
        volatile_deposit_yield_bearing.transfer_yield(
            to=volatile_deposit_yield_bearing,
            amount=volatile_deposit_yield_bearing.yield_accrued,
            asset_price=volatile_asset_price,
        )

    return {
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
    }
