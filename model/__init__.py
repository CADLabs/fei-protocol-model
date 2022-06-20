"""
Fei Protocol Model
"""
__version__ = "0.0.0"

from radcad import Model

from model.system_parameters import parameters

# from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks


# Instantiate a new Model
model = Model(
    params=parameters,
    # Initial state is configured in the initialization.py module
    initial_state={},  # initial_state
    state_update_blocks=state_update_blocks,
)
