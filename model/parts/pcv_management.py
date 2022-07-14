"""PCV Management
"""

import logging
from model.types import (
    PCVDeposit,
    USD,
)
from model.system_parameters import Parameters


def policy_pcv_rebalancing_target_stable_pcv(
    params: Parameters, substep, state_history, previous_state
):
    """PCV Rebalancing: Target Stable PCV Policy
    The following PCV rebalancing policy targets a specific stable PCV ratio,
    i.e. the % of PCV value that is backed by stable assets.

    To meet the target allocation between stable and volatile assets,
    PCV rebalancing is first attempted from idle PCV deposits.

    If there is insufficient capital in idle PCV deposits to allocate to meet the stable PCV target,
    movements are made in tranches/priority first from yield-bearing PCV,
    followed by any other PCV included in the rebalancing strategy.

    Rebalancing is performed periodically according to the rebalancing_period parameter,
    when the target_stable_pcv_ratio parameter is below OR above the target,
    according to the target_rebalancing_condition parameter.

    # Rebalancing Parameters
    rebalancing_period: the duration in days between applying rebalancing strategy

    target_stable_pcv_ratio: the target % of PCV value that is backed by stable assets

    target_rebalancing_condition: rebalance towards target stable PCV ratio if less than (lt, <) or greater than (gt, >) target,
    if market conditions are good the strategy can increase volatile asset exposure,
    and if market conditions are bad the strategy can reduce volatile asset exposure.
    """
    # Params
    dt = params["dt"]
    rebalancing_period = params["rebalancing_period"]
    target_stable_pcv_ratio = params["target_stable_pcv_ratio"]
    target_rebalancing_condition = params["target_rebalancing_condition"]

    # Previous State
    timestep = previous_state["timestep"]
    total_pcv = previous_state["total_pcv"]
    stable_pcv_ratio = previous_state["stable_pcv_ratio"]
    volatile_asset_price = previous_state["volatile_asset_price"]
    stable_asset_price = previous_state["stable_asset_price"]

    # Relevant PCV Deposits
    stable_deposit_idle: PCVDeposit = previous_state["stable_deposit_idle"]
    stable_deposit_yield_bearing: PCVDeposit = previous_state["stable_deposit_yield_bearing"]
    volatile_deposit_idle: PCVDeposit = previous_state["volatile_deposit_idle"]
    volatile_deposit_yield_bearing: PCVDeposit = previous_state["volatile_deposit_yield_bearing"]

    # The stable PCV ratio is the % of PCV value that is backed by stable assets
    stable_allocation = stable_pcv_ratio
    volatile_allocation = 1 - stable_pcv_ratio

    # The rebalancing strategy will move PCV assets between stable and volatile deposits,
    # to TRY make the current allocation meet the target allocation
    current_allocation = {
        "stable_asset": stable_allocation,
        "volatile_asset": volatile_allocation,
    }
    target_allocation = {
        "stable_asset": target_stable_pcv_ratio,
        "volatile_asset": (1 - target_stable_pcv_ratio),
    }

    # Calculate rebalancing conditions
    ratio_less_than_or_greater_than_target = target_rebalancing_condition(
        current_allocation["stable_asset"], target_allocation["stable_asset"]
    )
    timestep_equals_rebalancing_period = timestep % rebalancing_period / dt == 0

    if (
        # Rebalance towards target stable PCV ratio if either less than (lt, <) or greater than (gt, >) target,
        # according to target_rebalancing_condition parameter.
        ratio_less_than_or_greater_than_target
        and timestep_equals_rebalancing_period
    ):
        # Calculate required rebalancing between stable and volatile assets to meet the stable PCV ratio target
        stable_allocation_pct_change = (
            target_allocation["stable_asset"] - current_allocation["stable_asset"]
        )
        stable_asset_target_value_change = stable_allocation_pct_change * total_pcv
        total_stable_asset_balance_change = stable_asset_target_value_change / stable_asset_price

        volatile_allocation_pct_change = (
            target_allocation["volatile_asset"] - current_allocation["volatile_asset"]
        )
        volatile_asset_target_value_change = volatile_allocation_pct_change * total_pcv
        total_volatile_asset_balance_change = (
            volatile_asset_target_value_change / volatile_asset_price
        )

        pcv_deposit_rebalancing_strategy(
            volatile_asset_price=volatile_asset_price,
            stable_asset_price=stable_asset_price,
            volatile_deposit_idle=volatile_deposit_idle,
            volatile_deposit_yield_bearing=volatile_deposit_yield_bearing,
            stable_deposit_idle=stable_deposit_idle,
            stable_deposit_yield_bearing=stable_deposit_yield_bearing,
            total_stable_asset_balance_change=total_stable_asset_balance_change,
            total_volatile_asset_balance_change=total_volatile_asset_balance_change,
        )

    return {
        "stable_deposit_idle": stable_deposit_idle,
        "stable_deposit_yield_bearing": stable_deposit_yield_bearing,
        "volatile_deposit_idle": volatile_deposit_idle,
        "volatile_deposit_yield_bearing": volatile_deposit_yield_bearing,
    }


