"""# Price Processes Module
State update functions for drawing samples from misc. projected or stochastic asset price
processes configured in System Parameters.
"""

import typing

from model.types import (
    USD,
)
from model.system_parameters import Parameters


def update_fei_price(
    params: Parameters, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD]:
    """## Update FEI price
    Update the FEI price from the `fei_price_process`.
    """

    # Parameters
    dt = params["dt"]
    fei_price_process = params["fei_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the price sample for the current run and timestep
    fei_price_sample = fei_price_process(run, timestep * dt)

    return "fei_price", fei_price_sample


def update_stable_asset_price(
    params: Parameters, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD]:
    """## Update Stable Asset Price
    Update the stable asset price from the `stable_asset_price_process`.
    """

    # Parameters
    dt = params["dt"]
    stable_asset_price_process = params["stable_asset_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the price sample for the current run and timestep
    stable_asset_price_sample = stable_asset_price_process(run, timestep * dt)

    return "stable_asset_price", stable_asset_price_sample


def update_volatile_asset_price(
    params: Parameters, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD]:
    """Update Volatile Asset Price
    Update the volatile asset price from the `volatile_asset_price_process`.
    """

    # Parameters
    dt = params["dt"]
    volatile_asset_price_process = params["volatile_asset_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the price sample for the current run and timestep
    volatile_asset_price_sample = volatile_asset_price_process(run, timestep * dt)

    return "volatile_asset_price", volatile_asset_price_sample
