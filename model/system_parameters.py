"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


import model.constants as constants
import experiments.simulation_configuration as simulation

from dataclasses import dataclass
from datetime import datetime
from model.utils import default
from model.types import Callable, Timestep, Run, List, USD, APY
from model.stochastic_processes import create_stochastic_process_realizations


volatile_asset_price_samples = create_stochastic_process_realizations(
    "volatile_asset_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=-50,
    sigma=20,
    initial_price=2000,
    runs=10,
)

stable_asset_price_samples = create_stochastic_process_realizations(
    "stable_asset_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=1,
    sigma=0.005,
    runs=10,
)

fei_price_mean = 1.0


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
    Simulation timescale / timestep unit of time, in _.
    Used to scale calculations that depend on the number of _ that have passed.
    For example, for dt = 100, each timestep equals 100 _.
    By default set to _
    """

    date_start: List[datetime] = default([datetime.now()])
    """Start date for simulation as Python datetime"""

    # Price Processes
    fei_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda _run, _timestep: fei_price_mean]
    )
    stable_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: stable_asset_price_samples[run - 1][timestep]]
    )
    volatile_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda run, timestep: volatile_asset_price_samples[run - 1][timestep]]
    )

    # Liquidity Pools
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

    # PCV Management Strategy
    rebalancing_period: List[Timestep] = default([90])  # days


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
