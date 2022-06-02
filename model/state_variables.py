"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

import model.constants as constants
import model.system_parameters as system_parameters

from dataclasses import dataclass
from datetime import datetime


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


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
