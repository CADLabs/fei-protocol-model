"""# Peg Stability Module
Implementation of Peg Stability Module related Policies.
"""

from typing import List
import logging
from model.system_parameters import Parameters
from model.types import FEI, USD, PCVDeposit, StateVariableKey


def policy_peg_stability_module(params: Parameters, substep, state_history, previous_state):
    """## Peg Stability Module Policy
    Currently the primary purpose of the Peg Stability Module is for the increase and reduction of PCV due to minting, redemption, and PSM fees.

    The System Parameter `active_psm_pcv_deposit_keys` sets the currently active PCV Deposit for the purpose of minting and redemption.
    See relevant parameter docstring for more details.

    See https://docs.tribedao.xyz/docs/protocol/Mechanism/PegStabilityModule
    """
    # Parameters
    psm_mint_fee = params["psm_mint_fee"]
    psm_redeem_fee = params["psm_redeem_fee"]

    # State Variables
    fei_minted_redeemed: FEI = previous_state["fei_minted_redeemed"]
    active_psm_pcv_deposit_keys: List[StateVariableKey] = previous_state[
        "active_psm_pcv_deposit_keys"
    ]
    active_psm_pcv_deposits: List[PCVDeposit] = [
        previous_state[key] for key in active_psm_pcv_deposit_keys
    ]
    fei_price: USD = previous_state["fei_price"]

    psm_mint_redeem_fees: USD = 0

    # Check if PSM enabled
    if not active_psm_pcv_deposit_keys:
        logging.warning("No active PSM PCV Deposit set!")
        return {}
    else:
        # Perform minting and redemption
        if fei_minted_redeemed >= 0:
            # Minting: select first active PSM PCV Deposit
            active_psm_pcv_deposit: PCVDeposit = active_psm_pcv_deposits[0]
            pcv_asset_price: USD = previous_state[active_psm_pcv_deposit.asset + "_asset_price"]
            mint_redeem_pcv_asset_balance = fei_minted_redeemed * fei_price / pcv_asset_price
            # Mint FEI for active PSM PCV Deposit asset
            active_psm_pcv_deposit.deposit(
                amount=mint_redeem_pcv_asset_balance, asset_price=pcv_asset_price
            )
            # Collect PSM mint fees
            psm_mint_redeem_fees = psm_mint_fee * fei_minted_redeemed
        else:
            # Redeeming: select first eligible (i.e. with enough balance) active PSM PCV Deposit
            eligible_active_psm_pcv_deposits: PCVDeposit = [
                deposit
                for deposit in active_psm_pcv_deposits
                if deposit.balance
                >= abs(
                    fei_minted_redeemed * fei_price / previous_state[deposit.asset + "_asset_price"]
                )
            ]
            if eligible_active_psm_pcv_deposits:
                active_psm_pcv_deposit = eligible_active_psm_pcv_deposits[0]
                pcv_asset_price: USD = previous_state[active_psm_pcv_deposit.asset + "_asset_price"]
                mint_redeem_pcv_asset_balance = fei_minted_redeemed * fei_price / pcv_asset_price
                # Redeem FEI for active PSM PCV Deposit asset
                assert (
                    abs(mint_redeem_pcv_asset_balance) < active_psm_pcv_deposit.balance
                ), "Insufficient PCV for redemption"
                active_psm_pcv_deposit.withdraw(
                    amount=abs(mint_redeem_pcv_asset_balance),
                    asset_price=pcv_asset_price,
                )
                # Collect PSM redeem fees
                psm_mint_redeem_fees = psm_redeem_fee * abs(fei_minted_redeemed)
            else:
                raise Exception("Insufficient PCV for redemption")

        return {
            active_psm_pcv_deposit.key: active_psm_pcv_deposit,
            "psm_mint_redeem_fees": psm_mint_redeem_fees,
        }
