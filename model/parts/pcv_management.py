def policy_pcv_rebalancing(params, substep, state_history, previous_state):
    """
    Emulates money market rate. supply_from_88mph, pool_supply and pool_borrow  are the three parameters.

    """
    # DEBUG: placeholder dynamics - buy/sell x% based on stable/volatile asset amount at previous
    # timestep. Based on a period rebalance target. Does not calculate monetary expenditure.
    
    # PSEUDO:
    # if good market conditions stable asset target is decreased
    # if good market conditions volatile asset target is increased
    # if bad market conditions stable asset target is increased
    # if bad market conditions volatile asset target is decreased
    
    # MODEL: does this policy need to be called after all these values are calculated?
    cr = previous_state['collateralization_ratio']
    volatile_asset_price = previous_state['volatile_asset_price']
    stable_asset_price = previous_state['stable_asset_price']
    total_volatile_asset_pcv_value = previous_state['total_volatile_asset_pcv_value']
    total_stable_asset_pcv_value = previous_state['total_stable_asset_pcv_value']

    # should use value weights to attempt to answer - based on the current weighting in
    # value for stable and volatile assets, what quantity of each asset: volatile / stable
    # needs to be bought / sold to achieve new target weights?
    
    # can encode the concept of a stable weights target (long term stable backing) and a
    # max per-period target since shifts that are too big would cause jumps / instability - need to DCA
    # out of and into assets
    
    # NB: these are NOT weights
    return {
        "stable_asset_pcv_target_change": 0.001,
        "volatile_asset_pcv_target_change": -0.001,
    }


def update_total_stable_asset_pcv_amount(params, substep, state_history, previous_state, policy_input):
    """
    Update total stable asset PCV amount.
    """
    # ASSUMPTION: can directly change the total amount. more realistically
    # needs to be changed at the constituent level
    # DEBUG: placeholder dynamics
    pct_target = policy_input['stable_asset_pcv_target_change']
    total_stable_asset_pcv_amount = previous_state['total_stable_asset_pcv_amount'] * (1 + pct_target)
    
    return "total_stable_asset_pcv_amount", total_stable_asset_pcv_amount


def update_total_volatile_asset_pcv_amount(params, substep, state_history, previous_state, policy_input):
    """
    Update total volatile asset PCV amount.
    """
    # ASSUMPTION: can directly change the total amount. more realistically
    # needs to be changed at the constituent level
    # DEBUG: placeholder dynamics
    pct_target = policy_input['volatile_asset_pcv_target_change']
    total_volatile_asset_pcv_amount = previous_state['total_volatile_asset_pcv_amount'] * (1 + pct_target)
    
    return "total_volatile_asset_pcv_amount", total_volatile_asset_pcv_amount


def update_total_stable_asset_pcv_value(params, substep, state_history, previous_state, policy_input):
    """
    Update total stable asset PCV value.
    """
    total_stable_asset_pcv_amount = previous_state['total_stable_asset_pcv_amount']
    stable_asset_price = previous_state['stable_asset_price']

    total_stable_asset_pcv_value = total_stable_asset_pcv_amount * stable_asset_price
    return "total_stable_asset_pcv_value", total_stable_asset_pcv_value


def update_total_volatile_asset_pcv_value(params, substep, state_history, previous_state, policy_input):
    """
    Update total volatile asset PCV value.
    """
    total_volatile_asset_pcv_amount = previous_state['total_volatile_asset_pcv_amount']
    volatile_asset_price = previous_state['volatile_asset_price']

    total_volatile_asset_pcv_value = total_volatile_asset_pcv_amount * volatile_asset_price
    return "total_volatile_asset_pcv_value", total_volatile_asset_pcv_value


def update_total_pcv_value(params, substep, state_history, previous_state, policy_input):
    """
    Update total volatile asset PCV value.
    """
    total_volatile_asset_pcv_value = previous_state['total_volatile_asset_pcv_value']
    total_stable_asset_pcv_value = previous_state['total_stable_asset_pcv_value']

    total_pcv_value = total_volatile_asset_pcv_value + total_stable_asset_pcv_value
    return "total_pcv_value", total_pcv_value


def update_stable_backing_ratio(params, substep, state_history, previous_state, policy_input):
    """
    Update PCV stable backing value.
    """
    total_volatile_asset_pcv_value = previous_state['total_volatile_asset_pcv_value']
    total_stable_asset_pcv_value = previous_state['total_stable_asset_pcv_value']

    stable_backing_ratio = total_stable_asset_pcv_value / (total_volatile_asset_pcv_value + total_stable_asset_pcv_value)
    return "stable_backing_ratio", stable_backing_ratio


def update_collateralization_ratio(params, substep, state_history, previous_state, policy_input):
    """
    Update PCV stable backing value.
    """
    total_user_circulating_fei = previous_state['total_user_circulating_fei']
    total_volatile_asset_pcv_value = previous_state['total_volatile_asset_pcv_value']
    total_stable_asset_pcv_value = previous_state['total_stable_asset_pcv_value']

    total_pcv_value = total_volatile_asset_pcv_value + total_stable_asset_pcv_value

    collateralization_ratio = total_pcv_value / total_user_circulating_fei
    return "collateralization_ratio", collateralization_ratio
