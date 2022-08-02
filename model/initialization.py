import radcad as radcad
import logging
from dataclasses import make_dataclass
from model.state_variables import StateVariables
from model.system_parameters import pcv_deposit_keys, user_deposit_keys
from model.types import (
    PCVDeposit,
    UserDeposit,
)


def setup_initial_state(context: radcad.Context):
    logging.info("Setting up initial state")

    params = context.parameters
    run = context.run
    timestep = 0

    # Add PCV Deposit and User Deposit distribution configuration to StateVariables
    StateVariablesWithDeposits = make_dataclass(
        "StateVariablesWithDeposits",
        fields=(
            # Add all PCV Deposit instances
            [(key, PCVDeposit, params["pcv_deposits"][key]) for key in pcv_deposit_keys]
            # Add all User Deposit instances
            + [(key, UserDeposit, params["user_deposits"][key]) for key in user_deposit_keys]
        ),
        bases=(StateVariables,),
    )
    # Update Initial State to include all Deposit instances
    context.initial_state.update(StateVariablesWithDeposits().__dict__)
    initial_state = context.initial_state

    """
    Liquidity Pool Setup
    """
    # Parameters
    dt = params["dt"]
    liquidity_pool_tvl = params["liquidity_pool_tvl"]
    fei_price_process = params["fei_price_process"]
    volatile_asset_price_process = params["volatile_asset_price_process"]

    # State Variables
    fei_liquidity_pool_pcv_deposit = initial_state["fei_liquidity_pool_pcv_deposit"]
    volatile_liquidity_pool_pcv_deposit = initial_state["volatile_liquidity_pool_pcv_deposit"]

    fei_price = fei_price_process(run, timestep * dt)
    volatile_asset_price = volatile_asset_price_process(run, timestep * dt)

    liquidity_pool_fei_asset_value = liquidity_pool_tvl / 2
    liquidity_pool_fei_balance = liquidity_pool_fei_asset_value / fei_price

    volatile_asset_pcv_deposit_liquidity_pool = liquidity_pool_tvl / 2
    liquidity_pool_volatile_asset_balance = (
        volatile_asset_pcv_deposit_liquidity_pool / volatile_asset_price
    )

    liquidity_pool_invariant = liquidity_pool_fei_balance * liquidity_pool_volatile_asset_balance
    liquidity_pool_liquidity_tokens = liquidity_pool_fei_balance

    # State Updates
    fei_liquidity_pool_pcv_deposit.set_balance(liquidity_pool_fei_balance, fei_price)
    volatile_liquidity_pool_pcv_deposit.set_balance(
        liquidity_pool_volatile_asset_balance, volatile_asset_price
    )

    context.initial_state.update(
        {
            "liquidity_pool_tvl": liquidity_pool_tvl,
            "liquidity_pool_invariant": liquidity_pool_invariant,
            "liquidity_pool_liquidity_tokens": liquidity_pool_liquidity_tokens,
            "fei_liquidity_pool_pcv_deposit": fei_liquidity_pool_pcv_deposit,
            "volatile_liquidity_pool_pcv_deposit": volatile_liquidity_pool_pcv_deposit,
        }
    )

    """
    PCV Yield Rate Setup
    """
    # Parameters
    stable_asset_yield_rate = params["stable_asset_yield_rate"]
    volatile_asset_yield_rate = params["volatile_asset_yield_rate"]

    # State Variables
    stable_yield_bearing_pcv_deposit: PCVDeposit = initial_state["stable_yield_bearing_pcv_deposit"]
    volatile_yield_bearing_pcv_deposit: PCVDeposit = initial_state[
        "volatile_yield_bearing_pcv_deposit"
    ]

    # State Updates
    stable_yield_bearing_pcv_deposit.yield_rate = stable_asset_yield_rate
    volatile_yield_bearing_pcv_deposit.yield_rate = volatile_asset_yield_rate
