import typing

from model.types import (
    USD,
)


def update_stable_asset_price(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD]:
    """
    ## Stable Asset Price State Update Function
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
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD]:
    """
    ## Volatile Asset Price State Update Function
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
