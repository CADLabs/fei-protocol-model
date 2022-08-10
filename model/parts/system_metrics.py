"""# System Metrics Module
Implementation of Policies for the calculation of various System Metrics and KPIs.
"""


def policy_system_metrics(params, substep, state_history, previous_state):
    """## System Metrics Policy
    Calculation of standard System Metrics such as the Stable Backing Ratio, Collateralization Ratio, etc.
    """
    # Parameters
    dt = params["dt"]

    # State Variables
    total_pcv = previous_state["total_pcv"]
    total_stable_asset_pcv = previous_state["total_stable_asset_pcv"]
    total_user_circulating_fei = previous_state["total_user_circulating_fei"]
    fei_price = previous_state["fei_price"]
    pcv_yield = previous_state["pcv_yield"]
    psm_mint_redeem_fees = previous_state["psm_mint_redeem_fees"]

    # PCV System Metrics
    stable_backing_ratio = total_stable_asset_pcv / total_user_circulating_fei
    stable_pcv_ratio = total_stable_asset_pcv / total_pcv
    collateralization_ratio = total_pcv / total_user_circulating_fei
    pcv_yield_rate = pcv_yield / total_pcv * 365 / dt

    # Protocol System Metrics
    protocol_equity = total_pcv - (total_user_circulating_fei * fei_price)
    protocol_revenue = pcv_yield + psm_mint_redeem_fees

    return {
        "stable_backing_ratio": stable_backing_ratio,
        "stable_pcv_ratio": stable_pcv_ratio,
        "collateralization_ratio": collateralization_ratio,
        "pcv_yield_rate": pcv_yield_rate,
        "protocol_equity": protocol_equity,
        "protocol_revenue": protocol_revenue,
    }
