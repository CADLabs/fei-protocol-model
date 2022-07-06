"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


from cmath import inf
from typing import Dict
import experiments.simulation_configuration as simulation

from operator import lt, gt
from dataclasses import dataclass
from datetime import datetime
from model.utils import default
from model.types import (
    Callable,
    PCVDeposit,
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


volatile_asset_price_samples = create_stochastic_process_realizations(
    "volatile_asset_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=-50,
    sigma=20,
    initial_price=2000,
    runs=100,
)

stable_asset_price_samples = create_stochastic_process_realizations(
    "stable_asset_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=1,
    sigma=0.005,
    runs=100,
)

# Configure distribution of PCV deposits
# Each distribution must contain the same set of deposits
pcv_distribution_sweep = [
    [
        # FEI PCV
        PCVDeposit(
            asset="fei",
            deposit_type="idle",
            _balance=170_000_000,
            _asset_value=170_000_000,
        ),
        PCVDeposit(
            asset="fei",
            deposit_type="liquidity_pool",
            # Initialized in setup_initial_state()
        ),
        PCVDeposit(
            asset="fei",
            deposit_type="money_market",
            _balance=30_000_000,
            _asset_value=0.0,  # Accounted as asset value of zero for PCV
        ),
        # Stable Asset PCV
        PCVDeposit(
            asset="stable",
            deposit_type="idle",
            _balance=70_000_000,  # set this to 1_000_000 to test rebalancing policy
            _asset_value=70_000_000,
        ),
        PCVDeposit(
            asset="stable",
            deposit_type="yield_bearing",
            _balance=70_000_000,
            _asset_value=70_000_000,
        ),
        # Volatile Asset PCV
        PCVDeposit(
            asset="volatile",
            deposit_type="idle",
            # Assumes initial volatile asset price of 2000 USD
            _balance=102_500_000 / 2_000,
            _asset_value=102_500_000,
        ),
        PCVDeposit(
            asset="volatile",
            deposit_type="yield_bearing",
            _balance=102_500_000 / 2_000,
            _asset_value=102_500_000,
        ),
        PCVDeposit(
            asset="volatile",
            deposit_type="liquidity_pool",
            # Initialized in setup_initial_state()
        ),
    ],
    # Set stable and volatile idle deposit asset values to 1_000_000 USD to test rebalancing policy
    # [
    #     # FEI PCV
    #     PCVDeposit(
    #         asset="fei",
    #         deposit_type="idle",
    #         _balance=170_000_000,
    #         _asset_value=170_000_000,
    #     ),
    #     PCVDeposit(
    #         asset="fei",
    #         deposit_type="liquidity_pool",
    #         # Initialized in setup_initial_state()
    #     ),
    #     PCVDeposit(
    #         asset="fei",
    #         deposit_type="money_market",
    #         _balance=30_000_000,
    #         _asset_value=0.0,  # Accounted as asset value of zero for PCV
    #     ),
    #     # Stable Asset PCV
    #     PCVDeposit(
    #         asset="stable",
    #         deposit_type="idle",
    #         _balance=1_000_000,
    #         _asset_value=1_000_000,
    #     ),
    #     PCVDeposit(
    #         asset="stable",
    #         deposit_type="yield_bearing",
    #         _balance=70_000_000,
    #         _asset_value=70_000_000,
    #     ),
    #     # Volatile Asset PCV
    #     PCVDeposit(
    #         asset="volatile",
    #         deposit_type="idle",
    #         # Assumes initial volatile asset price of 2000 USD
    #         _balance=1_000_000 / 2_000,
    #         _asset_value=1_000_000,
    #     ),
    #     PCVDeposit(
    #         asset="volatile",
    #         deposit_type="yield_bearing",
    #         _balance=102_500_000 / 2_000,
    #         _asset_value=102_500_000,
    #     ),
    #     PCVDeposit(
    #         asset="volatile",
    #         deposit_type="liquidity_pool",
    #         # Initialized in setup_initial_state()
    #     )
    # ]
]
# Generate PCV Deposit keys
pcv_distribution_sweep = [
    {deposit.asset + "_deposit_" + deposit.deposit_type: deposit for deposit in distribution}
    for distribution in pcv_distribution_sweep
]
pcv_deposit_keys = pcv_distribution_sweep[0].keys()


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
    multiplier_per_block: List[float] = default([23782343987 / wei])
    jump_multiplier_per_block: List[float] = default([518455098934 / wei])
    money_market_kink: List[float] = default([0.8])
    money_market_reserve_factor: List[float] = default([0.25])

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

    TODO Introduce policy for rebalancing towards stable backing ratio,
    to replace current policy of rebalancing towards stable PCV ratio
    """
    target_stable_pcv_ratio: List[float] = default([0.5])
    """
    The target % of PCV value that is backed by stable assets
    """
    target_rebalancing_condition: List[str] = default([lt])
    """
    Rebalance towards target stable PCV or backing ratio if less than (lt, <) or greater than (gt, >) target,
    if market conditions are good the strategy can increase volatile asset exposure (gt, >),
    and if market conditions are bad the strategy can reduce volatile asset exposure (lt, <).
    """

    # PCV Deposit configuration
    pcv_deposits: List[Dict[str, PCVDeposit]] = default(pcv_distribution_sweep)
    """
    The distribution of PCV Deposits used to initialize the PCV Deposit State Variables,
    to enable performing a parameter sweep of the Initial State of PCV Deposits.
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
