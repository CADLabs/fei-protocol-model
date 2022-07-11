"""Accounting
"""

from model.types import PCVDeposit, Percentage
from model.system_parameters import Parameters


def policy_fei_accounting(params: Parameters, substep, state_history, previous_state):
    # State Variables
    fei_deposit_idle: PCVDeposit = previous_state["fei_deposit_idle"]
    fei_deposit_liquidity_pool: PCVDeposit = previous_state["fei_deposit_liquidity_pool"]
    fei_deposit_money_market: PCVDeposit = previous_state["fei_deposit_money_market"]
    fei_money_market_utilization: Percentage = previous_state["fei_money_market_utilization"]

    idle_user_circulating_fei = previous_state["idle_user_circulating_fei"]
    fei_savings_deposit_balance = previous_state["fei_savings_deposit_balance"]

    # State Update
    total_protocol_owned_fei = (
        fei_deposit_idle.balance
        + fei_deposit_liquidity_pool.balance
        + fei_deposit_money_market.balance * (1 - fei_money_market_utilization)
    )

    total_user_circulating_fei = (
        idle_user_circulating_fei
        + fei_savings_deposit_balance
        + fei_deposit_money_market.balance * fei_money_market_utilization
    )

    total_fei_supply = total_protocol_owned_fei + total_user_circulating_fei

    return {
        "total_protocol_owned_fei": total_protocol_owned_fei,
        "total_user_circulating_fei": total_user_circulating_fei,
        "total_fei_supply": total_fei_supply,
    }


def policy_pcv_accounting(params, substep, state_history, previous_state):
    # State Variables: Stable PCV
    stable_deposit_idle: PCVDeposit = previous_state["stable_deposit_idle"]
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]

    # State Variables: Volatile PCV
    volatile_deposit_idle: PCVDeposit = previous_state["volatile_deposit_idle"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]
    volatile_deposit_liquidity_pool: PCVDeposit = previous_state["volatile_deposit_liquidity_pool"]

    # State Variables: Price Processes
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # State Update
    total_stable_asset_pcv_balance = (
        stable_deposit_idle.balance + stable_deposit_yield_bearing.balance
    )
    total_volatile_asset_pcv_balance = (
        volatile_deposit_idle.balance
        + volatile_deposit_yield_bearing.balance
        + volatile_deposit_liquidity_pool.balance
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
