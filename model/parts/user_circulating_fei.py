def update_total_user_circulating_fei(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update PCV stable backing value.
    """
    # DEBUG: magic number
    total_user_circulating_fei = 1e8
    return "total_user_circulating_fei", total_user_circulating_fei


def update_protocol_equity(
    params, substep, state_history, previous_state, policy_input
):
    """
    Update PCV stable backing value.
    """
    total_pcv_value = previous_state["total_pcv_value"]
    total_user_circulating_fei = previous_state["total_user_circulating_fei"]
    fei_price = previous_state["fei_price"]

    total_user_circulating_fei_value = total_user_circulating_fei * fei_price

    protocol_equity = total_pcv_value - total_user_circulating_fei_value

    return "protocol_equity", protocol_equity
