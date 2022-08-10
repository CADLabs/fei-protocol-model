"""# Money Markets Module
A module with a single Policy that implements a generic Compound style Money Market
to model the FEI Savings Rate competing yield opportunity that exists for the FEI token.
"""

import numpy as np
import pandas as pd

from model.types import PCVDeposit, Timestep, UserDeposit
from model.constants import blocks_per_year
from model.system_parameters import Parameters


def policy_money_market(params: Parameters, substep, state_history, previous_state):
    """## Money Market Policy
    The Compound lending market "Compound Jump Rate Model", shared by a number of lending markets including Aave,
    is used as a proxy for all lending markets in this model.

    See parameters here:
    * https://etherscan.io/token/0x7713dd9ca933848f6819f38b8352d9a15ea73f67#readContract
    * https://etherscan.io/address/0xfb564da37b41b2f6b6edcc3e56fbf523bd9f2012#readContract

    See https://app.aave.com/reserve-overview/?underlyingAsset=0x956f47f50a910163d8bf957cf5846d573e7f87ca&marketName=proto_mainnet
    for validation of output.

    ## Compound Standard Interest Rate Model (for reference)
    ```
    base_rate = ...
    multiplier = ...
    borrowing_interest_rate = multiplier * utilization_rate + base_rate
    ```
    """
    # Parameters
    dt = params["dt"]
    base_rate_per_block = params["base_rate_per_block"]
    multiplier_per_block = params["multiplier_per_block"]
    jump_multiplier_per_block = params["jump_multiplier_per_block"]
    kink = params["money_market_kink"]
    reserve_factor = params["money_market_reserve_factor"]
    money_market_utilization_rate_process = params["money_market_utilization_rate_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    fei_money_market_pcv_deposit: PCVDeposit = previous_state["fei_money_market_pcv_deposit"]
    fei_money_market_user_deposit: UserDeposit = previous_state["fei_money_market_user_deposit"]

    # Calculate total money market balance as combination of protocol- and user-supplied FEI
    balance = fei_money_market_pcv_deposit.balance + fei_money_market_user_deposit.balance

    # Get volatile asset (va) price series
    va_price_series = pd.Series(substate[-1]["volatile_asset_price"] for substate in state_history)

    # Volatile asset price trend risk metric = price slope / average price
    va_price_mean = (
        previous_state["volatile_asset_price_mean"] * (timestep - 1)
        + previous_state["volatile_asset_price"]
    ) / timestep
    time_window: Timestep = params["volatile_asset_risk_metric_time_window"]
    va_price_slope = (
        np.polyfit(
            range(len(va_price_series[-min(timestep, time_window) : -1])),
            va_price_series[-min(timestep, time_window) : -1],
            1,
        )[0]
        if timestep > 2
        else 0
    )
    va_risk_metric = -va_price_slope / va_price_mean
    # Min-max normalization
    va_risk_metric_min = min(va_risk_metric, previous_state["volatile_asset_risk_metric_min"])
    va_risk_metric_max = max(va_risk_metric, previous_state["volatile_asset_risk_metric_max"])
    va_risk_metric = (
        (va_risk_metric - va_risk_metric_min) / (va_risk_metric_max - va_risk_metric_min)
        if va_risk_metric_max - va_risk_metric_min
        else va_risk_metric
    )
    va_risk_metric = np.nan_to_num(va_risk_metric, posinf=0, neginf=0)

    # Utilization rate stochastic process:
    # NOTE As an extension, can introduce a lag in the process
    max_risk_discount = 0.5
    utilization_rate = money_market_utilization_rate_process(run, timestep) * (
        1 - max_risk_discount * va_risk_metric
    )  # At peak risk, set to max_risk_discount % of utilization rate
    borrowed = balance * utilization_rate

    # Borrowing driven utilization rate:
    # borrowed = money_market_borrowed_process(run, timestep)
    # cash = balance - borrowed
    # Assume Compound "reserves" or protocolSeizeShare of zero i.e. no profit taken
    # reserves = 0
    # utilization_rate = borrowed / (cash + borrowed - reserves)  # == borrowed / balance

    # Calculate borrowing interest rate
    # To be consistent with the smart contract configuration,
    # per-block parameters are used with the interest rate converted to a yearly rate
    borrowing_interest_rate = (
        (
            multiplier_per_block * min(utilization_rate, kink)
            + jump_multiplier_per_block * max(0, utilization_rate - kink)
            + base_rate_per_block
        )  # total reward per block
        * blocks_per_year
        * dt
    )

    # Calculate supply interest rate
    supply_interest_rate = borrowing_interest_rate * utilization_rate * (1 - reserve_factor)

    # State Update
    # Calculate effective yield rate on total balance
    effective_yield_rate = utilization_rate * supply_interest_rate
    fei_money_market_pcv_deposit.yield_rate = effective_yield_rate
    fei_money_market_user_deposit.yield_rate = effective_yield_rate

    return {
        "volatile_asset_risk_metric": va_risk_metric,
        "volatile_asset_risk_metric_min": va_risk_metric_min,
        "volatile_asset_risk_metric_max": va_risk_metric_max,
        "volatile_asset_price_mean": va_price_mean,
        "fei_money_market_pcv_deposit": fei_money_market_pcv_deposit,
        "fei_money_market_user_deposit": fei_money_market_user_deposit,
        "fei_money_market_borrowed": borrowed,
        "fei_money_market_utilization": utilization_rate,
        "fei_money_market_borrow_rate": borrowing_interest_rate,
        "fei_money_market_supply_rate": supply_interest_rate,
    }
