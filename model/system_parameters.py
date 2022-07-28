"""
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
# Each distribution must contain the same set of deposits
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
            _balance=70_000_000,  # set this to 1_000_000 to test rebalancing policy
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


# From Dune dashboard
total_user_circulating_fei = 225_000_000
# TODO Confirm how much of 30e6 MM supply is user-supplied
fei_money_market_user_deposit_balance = 30_000_000

# Configure distribution of User Deposits
# Each distribution must contain the same set of deposits
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
    ]
]

# Generate User Deposit keys
user_deposit_distribution_sweep = [
    {deposit.key: deposit for deposit in distribution}
    for distribution in user_deposit_distribution_sweep
]
user_deposit_keys = list(user_deposit_distribution_sweep[0].keys())


@dataclass
class Parameters:
    """System Parameters
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
    """

    date_start: List[datetime] = default([datetime.now()])
    """Start date for simulation as Python datetime"""

    # Price Processes
    fei_price_process: List[Callable[[Run, Timestep], USD]] = default([lambda _run, _timestep: 1.0])
    """
    A process that returns the FEI spot price at each timestep.

    By default set a static price of 1 USD.
    """
    stable_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: stable_asset_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the stable asset spot price at each timestep.

    By default set to a Gaussian Noise stochastic process.
    """
    volatile_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: volatile_asset_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the volatile asset spot price at each timestep.

    By default set to a Brownian meander stochastic process.
    """

    # FEI Savings Deposit
    fei_savings_rate_process: List[Callable[[Run, Timestep], APR]] = default(
        [lambda _run, _timestep: 0.015]
    )

    # Liquidity Pool
    liquidity_pool_tvl: List[USD] = default([50_000_000])
    """Volatile Asset Liquidity Pool TVL
    The majority of FEI<>WETH liquidity is currently held in a Balancer pool at a 30/70 FEI/ETH ratio.
    
    See https://defi.watch/pools/Ethereum/0x90291319f1d4ea3ad4db0dd8fe9e12baf749e84500020000000000000000013c

    Other resources:
    * https://v2.info.uniswap.org/pair/0x94b0a3d511b6ecdb17ebf877278ab030acb0a878
    * https://tribe.fei.money/t/fip-70-lets-get-balsy/3752
    * https://forum.balancer.fi/t/fei-weth-liquidity-and-strenghtening-ties-with-fei/2381
    """

    liquidity_pool_trading_fee: List[float] = default([0.003])
    """
    The Uniswap style trading fee collected on incoming assets
    """

    # Money Market
    base_rate_per_block: List[float] = default([0])
    # Compound lending market "Compound Jump Rate Model" on-chain parameters, see `model.parts.money_markets` module
    # TODO [eng] As an extension, consider making key parameters config based
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
    The annualized yield (APR) earned by the stable asset yield-bearing PCV Deposit
    """

    volatile_asset_yield_rate: List[APR] = default([0.10])
    """
    The annualized yield (APR) earned by the volatile asset yield-bearing PCV Deposit
    """

    # PCV Management Strategy
    rebalancing_period: List[Timestep] = default([int(365 / 4)])  # days
    """
    The duration in days between applying rebalancing strategy
    """

    yield_withdrawal_period: List[Timestep] = default([-1])  # days, -1 == disabled
    """
    The duration in days between withdrawing yield to an idle PCV Deposit
    """

    yield_reinvest_period: List[Timestep] = default([-1])  # days, -1 == disabled
    """
    The duration in days between reinvesting yield into the PCV Deposit balance
    """

    target_stable_backing_ratio: List[float] = default([0.8])
    """
    The target % of user-circulating FEI that is backed by stable assets

    See https://tribe.fei.money/t/fip-104-fei-pcv-reinforcement-proposal

    Set to `None` to disable.
    """

    target_stable_pcv_ratio: List[float] = default([None])
    """
    The target % of PCV value that is backed by stable assets

    Set to `None` to disable.
    """

    target_rebalancing_condition: List[str] = default([lt])
    """
    Rebalance towards target stable PCV or backing ratio if less than (lt, <) or greater than (gt, >) target,
    if market conditions are good the strategy can increase volatile asset exposure (gt, >),
    and if market conditions are bad the strategy can reduce volatile asset exposure (lt, <).
    """

    # User-circulating FEI Capital Allocation Model
    capital_allocation_fei_deposit_variables: List[Deposit] = default(
        [
            [
                "fei_liquidity_pool_user_deposit",
                "fei_money_market_user_deposit",
                "fei_savings_user_deposit",
                # "fei_idle_user_deposit",
            ]
        ]
    )
    """
    FEI Deposit class State Variables rebalanced in Capital Allocation Model.
    """

    capital_allocation_rebalance_duration: Timestep = default([30])
    """
    Rebalance over X number of timesteps towards target user-circulating FEI Capital Allocation.
    """

    capital_allocation_yield_rate_moving_average_window: Timestep = default([3])
    """
    Calculate moving average of yield rate over window of X number of timesteps
    """

    capital_allocation_exogenous_concentration: List[np.ndarray] = default([np.array([1, 1, 1, 1])])
    """
    Dirichlet distribution concentration parameter for use in Capital Allocation exogenous, stochastic policy
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
