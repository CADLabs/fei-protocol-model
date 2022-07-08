"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

from dataclasses import dataclass
from datetime import datetime
from model.types import (
    Uninitialized,
    Percentage,
    APR,
    USD,
    FEI,
    VolatileAssetUnits,
    StableAssetUnits,
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value

    See https://docs.google.com/spreadsheets/d/1LgqKEGRWaooWR6uD5X-vsOx2HBunfcGKJ58mX5rp7Z8/edit for derivation of
    FEI protocol model initial state / base case.
    """

    # Simulation
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # FEI Supply
    total_fei_supply: FEI = Uninitialized
    total_protocol_owned_fei: FEI = Uninitialized
    total_user_circulating_fei: FEI = Uninitialized

    # TODO: configure user-circulating FEI states
    idle_user_circulating_fei: FEI = 225_000_000
    fei_minted_redeemed: FEI = 0.0
    cumulative_psm_redemptions: FEI = 0.0

    # Price Processes
    fei_price: USD = 1.0
    volatile_asset_price: USD = 2_000
    stable_asset_price: USD = 1.0

    # Liquidity Pools
    liquidity_pool_invariant: float = Uninitialized
    liquidity_pool_tvl: USD = Uninitialized
    liquidity_pool_fei_source_sink: FEI = 0.0
    liquidity_pool_impermanent_loss: USD = 0.0
    liquidity_pool_trading_fees: USD = 0.0

    # Money Markets
    fei_money_market_borrowed: FEI = 0.0
    fei_money_market_utilization: Percentage = 0.0
    fei_money_market_borrow_rate: APR = 0.0
    fei_money_market_supply_rate: APR = 0.0
    """FEI Money Market Supply Rate
    Current yield for supply of FEI is quite low,
    historically 3% may be a good base case to parametrise borrow / utilization.
    
    See:
    * https://dune.com/queries/394975/753736
    * https://app.aave.com/
    * https://app.compound.finance/
    """

    # FEI Savings Deposit
    # TODO Account for wrapped yield-bearing FEI supply
    fei_savings_deposit_balance: FEI = 0.0
    fei_savings_rate: APR = Uninitialized

    # PCV Aggregates
    total_pcv: USD = Uninitialized
    total_stable_asset_pcv_balance: StableAssetUnits = Uninitialized
    total_volatile_asset_pcv_balance: VolatileAssetUnits = Uninitialized
    total_stable_asset_pcv: USD = Uninitialized
    total_volatile_asset_pcv: USD = Uninitialized

    # PCV Metrics
    stable_pcv_ratio: Percentage = Uninitialized
    collateralization_ratio: Percentage = Uninitialized
    protocol_equity: USD = Uninitialized

    # Assorted System Metrics
    fei_demand: float = Uninitialized


initial_state = StateVariables().__dict__
