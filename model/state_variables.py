"""# State Variables
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import numpy as np
from model.types import (
    UNI,
    StateVariableKey,
    Uninitialized,
    Percentage,
    APR,
    USD,
    FEI,
    VolatileAssetUnits,
    StableAssetUnits,
)
from model.utils import default


@dataclass
class StateVariables:
    """## State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Simulation
    timestamp: datetime = None
    """The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter."""

    # FEI Supply
    total_fei_supply: FEI = Uninitialized
    """
    The total FEI supply including both protocol-owned and user-circulating FEI.

    Updated in `model.parts.accounting`.
    """

    total_protocol_owned_fei: FEI = Uninitialized
    """
    The total protocol-owned FEI supply.

    Updated in `model.parts.accounting`.
    """

    total_user_circulating_fei: FEI = Uninitialized
    """
    The total user-circulating FEI supply.

    Updated in `model.parts.accounting`.
    """

    fei_minted_redeemed: FEI = 0.0
    """
    The net amount of FEI minted (+ve) or redeemed (-ve) at each timestep
    for the purpose of Liquidity Pool rebalancing. 

    Updated in `model.parts.liquidity_pools`.
    """

    active_psm_pcv_deposit_keys: List[StateVariableKey] = default(
        [
            # In order of priority:
            "stable_idle_pcv_deposit",
            "volatile_idle_pcv_deposit",
            "volatile_yield_bearing_pcv_deposit",
        ]
    )
    """
    A list of PCV Deposit State Variable keys actively used by the PSM for minting and redemption.
    PCV Deposits are in order of priority - i.e. if one PCV Deposit is depleted, the next PCV Deposit is tried,
    and if no PCV Deposit balance is available for redemption, the simulation will fail.

    This list can be set by a Policy, for example setting to Volatile Asset PCV Deposits to only redeem for ETH in a market downturn.
    """

    psm_mint_redeem_fees: USD = Uninitialized
    """
    The PSM mint and redeem fees collected at each timestep.

    Updated in `model.parts.peg_stability_module`.
    """

    # Price Processes
    fei_price: USD = 1.0
    """The FEI token initial price, updated by `fei_price_process` System Parameter in `model.parts.price_processes`."""
    volatile_asset_price: USD = 2_000
    """The Volatile Asset initial price, update by `volatile_asset_process` System Parameter in `model.parts.price_processes`."""
    stable_asset_price: USD = 1.0
    """The Stable Asset initial price, update by `stable_asset_process` System Parameter in `model.parts.price_processes`."""
    volatile_asset_price_mean: float = 0.0
    """The Volatile Asset price mean used for calculation of `volatile_asset_risk_metric` State Variable."""

    volatile_asset_risk_metric: float = Uninitialized
    """
    The Volatile Asset Risk Metric, based on the price trend: price slope / average price.

    Updated in `model.parts.money_markets`.
    """

    volatile_asset_risk_metric_min: float = 0.0
    """
    The Volatile Asset Risk Metric simulation minimum used for calculation of `volatile_asset_risk_metric` State Variable.

    Updated in `model.parts.money_markets`.
    """

    volatile_asset_risk_metric_max: float = 0.0
    """
    The Volatile Asset Risk Metric simulation maximum used for calculation of `volatile_asset_risk_metric` State Variable.

    Updated in `model.parts.money_markets`.
    """

    # Liquidity Pools
    # NOTE Total liquidity pool metrics including both protocol- and user-supplied liquidity
    liquidity_pool_invariant: float = Uninitialized
    """The Uniswap style Liquidity Pool Constant Product invariant"""
    liquidity_pool_tvl: USD = Uninitialized
    """The Liquidity Pool Total Value Locked (TVL)"""
    liquidity_pool_fei_source_sink: FEI = 0.0
    """The user-circulating FEI sourced from or sinked to the Liquidity Pool due to rebalancing"""
    liquidity_pool_impermanent_loss: Percentage = 0.0
    """The total Liquidity Pool impermanent loss as a percentage of provided liquidity"""
    liquidity_pool_trading_fees: USD = 0.0
    """The Liquidity Pool trading fees collected at each timestep"""
    liquidity_pool_liquidity_tokens: UNI = 0.0
    """The total Liquidity Pool pool tokens, initialised as being equal to the initial Liquidity Pool FEI balance"""
    total_liquidity_pool_trading_fees: USD = 0.0
    """The accumulated total Liquidity Pool trading fees from start of simulation"""

    # Money Markets
    fei_money_market_borrowed: FEI = Uninitialized
    """The amount of FEI borrowed from the Money Market"""
    fei_money_market_utilization: Percentage = Uninitialized
    """The Money Market utilisation rate or percentage of FEI supplied that has been borrowed"""
    fei_money_market_borrow_rate: APR = 0.0
    """The FEI Money Market annualised borrow interest rate, as a function of Money Market utilization."""
    fei_money_market_supply_rate: APR = 0.0
    """The FEI Money Market annualised supply interest rate, as a function of Money Market utilization."""

    # FEI Savings Deposit
    fei_savings_rate: APR = Uninitialized
    """The FEI Savings Rate, updated by `fei_savings_rate_process` System Parameter in `model.parts.fei_savings_deposit`."""

    # PCV Aggregates
    total_pcv: USD = Uninitialized
    """The total USD value of PCV"""
    total_stable_asset_pcv_balance: StableAssetUnits = Uninitialized
    """The total balance of Stable Asset PCV"""
    total_volatile_asset_pcv_balance: VolatileAssetUnits = Uninitialized
    """The total balance of Volatile Asset PCV"""
    total_stable_asset_pcv: USD = Uninitialized
    """The total USD value of Stable Asset PCV"""
    total_volatile_asset_pcv: USD = Uninitialized
    """The total USD value of Volatile Asset PCV"""

    # PCV Metrics
    stable_backing_ratio: Percentage = Uninitialized
    """The percentage of user-circulating FEI backed by stable assets"""
    stable_pcv_ratio: Percentage = Uninitialized
    """The percentage of PCV backed by stable assets"""
    collateralization_ratio: Percentage = Uninitialized
    """The percentage collateralization of the total FEI supply"""
    # NOTE: Uncomment Below as part of working exercise in Quiz Notebook 1
    #reserve_ratio: Percentage = Uninitialized
    #"""The reserve ratio of the Fei Protocol"""
    pcv_yield: USD = Uninitialized
    """The per-timestep PCV yield accrued"""
    pcv_yield_rate: Percentage = Uninitialized
    """The annualised per-timestep PCV yield rate"""
    protocol_equity: USD = Uninitialized
    """The total PCV value less the value of user-circulating FEI supply"""
    protocol_revenue: USD = Uninitialized
    """The per-timestep protocol revenue including PCV yield and PSM mint/redeem fees"""

    # User-circulating FEI Capital Allocation Model
    capital_allocation_target_weights: np.ndarray = default(np.array([]))
    """A variable used to keep track of the target Capital Allocation of user-circulating FEI"""
    capital_allocation_rebalance_matrix: np.ndarray = default(np.array([]))
    """A variable used to debug Capital Allocation rebalancing"""
    capital_allocation_rebalance_remainder: np.ndarray = default(np.array([]))
    """A variable used to debug any FEI remainder that could not be allocated as part of Capital Allocation rebalancing"""


initial_state = StateVariables().__dict__
