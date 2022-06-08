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

    """
    MODEL ASSUMPTION: At the highest level, we are interested in rebalancing between two assets only,
    stable and volatile. In practice, this is of interest for the policy.
    When it comes to subdividing the total amount to be rebalanced it is more opportune to deal with
    'internal' weights than to consider each deposit type as its own asset type - which is de facto
    the case once the target allocation has more than two values.
    
    Formally, W_S + W_V = 1, where W_S = W_S,I + W_S,Y and W_V = W_V,I + W_V,Y.
    """

    target_allocation = {
        "stable_asset": 0.5,
        "volatile_asset": 0.5,
    }

    # ASSUMPTION: arbitrarily make all rebalancing changes to idle PCV deposits only
    stable_asset_internal_weights = {
        "idle": 1.0,
        "yield_bearing": 0.0,
    }
    volatile_asset_internal_weights = {
        "idle": 1.0,
        "yield_bearing": 0.0,
    }

    # How much of each asset out of each deposit type to buy/sell in total after the policy has evaluated
    stable_asset_target_amount_change = {
        "idle": 0.0,
        "yield_bearing": 0.0,
    }
    volatile_asset_target_amount_change = {
        "idle": 0.0,
        "yield_bearing": 0.0,
    }

    # Condition of being under-backed by stable asset
    if (
        current_allocation["stable_asset"] < target_allocation["stable_asset"]
        # and VOLATILITY_CONDITION
        # and/or WHATEVER_ELSE
        and timestep % rebalancing_period == 0
    ):
        # calculate total amount of stable and volatile asset to rebalance
        stable_allocation_pct_change = (
            target_allocation["stable_asset"] - current_allocation["stable_asset"]
        )

        stable_asset_target_value_change = stable_allocation_pct_change * total_pcv
        total_required_stable_asset_change = (
            stable_asset_target_value_change / stable_asset_price
        )

        volatile_allocation_pct_change = (
            target_allocation["volatile_asset"] - current_allocation["volatile_asset"]
        )

        volatile_asset_target_value_change = volatile_allocation_pct_change * total_pcv
        total_required_volatile_asset_change = (
            volatile_asset_target_value_change / volatile_asset_price
        )

        # split allocation of amount to rebalance between existing deposit types
        stable_asset_target_amount_change["idle"] = (
            total_required_stable_asset_change * stable_asset_internal_weights["idle"]
        )
        stable_asset_target_amount_change["yield_bearing"] = (
            total_required_stable_asset_change
            * stable_asset_internal_weights["yield_bearing"]
        )

        volatile_asset_target_amount_change["idle"] = (
            total_required_volatile_asset_change
            * volatile_asset_internal_weights["idle"]
        )

        volatile_asset_target_amount_change["yield_bearing"] = (
            total_required_volatile_asset_change
            * volatile_asset_internal_weights["yield_bearing"]
        )

    """
    Should use value weights to attempt to answer - based on the current weighting in
    value for stable and volatile assets, what quantity of each asset: volatile / stable
    needs to be bought / sold to achieve new target weights?

    Can encode the concept of a stable weights target (long term stable backing) and a
    max per-period target since shifts that are too big would cause jumps / instability - need to DCA
    out of and into assets

    volatility + asset allocation deviation - based asset value rebalancing
    """

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
    total_stable_asset_pcv = total_stable_asset_pcv_balance * stable_asset_price
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
    pcv_balance = (
        previous_state["stable_asset_pcv_idle_balance"]
        + previous_state["stable_asset_pcv_deposit_yield_bearing_balance"]
    )

    return "total_stable_asset_pcv_balance", pcv_balance  # + target_amount_change


def update_total_volatile_asset_pcv_balance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update total volatile asset PCV balance
    """
    pcv_balance = (
        previous_state["volatile_asset_pcv_idle_balance"]
        + previous_state["volatile_asset_pcv_deposit_yield_bearing_balance"]
        + previous_state["volatile_asset_pcv_deposit_liquidity_pool_balance"]
    )

    return "total_volatile_asset_pcv_balance", pcv_balance  # + target_amount_change


def update_stable_asset_idle_pcv_from_rebalance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update idle stable asset PCV balance
    """
    # ASSUMPTION: is changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["stable_asset_pcv_idle_balance"]
    target_amount_change = policy_input["stable_asset_target_amount_change"]["idle"]

    return "stable_asset_pcv_idle_balance", pcv_balance + target_amount_change


def update_stable_asset_yield_bearing_pcv_from_rebalance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update yield bearing stable asset PCV balance
    """
    # ASSUMPTION: is changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["stable_asset_pcv_deposit_yield_bearing_balance"]
    target_amount_change = policy_input["stable_asset_target_amount_change"][
        "yield_bearing"
    ]

    return (
        "stable_asset_pcv_deposit_yield_bearing_balance",
        pcv_balance + target_amount_change,
    )


def update_volatile_asset_idle_pcv_from_rebalance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update idle volatile asset PCV balance
    """
    # ASSUMPTION: is changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["volatile_asset_pcv_idle_balance"]
    target_amount_change = policy_input["volatile_asset_target_amount_change"]["idle"]

    return "volatile_asset_pcv_idle_balance", pcv_balance + target_amount_change


def update_volatile_asset_yield_bearing_pcv_from_rebalance(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update yield bearing volatile asset PCV balance
    """
    # ASSUMPTION: is changed at the constituent level
    # DEBUG: placeholder dynamics
    pcv_balance = previous_state["volatile_asset_pcv_deposit_yield_bearing_balance"]
    target_amount_change = policy_input["volatile_asset_target_amount_change"][
        "yield_bearing"
    ]

    return (
        "volatile_asset_pcv_deposit_yield_bearing_balance",
        pcv_balance + target_amount_change,
    )
