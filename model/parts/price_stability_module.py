from model.system_parameters import Parameters
from model.types import FEI, USD, PCVDeposit, StateVariableKey, UserDeposit


def policy_price_stability_module(params: Parameters, substep, state_history, previous_state):
    # State Variables
    fei_minted_redeemed: FEI = previous_state["fei_minted_redeemed"]
    active_psm_pcv_deposit_key: StateVariableKey = previous_state["active_psm_pcv_deposit_key"]
    active_psm_pcv_deposit: PCVDeposit = previous_state[active_psm_pcv_deposit_key]
    fei_price: USD = previous_state["fei_price"]
    pcv_asset_price: USD = previous_state[active_psm_pcv_deposit.asset + "_asset_price"]

    # Check if PSM enabled
    if not active_psm_pcv_deposit_key:
        return {}
    else:
        # Perform minting and redemption
        # NOTE Assumes 100% of FEI minted/redeemed for purpose of liquidity pool rebalancing
        # TODO Account for minting and redemption fees
        mint_redeem_pcv_asset_balance = fei_minted_redeemed * fei_price / pcv_asset_price
        if mint_redeem_pcv_asset_balance >= 0:
            # Mint FEI for active PSM PCV Deposit asset
            active_psm_pcv_deposit.deposit(
                amount=mint_redeem_pcv_asset_balance, asset_price=pcv_asset_price
            )
        else:
            # Redeem FEI for active PSM PCV Deposit asset
            assert (
                abs(mint_redeem_pcv_asset_balance) < active_psm_pcv_deposit.balance
            ), "Insufficient PCV for redemption"
            active_psm_pcv_deposit.withdraw(
                amount=abs(mint_redeem_pcv_asset_balance), asset_price=pcv_asset_price
            )

        return {
            active_psm_pcv_deposit.key: active_psm_pcv_deposit,
        }
