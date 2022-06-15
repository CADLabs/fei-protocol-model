from model.types import FEI, PCVDeposit
from model.constants import wei, blocks_per_year


def policy_money_market(params, substep, state_history, previous_state):
    # Parameters
    dt = params["dt"]

    # State Variables
    fei_deposit_money_market: PCVDeposit = previous_state["fei_deposit_money_market"]
    balance = fei_deposit_money_market.balance
    borrowed: FEI = previous_state["fei_money_market_borrowed"]

    # TODO Placeholder dynamics: increase borrowed amount until 95% utilization (above kink of 80%)
    # borrowed amount is added to itself every period - linearly increasing up until the ceiling
    borrowed = min(balance * 0.95, borrowed + balance * 0.005)

    """Compound Jump Rate Model
    See parameters here:
    * https://etherscan.io/token/0x7713dd9ca933848f6819f38b8352d9a15ea73f67#readContract
    * https://etherscan.io/address/0xfb564da37b41b2f6b6edcc3e56fbf523bd9f2012#readContract

    See https://app.aave.com/reserve-overview/?underlyingAsset=0x956f47f50a910163d8bf957cf5846d573e7f87ca&marketName=proto_mainnet
    for validation.

    # For reference: Compound Standard Interest Rate Model
    ```
    base_rate = ...
    multiplier = ...
    borrowing_interest_rate = multiplier * utilization_rate + base_rate
    ```
    """
    # Calculate utilization rate
    # Assume Compound "reserves" or protocolSeizeShare of zero i.e. no profit taken
    cash = balance - borrowed
    reserves = 0
    utilization_rate = borrowed / (cash + borrowed - reserves) # == borrowed / balance

    # Calculate borrowing interest rate
    # TODO Move to parameters
    base_rate_per_block = 0
    multiplier_per_block = 23782343987 / wei
    jump_multiplier_per_block = 518455098934 / wei
    kink = 800000000000000000 / wei

    borrowing_interest_rate = (
        (
            multiplier_per_block * min(utilization_rate, kink)
            + jump_multiplier_per_block * max(0, utilization_rate - kink)
            + base_rate_per_block
        )
        * blocks_per_year
        * dt
    )

    # Calculate supply interest rate
    reserve_factor = 250000000000000000 / wei
    supply_interest_rate = borrowing_interest_rate * utilization_rate * (1 - reserve_factor)

    # State Update
    fei_deposit_money_market.yield_rate = supply_interest_rate

    return {
        "fei_deposit_money_market": fei_deposit_money_market,
        "fei_money_market_borrowed": borrowed,
        "fei_money_market_utilization": utilization_rate,
        "fei_money_market_borrow_rate": borrowing_interest_rate,
        "fei_money_market_supply_rate": supply_interest_rate,
    }
