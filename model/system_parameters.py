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
    Timestep,
    Run,
    List,
)


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


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
