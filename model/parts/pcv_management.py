"""PCV Management
"""

import logging
from model.types import (
    PCVDeposit,
    USD,
)
from model.system_parameters import Parameters


def policy_pcv_rebalancing_target_stable_pcv(params: Parameters, substep, state_history, previous_state):
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

    if (
        # TODO [readability] 2022-07-11: can we split this if-statement into two boolean variables
        #  such that we do: if flag1 and flag2: [...].
        #  Additionally, it is tough to understand what happens when we call target_rebalancing_condition()

        # Rebalance towards target stable PCV ratio if either less than (lt, <) or greater than (gt, >) target,
        # according to target_rebalancing_condition parameter.
        target_rebalancing_condition(
            current_allocation["stable_asset"], target_allocation["stable_asset"]
        )
        # and VOLATILITY_CONDITION
        # and/or WHATEVER_ELSE
        and timestep % rebalancing_period / dt == 0
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

        # NOTE Switch between rebalancing strategies here (e.g. v1, v2, ...)
        pcv_deposit_rebalancing_strategy_v2(
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


def pcv_deposit_rebalancing_strategy_v1(
    # TODO [documentation] 2022-07-11: add rationale about v1 and v2 functions in docstring, or cross reference with document
    volatile_asset_price: USD,
    stable_asset_price: USD,
    volatile_deposit_idle: PCVDeposit,
    volatile_deposit_yield_bearing: PCVDeposit,
    stable_deposit_idle: PCVDeposit,
    stable_deposit_yield_bearing: PCVDeposit,
    total_stable_asset_balance_change,
    total_volatile_asset_balance_change,
):

    # NOTE: unsure of how memory optimal it is to assign these to new variables by reference,
    # if one wanted to avoid doing this one could make the rebalancing section explicit for both cases

    # scenario where the policy must sell volatile asset and buy stable asset (increase stable PCV)
    if total_stable_asset_balance_change >= 0 and total_volatile_asset_balance_change < 0:

        # cast stable and volatile deposits into buy and sell side deposits depending
        # on sign of balance changes
        sell_side_balance_change = abs(total_volatile_asset_balance_change)
        buy_side_balance_change = total_stable_asset_balance_change

        sell_side_deposit_idle = volatile_deposit_idle
        sell_side_deposit_yield_bearing = volatile_deposit_yield_bearing
        buy_side_deposit_idle = stable_deposit_idle
        buy_side_deposit_yield_bearing = stable_deposit_yield_bearing

        sell_side_asset_price = volatile_asset_price
        buy_side_asset_price = stable_asset_price

    # scenario where the policy must sell stable asset and buy volatile asset (decrease stable PCV)
    else:

        # cast stable and volatile deposits into buy and sell side deposits depending
        # on sign of balance changes
        sell_side_balance_change = abs(total_stable_asset_balance_change)
        buy_side_balance_change = total_volatile_asset_balance_change

        sell_side_deposit_idle = stable_deposit_idle
        sell_side_deposit_yield_bearing = stable_deposit_yield_bearing
        buy_side_deposit_idle = volatile_deposit_idle
        buy_side_deposit_yield_bearing = volatile_deposit_yield_bearing

        sell_side_asset_price = stable_asset_price
        buy_side_asset_price = volatile_asset_price

    ################## PERFORM REBALANCING ################################

    # if the idle sell side deposit has enough balance
    if sell_side_deposit_idle.balance - sell_side_balance_change >= 0:

        print("DEBUG: only need idle deposits to rebalance")

        # withdraw from sell side asset idle deposit
        sell_side_deposit_idle.withdraw(amount=sell_side_balance_change, asset_price=sell_side_asset_price)

        # deposit the balance into idle buy side balance
        # implicitly: the sell side asset withdrawal perfectly finances the buy side asset deposit
        buy_side_deposit_idle.deposit(amount=buy_side_balance_change, asset_price=buy_side_asset_price)

    # if the idle volatile deposit does not by itself have enough balance for the sale
    else:

        print("DEBUG: cashing out of yield bearing deposits")

        # calculate difference between total amount to sell and idle deposit balance
        YB_balance_to_withdraw = sell_side_balance_change - sell_side_deposit_idle.balance
        assert YB_balance_to_withdraw > 0, "balance to withdraw is negative"

        # if the yield bearing deposit has enough balance for the remainder of the withdrawal to occur
        if sell_side_deposit_yield_bearing.balance - YB_balance_to_withdraw >= 0:

            # withdraw from sell side yield bearing deposit and deposit into sell side idle deposit
            # (can also use transfer() here)
            sell_side_deposit_yield_bearing.withdraw(amount=YB_balance_to_withdraw, asset_price=sell_side_asset_price)
            sell_side_deposit_idle.deposit(amount=YB_balance_to_withdraw, asset_price=sell_side_asset_price)

            # now the new balance of the sell side deposit should be == sell_side_balance_change
            # so the idle deposit has exactly the amount needed to rebalance
            sell_side_deposit_idle.withdraw(amount=sell_side_balance_change, asset_price=sell_side_asset_price)

            # deposit the balance into idle balance
            # implicitly: the volatile asset withdrawal perfectly finances the stable asset deposit
            buy_side_deposit_idle.deposit(amount=buy_side_balance_change, asset_price=buy_side_asset_price)

        # yield bearing + idle deposits no NOT have enough to perform the rebalance
        else:
            print("not enough balance across all sell side deposits to rebalance!")
            # this can either sell all remaining balance or perform additional operations
            # in practice, if a whole layer of DCA'ing into and out of positions happens this should
            # be unlikely to occur


def pcv_deposit_rebalancing_strategy_v2(
    # TODO [documentation] 2022-07-11: add rationale about v1 and v2 functions in docstring, or cross reference with document
    volatile_asset_price: USD,
    stable_asset_price: USD,
    volatile_deposit_idle: PCVDeposit,
    volatile_deposit_yield_bearing: PCVDeposit,
    stable_deposit_idle: PCVDeposit,
    stable_deposit_yield_bearing: PCVDeposit,
    total_stable_asset_balance_change,
    total_volatile_asset_balance_change,
):

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
                    deposit.transfer_yield(to=deposit, amount=deposit.yield_accrued, asset_price=volatile_asset_price)
                transfer_balance = min(balance_change, deposit.balance)
                # Transfer from stable PCV to volatile idle PCV deposit
                deposit.transfer(
                    to=stable_deposit_idle,
                    amount=transfer_balance,
                    from_asset_price=volatile_asset_price,
                    to_asset_price=stable_asset_price
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
                    deposit.transfer_yield(to=deposit, amount=deposit.yield_accrued, asset_price=stable_asset_price)
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
