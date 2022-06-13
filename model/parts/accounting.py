def policy_accounting(params, substep, state_history, previous_state):
    # State Variables
    fei_deposit_idle = previous_state["fei_deposit_idle"]
    fei_deposit_liquidity_pool = previous_state["fei_deposit_liquidity_pool"]

    # State Update
    total_protocol_owned_fei = fei_deposit_idle.balance + fei_deposit_liquidity_pool.balance

    # TODO: configure user-circulating FEI states
    # idle_user_circulating_fei = previous_state["idle_user_circulating_fei"]
    # fei_savings_deposit_balance = previous_state["fei_savings_deposit_balance"]
    total_user_circulating_fei = previous_state["total_user_circulating_fei"]

    total_fei_supply = total_protocol_owned_fei + total_user_circulating_fei

    return {
        "total_protocol_owned_fei": total_protocol_owned_fei,
        "total_user_circulating_fei": total_user_circulating_fei,
        "total_fei_supply": total_fei_supply,
    }
