"""Money Markets
"""

from model.types import FEI, PCVDeposit
from model.constants import wei, blocks_per_year
from model.system_parameters import Parameters


def policy_money_market(params: Parameters, substep, state_history, previous_state):
    """Money Market Policy
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

    # State Variables
    fei_deposit_money_market: PCVDeposit = previous_state["fei_deposit_money_market"]
    balance = fei_deposit_money_market.balance
    borrowed: FEI = previous_state["fei_money_market_borrowed"]

    # TODO Replace placeholder dynamics
    # Borrowed amount increases linearly until 95% utilization (above kink of 80%)
    borrowed = min(balance * 0.95, borrowed + balance * 0.005)

    # Compound Jump Rate Model
    # Calculate utilization rate
    # Assume Compound "reserves" or protocolSeizeShare of zero i.e. no profit taken
    cash = balance - borrowed
    reserves = 0  # placeholder
    utilization_rate = borrowed / (cash + borrowed - reserves)  # == borrowed / balance

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
    # Calculate effective yield rate on total PCVDeposit balance
    fei_deposit_money_market.yield_rate = utilization_rate * supply_interest_rate

    return {
        "fei_deposit_money_market": fei_deposit_money_market,
        "fei_money_market_borrowed": borrowed,
        "fei_money_market_utilization": utilization_rate,
        "fei_money_market_borrow_rate": borrowing_interest_rate,
        "fei_money_market_supply_rate": supply_interest_rate,
    }
