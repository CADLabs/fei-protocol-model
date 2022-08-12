"""# System Parameters
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


from typing import Dict, List
import experiments.simulation_configuration as simulation

import numpy as np
from operator import lt, gt
from dataclasses import dataclass
from datetime import datetime
from model.utils import default
from model.types import (
    Callable,
    Deposit,
    PCVDeposit,
    Percentage,
    UserDeposit,
    Timestep,
    Run,
    List,
    USD,
    APR,
)
from model.stochastic_processes import create_stochastic_process_realizations
from model.constants import (
    wei,
)


# Used to configure stochastic processes,
# for simulation monte carlo runs,
# see experiments/simulation_configuration.py
# or specific experiment notebook
monte_carlo_runs = 100

volatile_asset_price_samples = create_stochastic_process_realizations(
    "brownian_motion_process",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=-50,
    sigma=20,
    initial_price=2000,
    runs=monte_carlo_runs,
)

stable_asset_price_samples = create_stochastic_process_realizations(
    "gaussian_noise_process",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=1,
    sigma=0.005,
    runs=monte_carlo_runs,
)

money_market_utilization_rate_samples = create_stochastic_process_realizations(
    "gaussian_noise_process",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    # NOTE Equivalent to money market utilisation rate
    mu=0.7,
    sigma=0.05,
    runs=monte_carlo_runs,
)


# Configure distribution of PCV Deposits
# Each distribution must contain the same set of PCV Deposits
"""
Illustrative parameterisation of initial state sourced from data sources such as
https://dune.com/llama/Fei-Protocol
https://app.fei.money/
as of 22 June 2022.
"""
pcv_deposit_distribution_sweep = [
    [
        # FEI PCV
        PCVDeposit(
            asset="fei",
            deposit_location="idle",
            _balance=170_000_000,
            _asset_value=170_000_000,
        ),
        PCVDeposit(
            asset="fei",
            deposit_location="liquidity_pool",
            # Initialized in setup_initial_state()
        ),
        PCVDeposit(
            asset="fei",
            deposit_location="money_market",
            _balance=30_000_000,
            _asset_value=0.0,  # Accounted as asset value of zero for PCV
        ),
        # Stable Asset PCV
        PCVDeposit(
            asset="stable",
            deposit_location="idle",
            _balance=70_000_000,
            _asset_value=70_000_000,
        ),
        PCVDeposit(
            asset="stable",
            deposit_location="yield_bearing",
            _balance=70_000_000,
            _asset_value=70_000_000,
        ),
        # Volatile Asset PCV
        PCVDeposit(
            asset="volatile",
            deposit_location="idle",
            # Assumes initial volatile asset price of 2000 USD
            _balance=102_500_000 / 2_000,
            _asset_value=102_500_000,
        ),
        PCVDeposit(
            asset="volatile",
            deposit_location="yield_bearing",
            _balance=102_500_000 / 2_000,
            _asset_value=102_500_000,
        ),
        PCVDeposit(
            asset="volatile",
            deposit_location="liquidity_pool",
            # Initialized in setup_initial_state()
        ),
    ],
]


# Generate PCV Deposit keys
pcv_deposit_distribution_sweep = [
    {deposit.key: deposit for deposit in distribution}
    for distribution in pcv_deposit_distribution_sweep
]
pcv_deposit_keys = list(pcv_deposit_distribution_sweep[0].keys())


# From Dune dashboard as of 22 June 2022:
total_user_circulating_fei = 225_000_000
fei_money_market_user_deposit_balance = 30_000_000

# Configure distribution of User Deposits
# Each distribution must contain the same set of User Deposits
"""
Illustrative parameterisation of initial state sourced from data sources such as
https://dune.com/llama/Fei-Protocol
https://app.fei.money/
as of 22 June 2022.
"""
user_deposit_distribution_sweep = [
    [
        # Assume all user-circulating FEI, apart from borrowed FEI, not supplied in money market is idle
        UserDeposit(
            asset="fei",
            deposit_location="idle",
            _balance=total_user_circulating_fei - fei_money_market_user_deposit_balance,
            _asset_value=total_user_circulating_fei - fei_money_market_user_deposit_balance,
        ),
        # Assume FEI Savings Deposit starts with no FEI deposited
        UserDeposit(
            asset="fei",
            deposit_location="savings",
            _balance=0,
            _asset_value=0,
        ),
        # Assume majority of liquidity provided by protocol
        UserDeposit(
            asset="fei",
            deposit_location="liquidity_pool",
            _balance=0,
            _asset_value=0,
        ),
        # Assume majority of liquidity provided by protocol
        UserDeposit(
            asset="volatile",
            deposit_location="liquidity_pool",
            _balance=0,
            _asset_value=0,
        ),
        UserDeposit(
            asset="fei",
            deposit_location="money_market",
            _balance=fei_money_market_user_deposit_balance,
            _asset_value=fei_money_market_user_deposit_balance,
        ),
    ],
]

# Generate User Deposit keys
user_deposit_distribution_sweep = [
    {deposit.key: deposit for deposit in distribution}
    for distribution in user_deposit_distribution_sweep
]
user_deposit_keys = list(user_deposit_distribution_sweep[0].keys())


@dataclass
class Parameters:
    """## System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value
    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Time parameters
    dt: List[Timestep] = default([simulation.DELTA_TIME])
    """
    Simulation timescale / timestep unit of time, in days.
    Used to scale calculations that depend on the number of days that have passed.
    For example, for dt = 100, each timestep equals 100 days.
    By default set to 1 day.

    NOTE Model has not been tested for `DELTA_TIME` != 1, further validation of calculations would be required.
    """

    date_start: List[datetime] = default(
        [
            datetime.now(),
        ]
    )
    """
    Start date for simulation as Python datetime

    Used by `model.utils` `update_timestamp(...)` State Update Function.
    """

    # Price Processes
    fei_price_process: List[Callable[[Run, Timestep], USD]] = default([lambda _run, _timestep: 1.0])
    """
    A process that returns the FEI spot price at each timestep.

    By default set a static price of 1 USD.

    Used in `model.parts.price_processes`.
    """

    stable_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: stable_asset_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the stable asset spot price at each timestep.

    By default set to a Gaussian Noise stochastic process.

    Used in `model.parts.price_processes`.
    """

    volatile_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: volatile_asset_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the volatile asset spot price at each timestep.

    By default set to a Brownian meander stochastic process.

    Used in `model.parts.price_processes`.
    """

    # FEI Savings Deposit
    fei_savings_rate_process: List[Callable[[Run, Timestep], APR]] = default(
        [lambda _run, _timestep: 0.015]
    )
    """
    A process that returns the FEI Savings Rate at each timestep.

    Used in `model.parts.fei_savings_deposit`.
    """

    # Peg Stability Module
    psm_mint_fee: List[Percentage] = default([0])
    """
    The fee collected by the PSM on minting.

    Used in `model.parts.peg_stability_module`.
    """

    psm_redeem_fee: List[Percentage] = default([0.001])  # 10 basis points = 0.1%
    """
    The fee collected by the PSM on redemption.

    Used in `model.parts.peg_stability_module`.
    """

    # Liquidity Pool
    liquidity_pool_tvl: List[USD] = default([50_000_000])
    """
    Volatile Asset Liquidity Pool TVL sourced from
    https://dune.com/llama/Fei-Protocol
    https://app.fei.money/
    as of 22 June 2022.

    This parameter is used to configure the Initial State of the Liquidity Pool PCV Deposit balances in `model/initialization.py`.

    Used in `model.parts.liquidity_pools`.
    """

    liquidity_pool_trading_fee: List[float] = default([0.003])
    """
    The Uniswap style trading fee collected on incoming assets.

    Used in `model.parts.liquidity_pools`.
    """

    # Money Market
    base_rate_per_block: List[float] = default([0])
    # Compound lending market "Compound Jump Rate Model" on-chain parameters, see `model.parts.money_markets` module
    multiplier_per_block: List[float] = default([23782343987 / wei])
    jump_multiplier_per_block: List[float] = default([518455098934 / wei])
    money_market_kink: List[float] = default([0.8])
    money_market_reserve_factor: List[float] = default([0.25])
    money_market_utilization_rate_process: List[Callable[[Run, Timestep], APR]] = default(
        [lambda run, timestep: money_market_utilization_rate_samples[run - 1][timestep]]
    )

    # Asset Yield Rates
    stable_asset_yield_rate: List[APR] = default([0.10])
    """
    The annualized yield (APR) earned by the stable asset yield-bearing PCV Deposit.

    Used in `model.parts.pcv_yield`.
    """

    volatile_asset_yield_rate: List[APR] = default([0.10])
    """
    The annualized yield (APR) earned by the volatile asset yield-bearing PCV Deposit.

    Used in `model.parts.pcv_yield`.
    """

    volatile_asset_risk_metric_time_window: List[Timestep] = default([30])
    """
    The time window used for calculating the Volatile Asset Risk Metric.

    Used in `model.parts.money_markets`.
    """

    # PCV Management Strategy
    rebalancing_period: List[Timestep] = default([int(365 / 4)])  # days
    """
    The duration in days between applying rebalancing strategy.

    Used in `model.parts.pcv_management`.
    """

    yield_withdrawal_period: List[Timestep] = default([None])  # days
    """
    The duration in days between withdrawing yield to an idle PCV Deposit.

    Set to `None` to disable. Only enable one of `yield_withdrawal_period` and `yield_reinvest_period` at a time.

    Used in `model.parts.pcv_yield`.
    """

    yield_reinvest_period: List[Timestep] = default([None])  # days
    """
    The duration in days between reinvesting yield into the PCV Deposit balance.

    Set to `None` to disable. Only enable one of `yield_withdrawal_period` and `yield_reinvest_period` at a time.

    Used in `model.parts.pcv_yield`.
    """

    target_stable_backing_ratio: List[float] = default([0.8])
    """
    The target % of user-circulating FEI that is backed by stable assets.

    See https://tribe.fei.money/t/fip-104-fei-pcv-reinforcement-proposal

    Set to `None` to disable. Only enable one of `target_stable_backing_ratio` and `target_stable_pcv_ratio` at a time.

    Used in `model.parts.pcv_management`.
    """

    target_stable_pcv_ratio: List[float] = default([None])
    """
    The target % of PCV value that is backed by stable assets.

    Set to `None` to disable. Only enable one of `target_stable_backing_ratio` and `target_stable_pcv_ratio` at a time.

    Used in `model.parts.pcv_management`.
    """

    target_rebalancing_condition: List[str] = default([lt])
    """
    Rebalance towards target stable PCV or backing ratio if less than (lt, <) or greater than (gt, >) target,
    if market conditions are good the strategy can increase volatile asset exposure (gt, >),
    and if market conditions are bad the strategy can reduce volatile asset exposure (lt, <).

    Used in `model.parts.pcv_management`.
    """

    # User-circulating FEI Capital Allocation Model
    capital_allocation_fei_deposit_variables: List[Deposit] = default(
        [
            [
                "fei_liquidity_pool_user_deposit",
                "fei_money_market_user_deposit",
                "fei_savings_user_deposit",
                "fei_idle_user_deposit",
            ]
        ]
    )
    """
    FEI Deposit class State Variables that will be rebalanced as part of Capital Allocation Model.

    Used in `model.parts.fei_capital_allocation`.
    """

    capital_allocation_rebalance_duration: Timestep = default([30])
    """
    Rebalance over X number of timesteps towards target user-circulating FEI Capital Allocation.

    Used in `model.parts.fei_capital_allocation`.
    """

    capital_allocation_yield_rate_moving_average_window: Timestep = default([3])
    """
    Calculate moving average of yield rate over window of X number of timesteps to smooth change in Capital Allocation weights.

    Used in `model.parts.fei_capital_allocation`.
    """

    capital_allocation_exogenous_concentration: List[np.ndarray] = default([np.array([1, 1, 1, 1])])
    """
    Dirichlet distribution concentration parameter for use in Capital Allocation exogenous, stochastic policy.

    Used in `model.parts.fei_capital_allocation`.
    """

    # PCV Deposit configuration
    pcv_deposits: List[Dict[str, PCVDeposit]] = default(pcv_deposit_distribution_sweep)
    """
    The distribution of PCV Deposits used to initialize the PCV Deposit State Variables,
    to enable performing a parameter sweep of the Initial State of PCV Deposits.
    """

    # User Deposit configuration
    user_deposits: List[Dict[str, PCVDeposit]] = default(user_deposit_distribution_sweep)
    """
    The distribution of User Deposits used to initialize the User Deposit State Variables,
    to enable performing a parameter sweep of the Initial State of User Deposits.
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
