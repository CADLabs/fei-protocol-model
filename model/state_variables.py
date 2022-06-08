"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

from numpy import NaN
import model.constants as constants
import model.system_parameters as system_parameters

from dataclasses import dataclass
from datetime import datetime
from model.types import (
    Uninitialized,
    Percentage,
    APY,
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
    """

    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # FEI Supply
    total_fei_supply: FEI = Uninitialized
    total_protocol_owned_fei: FEI = Uninitialized
    total_user_circulating_fei: FEI = 10_000_000  # DEBUG: magic number

    idle_user_circulating_fei: FEI = 0.0
    fei_minted_redeemed: FEI = 0.0
    cumulative_psm_redemptions: FEI = 0.0

    # Price Processes
    fei_price: USD = 1.0
    volatile_asset_price: USD = Uninitialized
    stable_asset_price: USD = Uninitialized

    # Liquidity Pools
    liquidity_pool_fei_balance: FEI = Uninitialized
    liquidity_pool_volatile_asset_balance: VolatileAssetUnits = Uninitialized
    # liquidity_pool_stable_asset_balance: StableAssetUnits = Uninitialized
    liquidity_pool_tvl: USD = Uninitialized
    liquidity_pool_fei_imbalance: FEI = 0.0

    # Money Markets
    fei_money_market_pcv_deposit: FEI = Uninitialized
    fei_money_market_borrowed: FEI = Uninitialized
    fei_money_market_lending_rate: APY = Uninitialized
    fei_money_market_utilization: Percentage = Uninitialized

    # FEI Savings Deposit
    fei_savings_deposit_balance: FEI = Uninitialized
    fei_savings_rate: APY = Uninitialized

    # 3rd party yield rates
    stable_asset_yield_rate: APY = Uninitialized
    volatile_asset_yield_rate: APY = Uninitialized

    # Protocol Owned FEI PCV
    idle_protocol_owned_fei_pcv_balance: FEI = Uninitialized
    idle_protocol_owned_fei_pcv: USD = Uninitialized

    # PCV Deposits
    # FEI
    fei_pcv_deposit_liquidity_pool_balance: FEI = Uninitialized
    fei_pcv_deposit_liquidity_pool: USD = Uninitialized

    fei_pcv_deposit_money_market_balance: FEI = Uninitialized
    fei_pcv_deposit_money_market: USD = Uninitialized

    # Stable Asset
    stable_asset_pcv_idle_balance: StableAssetUnits = 1e8  # DEBUG: magic number
    stable_asset_pcv_idle: USD = Uninitialized

    stable_asset_pcv_deposit_yield_bearing_balance: StableAssetUnits = 0
    stable_asset_pcv_deposit_yield_bearing: USD = Uninitialized

    # Volatile Asset
    volatile_asset_pcv_idle_balance: VolatileAssetUnits = 100_000  # DEBUG: magic number
    volatile_asset_pcv_idle: USD = Uninitialized

    volatile_asset_pcv_deposit_yield_bearing_balance: VolatileAssetUnits = 0
    volatile_asset_pcv_deposit_yield_bearing: USD = Uninitialized

    volatile_asset_pcv_deposit_liquidity_pool_balance: VolatileAssetUnits = 0
    volatile_asset_pcv_deposit_liquidity_pool: USD = Uninitialized

    # PCV Aggregates
    total_pcv: USD = Uninitialized
    total_stable_asset_pcv_balance: StableAssetUnits = Uninitialized
    total_volatile_asset_pcv_balance: VolatileAssetUnits = Uninitialized
    total_stable_asset_pcv: USD = Uninitialized
    total_volatile_asset_pcv: USD = Uninitialized

    stable_backing_ratio: Percentage = Uninitialized
    # volatile_backing_ratio: Percentage = Uninitialized

    collateralization_ratio: Percentage = Uninitialized
    protocol_equity: USD = Uninitialized

    # Assorted System Metrics
    fei_demand: float = Uninitialized


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
