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
import radcad as radcad
import logging

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
    PCVDeposit,
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
    total_user_circulating_fei: FEI = 225_000_000

    # TODO: configure user-circulating FEI states
    idle_user_circulating_fei: FEI = 0.0
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
    # TODO: convert to PCVDeposit class
    fei_money_market_pcv_deposit_balance: FEI = Uninitialized
    fei_money_market_pcv_deposit: USD = Uninitialized
    fei_money_market_borrowed: FEI = Uninitialized
    fei_money_market_lending_rate: APY = Uninitialized
    fei_money_market_utilization: Percentage = Uninitialized

    # FEI Savings Deposit
    # TODO: account for wrapped yield-bearing FEI supply
    fei_savings_deposit_balance: FEI = Uninitialized
    fei_savings_rate: APY = Uninitialized

    # 3rd party yield rates
    # TODO: convert to parameters used to initialize PCV deposits in setup_initial_state()
    # stable_asset_yield_rate: APY = Uninitialized
    # volatile_asset_yield_rate: APY = Uninitialized

    # FEI PCV
    fei_deposit_idle: PCVDeposit = PCVDeposit(
        asset="fei",
        deposit_type="idle",
        balance=170_000_000,
        asset_value=170_000_000,
    )

    fei_deposit_liquidity_pool: PCVDeposit = PCVDeposit(
        asset="fei",
        deposit_type="liquidity_pool",
        # Initialized in setup_initial_state()
    )

    fei_deposit_money_market: PCVDeposit = PCVDeposit(
        asset="fei",
        deposit_type="money_market",
        balance=30_000_000,
        asset_value=0.0,  # Accounted as asset value of zero for PCV
    )

    # Stable Asset PCV
    stable_deposit_idle: PCVDeposit = PCVDeposit(
        asset="stable",
        deposit_type="idle",
        balance=140_000_000,
        asset_value=140_000_000,
    )

    stable_deposit_yield_bearing: PCVDeposit = PCVDeposit(
        asset="stable",
        deposit_type="yield_bearing",
        balance=0,
        asset_value=0,
    )

    # Volatile Asset PCV
    volatile_deposit_idle: PCVDeposit = PCVDeposit(
        asset="volatile",
        deposit_type="idle",
        # Assumes initial volatile asset price of 2000 USD
        balance=205_000_000 / 2_000,
        asset_value=205_000_000,
    )

    volatile_deposit_yield_bearing: PCVDeposit = PCVDeposit(
        asset="volatile",
        deposit_type="yield_bearing",
        balance=0,
        asset_value=0,
    )

    volatile_deposit_liquidity_pool: PCVDeposit = PCVDeposit(
        asset="volatile",
        deposit_type="liquidity_pool",
        # Initialized in setup_initial_state()
    )

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


def setup_initial_state(context: radcad.Context):
    logging.info("Setting up initial state")

    params = context.parameters
    initial_state = context.initial_state
    run = context.run
    timestep = 0

    # Parameters
    # TODO: fix subset indexing from radCAD context
    dt = params["dt"]
    liquidity_pool_tvl = params["liquidity_pool_tvl"]
    fei_price_process = params["fei_price_process"]
    volatile_asset_price_process = params["volatile_asset_price_process"]

    # State Variables
    fei_deposit_liquidity_pool = initial_state["fei_deposit_liquidity_pool"]
    volatile_deposit_liquidity_pool = initial_state["volatile_deposit_liquidity_pool"]

    # Liquidity Pool Setup
    fei_price = fei_price_process(run, timestep * dt)
    volatile_asset_price = volatile_asset_price_process(run, timestep * dt)

    liquidity_pool_fei_asset_value = liquidity_pool_tvl / 2
    liquidity_pool_fei_balance = liquidity_pool_fei_asset_value / fei_price

    volatile_asset_pcv_deposit_liquidity_pool = liquidity_pool_tvl / 2
    liquidity_pool_volatile_asset_balance = (
        volatile_asset_pcv_deposit_liquidity_pool / volatile_asset_price
    )

    liquidity_pool_invariant = liquidity_pool_fei_balance * liquidity_pool_volatile_asset_balance

    # State Updates
    fei_deposit_liquidity_pool.balance = liquidity_pool_fei_balance
    fei_deposit_liquidity_pool.asset_value = liquidity_pool_fei_balance * fei_price
    volatile_deposit_liquidity_pool.balance = liquidity_pool_volatile_asset_balance
    volatile_deposit_liquidity_pool.asset_value = (
        liquidity_pool_volatile_asset_balance * volatile_asset_price
    )

    context.initial_state.update(
        {
            "liquidity_pool_tvl": liquidity_pool_tvl,
            "liquidity_pool_invariant": liquidity_pool_invariant,
            "fei_deposit_liquidity_pool": fei_deposit_liquidity_pool,
            "volatile_deposit_liquidity_pool": volatile_deposit_liquidity_pool,
        }
    )
