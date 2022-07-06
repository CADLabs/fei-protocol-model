"""System Metrics
"""


def policy_pcv_metrics(params, substep, state_history, previous_state):
    # State Variables
    total_pcv = previous_state["total_pcv"]
    total_stable_asset_pcv = previous_state["total_stable_asset_pcv"]
    total_user_circulating_fei = previous_state["total_user_circulating_fei"]
    fei_price = previous_state["fei_price"]

    # State Update
    stable_backing_ratio = total_stable_asset_pcv / total_user_circulating_fei
    stable_pcv_ratio = total_stable_asset_pcv / total_pcv
    collateralization_ratio = total_pcv / total_user_circulating_fei
    protocol_equity = total_pcv - (total_user_circulating_fei * fei_price)

    return {
        "stable_backing_ratio": stable_backing_ratio,
        "stable_pcv_ratio": stable_pcv_ratio,
        "collateralization_ratio": collateralization_ratio,
        "protocol_equity": protocol_equity,
    }