def pcv_deposit_rebalancing_strategy(
    volatile_asset_price: USD,
    stable_asset_price: USD,
    volatile_deposit_idle: PCVDeposit,
    volatile_deposit_yield_bearing: PCVDeposit,
    stable_deposit_idle: PCVDeposit,
    stable_deposit_yield_bearing: PCVDeposit,
    total_stable_asset_balance_change,
    total_volatile_asset_balance_change,
):
    """PCV Deposit Rebalancing Strategy

    See "PCV Rebalancing: Target Stable PCV Policy"

    Args:
        volatile_asset_price (USD): The volatile asset price
        stable_asset_price (USD): The stable asset price
        volatile_deposit_idle (PCVDeposit): The idle volatile asset PCV Deposit
        volatile_deposit_yield_bearing (PCVDeposit): The yield-bearing volatile asset PCV Deposit
        stable_deposit_idle (PCVDeposit): The idle stable asset PCV Deposit
        stable_deposit_yield_bearing (PCVDeposit): The yield-bearing stable asset PCV Deposit
        total_stable_asset_balance_change (_type_): The total stable asset balance change to meet target
        total_volatile_asset_balance_change (_type_): The total volatile asset balance change to meet target
    """
    # Rebalancing Strategy
    # PCV deposits in tranches / order of priority for rebalancing
    stable_pcv_deposits = [
        stable_deposit_idle,
        stable_deposit_yield_bearing,
    ]
    volatile_pcv_deposits = [
        volatile_deposit_idle,  # Try rebalance from idle assets first
        volatile_deposit_yield_bearing,  # Followed by any other PCV assets
    ]

    # PCV movement from volatile to stable
    if total_stable_asset_balance_change >= 0 and total_volatile_asset_balance_change < 0:
        balance_change = abs(total_volatile_asset_balance_change)
        # Try rebalance PCV from deposits in order of priority
        for deposit in volatile_pcv_deposits:
            if balance_change:
                if deposit.yield_rate > 0:
                    logging.warning("Cashing out of yield-bearing deposit")
                    # Transfer yield to deposit balance
                    deposit.transfer_yield(
                        to=deposit, amount=deposit.yield_accrued, asset_price=volatile_asset_price
                    )
                transfer_balance = min(balance_change, deposit.balance)
                # Transfer from stable PCV to volatile idle PCV deposit
                deposit.transfer(
                    to=stable_deposit_idle,
                    amount=transfer_balance,
                    from_asset_price=volatile_asset_price,
                    to_asset_price=stable_asset_price,
                )
                balance_change -= transfer_balance
            # Check if balance remainder
            if balance_change > 0:
                # TODO Additional constraints on movements and DCAing will be introduced in future,
                # for now we catch the edge case for further analysis
                logging.warning("Not enough balance across all sell side deposits to rebalance!")
    # PCV movement from stable to volatile
    else:
        balance_change = abs(total_stable_asset_balance_change)
        # Try rebalance PCV from deposits in order of priority
        for deposit in stable_pcv_deposits:
            if balance_change:
                if deposit.yield_rate > 0:
                    logging.warning("Cashing out of yield-bearing deposit")
                    # Transfer yield to deposit balance
                    deposit.transfer_yield(
                        to=deposit, amount=deposit.yield_accrued, asset_price=stable_asset_price
                    )
                transfer_balance = min(balance_change, deposit.balance)
                # Transfer from volatile PCV to stable idle PCV deposit
                deposit.transfer(
                    to=volatile_deposit_idle,
                    amount=transfer_balance,
                    from_asset_price=stable_asset_price,
                    to_asset_price=volatile_asset_price,
                )
                balance_change -= transfer_balance
        # Check if balance remainder
        if balance_change > 0:
            logging.warning("Not enough balance across all sell side deposits to rebalance!")
