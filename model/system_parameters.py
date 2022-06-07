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
from model.types import (
    Callable,
    Timestep,
    Run,
    List,
    USD,
)


from model.stochastic_processes import create_stochastic_process_realizations

# +
# DEBUG: magic number
volatile_price_samples = create_stochastic_process_realizations(
    "volatile_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=-50,
    sigma=20,
    initial_price=2000,
)
# DEBUG: magic number
stable_price_samples = create_stochastic_process_realizations(
    "stable_price_samples",
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    mu=1,
    sigma=0.005,
)

fei_price_mean = 1.0


# -


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

    fei_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda _run, _timestep: fei_price_mean]
    )

    stable_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda _run, _timestep: stable_price_samples[_run - 1][_timestep]]
    )

    volatile_asset_price_process: List[Callable[[Run, Timestep], USD]] = default(
        [lambda _run, _timestep: volatile_price_samples[_run - 1][_timestep]]
    )


# Initialize Parameters instance with default values
parameters = Parameters().__dict__

# +
# Generate stochastic process realizations
# eth_price_samples = create_stochastic_process_realizations("eth_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)
