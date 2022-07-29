"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from model.types import (
    StateVariableKey,
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
    fei_minted_redeemed: FEI = 0.0
    active_psm_pcv_deposit_key: StateVariableKey = "stable_idle_pcv_deposit"

    # Price Processes
    fei_price: USD = 1.0
    volatile_asset_price: USD = 2_000
    stable_asset_price: USD = 1.0

    # Liquidity Pools
    # NOTE Total liquidity pool metrics including both protocol- and user-supplied liquidity
    liquidity_pool_invariant: float = Uninitialized
    liquidity_pool_tvl: USD = Uninitialized
    liquidity_pool_fei_source_sink: FEI = 0.0
    liquidity_pool_impermanent_loss: USD = 0.0
    liquidity_pool_trading_fees: USD = 0.0
    total_liquidity_pool_trading_fees: USD = 0.0

    # Money Markets
    fei_money_market_borrowed: FEI = Uninitialized
    fei_money_market_utilization: Percentage = Uninitialized
    fei_money_market_borrow_rate: APR = 0.0
    fei_money_market_supply_rate: APR = 0.0
    """FEI Money Market Supply Rate
    Current yield for supply of FEI is quite low,
    historically 3% may be a good base case to parameterise borrow / utilization.
    
    See:
    * https://dune.com/queries/394975/753736
    * https://app.aave.com/
    * https://app.compound.finance/
    """

    # FEI Savings Deposit
    fei_savings_rate: APR = Uninitialized

    # PCV Aggregates
    total_pcv: USD = Uninitialized
    total_stable_asset_pcv_balance: StableAssetUnits = Uninitialized
    total_volatile_asset_pcv_balance: VolatileAssetUnits = Uninitialized
    total_stable_asset_pcv: USD = Uninitialized
    total_volatile_asset_pcv: USD = Uninitialized

    # PCV Metrics
    stable_backing_ratio: Percentage = Uninitialized
    stable_pcv_ratio: Percentage = Uninitialized
    collateralization_ratio: Percentage = Uninitialized
    protocol_equity: USD = Uninitialized
    pcv_yield: Percentage = Uninitialized
    pcv_yield_rate: Percentage = Uninitialized

    # User-circulating FEI Capital Allocation Model
    capital_allocation_target_weights: np.ndarray = Uninitialized
    capital_allocation_rebalance_matrix: np.ndarray = field(default_factory=dict)
    capital_allocation_rebalance_remainder: FEI = Uninitialized

    # Assorted System Metrics
    fei_demand: float = Uninitialized


initial_state = StateVariables().__dict__
