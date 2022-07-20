"""PCV Yield
"""

from model.types import (
    PCVDeposit,
    UserDeposit,
)
from model.system_parameters import Parameters


def policy_yield_accrual(params: Parameters, substep, state_history, previous_state):
    """Yield Accrual Policy
    Accrue simple interest on yield-bearing PCV Deposits.
    """
    # Parameters
    dt = params["dt"]

    # State Variables
    stable_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "stable_yield_bearing_pcv_deposit"
    ]
    volatile_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "volatile_yield_bearing_pcv_deposit"
    ]
    fei_money_market_pcv_deposit: PCVDeposit = previous_state["fei_money_market_pcv_deposit"]
    fei_liquidity_pool_pcv_deposit: PCVDeposit = previous_state["fei_liquidity_pool_pcv_deposit"]
    fei_liquidity_pool_user_deposit: UserDeposit = previous_state["fei_liquidity_pool_user_deposit"]
    liquidity_pool_trading_fees = previous_state["liquidity_pool_trading_fees"]

    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    fei_price = previous_state["fei_price"]

    # Calculate protocol's share of the total liquidity pool trading fees
    protocol_liquidity_share = fei_liquidity_pool_pcv_deposit.balance / (
        fei_liquidity_pool_pcv_deposit.balance + fei_liquidity_pool_user_deposit.balance
    )
    protocol_liquidity_pool_trading_fees = protocol_liquidity_share * liquidity_pool_trading_fees

    # State Update
    pcv_yield = sum(
        [
            # NOTE accrue_yield() updates PCV Deposit yield
            stable_yield_bearing_pcv_deposit.accrue_yield(
                period_in_days=dt, asset_price=stable_asset_price
            ),
            volatile_yield_bearing_pcv_deposit.accrue_yield(
                period_in_days=dt, asset_price=volatile_asset_price
            ),
            fei_money_market_pcv_deposit.accrue_yield(period_in_days=dt, asset_price=fei_price),
            protocol_liquidity_pool_trading_fees,
        ]
    )

    return {
        "stable_yield_bearing_pcv_deposit": stable_yield_bearing_pcv_deposit,
        "volatile_yield_bearing_pcv_deposit": volatile_yield_bearing_pcv_deposit,
        "fei_money_market_pcv_deposit": fei_money_market_pcv_deposit,
        "pcv_yield": pcv_yield,
    }


def policy_withdraw_yield(params: Parameters, substep, state_history, previous_state):
    """Withdraw Yield Policy
    Withdraw yield into idle PCV Deposit periodically.
    """

    # Parameters
    dt = params["dt"]
    yield_withdrawal_period = params["yield_withdrawal_period"]

    # State Variables
    timestep = previous_state["timestep"]
    stable_idle_pcv_deposit: PCVDeposit = previous_state["stable_idle_pcv_deposit"]
    volatile_idle_pcv_deposit: PCVDeposit = previous_state["volatile_idle_pcv_deposit"]
    stable_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "stable_yield_bearing_pcv_deposit"
    ]
    volatile_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "volatile_yield_bearing_pcv_deposit"
    ]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    timestep_equals_withdrawal_period = timestep % yield_withdrawal_period / dt == 0
    if timestep_equals_withdrawal_period:  # Periodic yield withdrawal
        stable_yield_bearing_pcv_deposit.transfer_yield(
            to=stable_idle_pcv_deposit,
            amount=stable_yield_bearing_pcv_deposit.yield_accrued,
            asset_price=stable_asset_price,
        )
        volatile_yield_bearing_pcv_deposit.transfer_yield(
            to=volatile_idle_pcv_deposit,
            amount=volatile_yield_bearing_pcv_deposit.yield_accrued,
            asset_price=volatile_asset_price,
        )

    return {
        "stable_idle_pcv_deposit": stable_idle_pcv_deposit,
        "volatile_idle_pcv_deposit": volatile_idle_pcv_deposit,
        "stable_yield_bearing_pcv_deposit": stable_yield_bearing_pcv_deposit,
        "volatile_yield_bearing_pcv_deposit": volatile_yield_bearing_pcv_deposit,
    }


def policy_reinvest_yield(params: Parameters, substep, state_history, previous_state):
    """Reinvest Yield Policy
    Reinvest yield accrued periodically.
    """

    # Parameters
    dt = params["dt"]
    yield_reinvest_period = params["yield_reinvest_period"]

    # State Variables
    timestep = previous_state["timestep"]
    stable_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "stable_yield_bearing_pcv_deposit"
    ]
    volatile_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "volatile_yield_bearing_pcv_deposit"
    ]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    timestep_equals_reinvest_period = timestep % yield_reinvest_period / dt == 0
    if timestep_equals_reinvest_period:  # Periodic yield reinvestment
        stable_yield_bearing_pcv_deposit.transfer_yield(
            to=stable_yield_bearing_pcv_deposit,
            amount=stable_yield_bearing_pcv_deposit.yield_accrued,
            asset_price=stable_asset_price,
        )
        volatile_yield_bearing_pcv_deposit.transfer_yield(
            to=volatile_yield_bearing_pcv_deposit,
            amount=volatile_yield_bearing_pcv_deposit.yield_accrued,
            asset_price=volatile_asset_price,
        )

    return {
        "stable_yield_bearing_pcv_deposit": stable_yield_bearing_pcv_deposit,
        "volatile_yield_bearing_pcv_deposit": volatile_yield_bearing_pcv_deposit,
    }
