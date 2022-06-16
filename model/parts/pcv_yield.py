from model.types import (
    APR,
    PCVDeposit,
)


def policy_yield_accrual(params, substep, state_history, previous_state):
    """Yield Accrual Policy
    Accrue simple (or compounded with compounded_yield parameter enabled) interest on yield-bearing PCV Deposits.
    """
    # Parameters
    dt = params["dt"]
    compounded_yield = params["compounded_yield"]

    # State Variables
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    if compounded_yield:
        stable_deposit_yield_bearing.accrue_yield_compounded(dt, stable_asset_price)
        volatile_deposit_yield_bearing.accrue_yield_compounded(dt, volatile_asset_price)
    else:
        stable_deposit_yield_bearing.accrue_yield(dt, stable_asset_price)
        volatile_deposit_yield_bearing.accrue_yield(dt, volatile_asset_price)

    return {
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
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
