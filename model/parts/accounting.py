"""Accounting
"""

from model.types import PCVDeposit, UserDeposit, Percentage
from model.system_parameters import Parameters


def policy_fei_accounting(params: Parameters, substep, state_history, previous_state):
    # PCV Deposit State Variables
    fei_idle_pcv_deposit: PCVDeposit = previous_state["fei_idle_pcv_deposit"]
    fei_liquidity_pool_pcv_deposit: PCVDeposit = previous_state["fei_liquidity_pool_pcv_deposit"]
    fei_money_market_pcv_deposit: PCVDeposit = previous_state["fei_money_market_pcv_deposit"]
    fei_money_market_utilization: Percentage = previous_state["fei_money_market_utilization"]

    # User Deposit State Variables
    fei_liquidity_pool_user_deposit: UserDeposit = previous_state["fei_liquidity_pool_user_deposit"]
    fei_money_market_user_deposit: UserDeposit = previous_state["fei_money_market_user_deposit"]
    fei_savings_user_deposit: UserDeposit = previous_state["fei_savings_user_deposit"]
    fei_idle_user_deposit: UserDeposit = previous_state["fei_idle_user_deposit"]

    # State Update
    total_protocol_owned_fei = (
        fei_idle_pcv_deposit.balance
        + fei_liquidity_pool_pcv_deposit.balance
        + fei_money_market_pcv_deposit.balance * (1 - fei_money_market_utilization)
    )

    total_user_circulating_fei = (
        fei_idle_user_deposit.balance
        + fei_savings_user_deposit.balance
        + fei_liquidity_pool_user_deposit.balance
        # Money market user supplied
        + fei_money_market_user_deposit.balance * (1 - fei_money_market_utilization)
        # Money market user borrowed
        + fei_money_market_pcv_deposit.balance * fei_money_market_utilization
    )

    total_fei_supply = total_protocol_owned_fei + total_user_circulating_fei

    return {
        "total_protocol_owned_fei": total_protocol_owned_fei,
        "total_user_circulating_fei": total_user_circulating_fei,
        "total_fei_supply": total_fei_supply,
    }


def policy_pcv_accounting(params, substep, state_history, previous_state):
    # State Variables: Stable PCV
    stable_idle_pcv_deposit: PCVDeposit = previous_state["stable_idle_pcv_deposit"]
    stable_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "stable_yield_bearing_pcv_deposit"
    ]

    # State Variables: Volatile PCV
    volatile_idle_pcv_deposit: PCVDeposit = previous_state["volatile_idle_pcv_deposit"]
    volatile_yield_bearing_pcv_deposit: PCVDeposit = previous_state[
        "volatile_yield_bearing_pcv_deposit"
    ]
    volatile_liquidity_pool_pcv_deposit: PCVDeposit = previous_state[
        "volatile_liquidity_pool_pcv_deposit"
    ]

    # State Variables: Price Processes
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    total_stable_asset_pcv_balance = (
        stable_idle_pcv_deposit.balance + stable_yield_bearing_pcv_deposit.balance
    )
    total_volatile_asset_pcv_balance = (
        volatile_idle_pcv_deposit.balance
        + volatile_yield_bearing_pcv_deposit.balance
        + volatile_liquidity_pool_pcv_deposit.balance
    )
    total_stable_asset_pcv = total_stable_asset_pcv_balance * stable_asset_price
    total_volatile_asset_pcv = total_volatile_asset_pcv_balance * volatile_asset_price
    total_pcv = total_stable_asset_pcv + total_volatile_asset_pcv

    return {
        "total_stable_asset_pcv_balance": total_stable_asset_pcv_balance,
        "total_volatile_asset_pcv_balance": total_volatile_asset_pcv_balance,
        "total_stable_asset_pcv": total_stable_asset_pcv,
        "total_volatile_asset_pcv": total_volatile_asset_pcv,
        "total_pcv": total_pcv,
    }
