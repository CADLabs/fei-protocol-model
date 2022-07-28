"""FEI Savings Deposit
WIP
"""

import logging
import typing
from model.types import (
    CAMWeights,
    PCVDeposit,
    UserDeposit,
    USD,
    APR,
    FEI,
)
from model.system_parameters import Parameters


def policy_fei_savings_deposit(
    params: Parameters,
    substep,
    state_history,
    previous_state,
):
    """FEI Savings Deposit Policy
    Fetch the FEI Savings Rate from the `fei_savings_rate_process`.
    """
    # Parameters
    dt = params["dt"]
    fei_savings_rate_process = params["fei_savings_rate_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the FEI Savings Rate sample for the current run and timestep
    fei_savings_rate_sample = fei_savings_rate_process(run, timestep * dt)

    return {"fei_savings_rate": fei_savings_rate_sample}


def update_fei_savings_deposit_yield_rate(
    params: Parameters, substep, state_history, previous_state, policy_input
):
    """Update FEI Savings Deposit Yield Rate
    Update the FEI Savings Deposit Yield Rate from the FEI Savings Deposit Policy.
    """
    # Policy Inputs
    fei_savings_rate = policy_input["fei_savings_rate"]

    # State Variables
    fei_savings_user_deposit: UserDeposit = previous_state["fei_savings_user_deposit"]
    fei_savings_user_deposit.yield_rate = fei_savings_rate

    return "fei_savings_user_deposit", fei_savings_user_deposit
