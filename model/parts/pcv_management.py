def policy_pcv_rebalancing(params, substep, state_history, previous_state):
    """
    DEBUG: placeholder dynamics - buy/sell x% based on stable/volatile asset amount at previous
    timestep. Based on a period rebalance target. Does not calculate monetary expenditure.

    PSEUDO:
    if good market conditions stable asset target is decreased
    if good market conditions volatile asset target is increased
    if bad market conditions stable asset target is increased
    if bad market conditions volatile asset target is decreased

    MODEL: does this policy need to be called after all these values are calculated?
    """

    total_pcv = previous_state["total_pcv"]
    stable_backing_ratio = previous_state["stable_backing_ratio"]

    volatile_asset_price = previous_state["volatile_asset_price"]
    stable_asset_price = previous_state["stable_asset_price"]

    dt = params["dt"]
    timestep = previous_state["timestep"]

    # Arbitrarily rebalance every X periods
    rebalancing_period = 50 * dt

    # The stable backing ratio is what % of PCV value is backed by stable assets
    # in this two-asset model this is the same thing as the % weight of stables for PCV
    stable_allocation = stable_backing_ratio
    volatile_allocation = 1 - stable_backing_ratio

    current_allocation = {
        "stable_asset": stable_allocation,
        "volatile_asset": volatile_allocation,
    }

    target_allocation = {
        "stable_asset": 0.5,
        "volatile_asset": 0.5,
    }

    # How much of each asset to buy/sell after the policy has evaluated
    stable_asset_target_amount_change = 0.0
    volatile_asset_target_amount_change = 0.0

    # Condition of being under-backed by stable asset
    if (
        current_allocation["stable_asset"] < target_allocation["stable_asset"]
        # and VOLATILITY_CONDITION
        # and/or WHATEVER_ELSE
        and timestep % rebalancing_period == 0
    ):
        stable_allocation_pct_change = (
            target_allocation["stable_asset"] - current_allocation["stable_asset"]
        )
        stable_asset_target_value_change = stable_allocation_pct_change * total_pcv
        stable_asset_target_amount_change = (
            stable_asset_target_value_change / stable_asset_price
        )

        volatile_allocation_pct_change = (
            target_allocation["volatile_asset"] - current_allocation["volatile_asset"]
        )
        volatile_asset_target_value_change = volatile_allocation_pct_change * total_pcv
        volatile_asset_target_amount_change = (
            volatile_asset_target_value_change / volatile_asset_price
        )

    # Should use value weights to attempt to answer - based on the current weighting in
    # value for stable and volatile assets, what quantity of each asset: volatile / stable
    # needs to be bought / sold to achieve new target weights?

    # Can encode the concept of a stable weights target (long term stable backing) and a
    # max per-period target since shifts that are too big would cause jumps / instability - need to DCA
    # out of and into assets

    # volatility + asset allocation deviation - based asset value rebalancing

    return {
        "stable_asset_target_amount_change": stable_asset_target_amount_change,  # NB: these are NOT weights
        "volatile_asset_target_amount_change": volatile_asset_target_amount_change,
    }


def policy_pcv_accounting(params, substep, state_history, previous_state):
    # State Variables
    total_user_circulating_fei = previous_state["total_user_circulating_fei"]
    total_stable_asset_pcv_balance = previous_state["total_stable_asset_pcv_balance"]
    total_volatile_asset_pcv_balance = previous_state[
        "total_volatile_asset_pcv_balance"
    ]

    fei_price = previous_state["fei_price"]
    stable_asset_price = previous_state["stable_asset_price"]
    volatile_asset_price = previous_state["volatile_asset_price"]

    # Accounting
    total_stable_asset_pcv = total_stable_asset_pcv_balance + stable_asset_price
    total_volatile_asset_pcv = total_volatile_asset_pcv_balance * volatile_asset_price
    total_pcv = total_volatile_asset_pcv + total_stable_asset_pcv

    return {
        "total_pcv": total_pcv,
        "total_stable_asset_pcv": total_stable_asset_pcv,
        "total_volatile_asset_pcv": total_volatile_asset_pcv,
        "protocol_equity": total_pcv - (total_user_circulating_fei * fei_price),
        "stable_backing_ratio": total_stable_asset_pcv / total_pcv,
        "collateralization_ratio": total_pcv / total_user_circulating_fei,
    }


def update_total_stable_asset_pcv_balance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update total stable asset PCV balance
    """
    # ASSUMPTION: can directly change the total amount. more realistically
    # needs to be changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["total_stable_asset_pcv_balance"]
    target_amount_change = policy_input["stable_asset_target_amount_change"]

    return "total_stable_asset_pcv_balance", pcv_balance + target_amount_change


def update_total_volatile_asset_pcv_balance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update total volatile asset PCV balance
    """
    # ASSUMPTION: can directly change the total amount. more realistically
    # needs to be changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["total_volatile_asset_pcv_balance"]
    target_amount_change = policy_input["volatile_asset_target_amount_change"]

    return "total_volatile_asset_pcv_balance", pcv_balance + target_amount_change
