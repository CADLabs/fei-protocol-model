import radcad as radcad
import logging
from model.types import (
    PCVDeposit,
)


def setup_initial_state(context: radcad.Context):
    logging.info("Setting up initial state")

    params = context.parameters
    initial_state = context.initial_state
    run = context.run
    timestep = 0

    """
    Liquidity Pool Setup
    """
    # Parameters
    dt = params["dt"]
    liquidity_pool_tvl = params["liquidity_pool_tvl"]
    fei_price_process = params["fei_price_process"]
    volatile_asset_price_process = params["volatile_asset_price_process"]

    # State Variables
    fei_deposit_liquidity_pool = initial_state["fei_deposit_liquidity_pool"]
    volatile_deposit_liquidity_pool = initial_state["volatile_deposit_liquidity_pool"]

    fei_price = fei_price_process(run, timestep * dt)
    volatile_asset_price = volatile_asset_price_process(run, timestep * dt)

    liquidity_pool_fei_asset_value = liquidity_pool_tvl / 2
    liquidity_pool_fei_balance = liquidity_pool_fei_asset_value / fei_price

    volatile_asset_pcv_deposit_liquidity_pool = liquidity_pool_tvl / 2
    liquidity_pool_volatile_asset_balance = (
        volatile_asset_pcv_deposit_liquidity_pool / volatile_asset_price
    )

    liquidity_pool_invariant = liquidity_pool_fei_balance * liquidity_pool_volatile_asset_balance

    # State Updates
    fei_deposit_liquidity_pool._balance = liquidity_pool_fei_balance
    fei_deposit_liquidity_pool._asset_value = liquidity_pool_fei_balance * fei_price
    volatile_deposit_liquidity_pool._balance = liquidity_pool_volatile_asset_balance
    volatile_deposit_liquidity_pool._asset_value = (
        liquidity_pool_volatile_asset_balance * volatile_asset_price
    )

    context.initial_state.update(
        {
            "liquidity_pool_tvl": liquidity_pool_tvl,
            "liquidity_pool_invariant": liquidity_pool_invariant,
            "fei_deposit_liquidity_pool": fei_deposit_liquidity_pool,
            "volatile_deposit_liquidity_pool": volatile_deposit_liquidity_pool,
        }
    )

    """
    PCV Yield Rate Setup
    """
    # Parameters
    stable_asset_yield_rate = params["stable_asset_yield_rate"]
    volatile_asset_yield_rate = params["volatile_asset_yield_rate"]

    # State Variables
    stable_deposit_yield_bearing: PCVDeposit = initial_state["stable_deposit_yield_bearing"]
    volatile_deposit_yield_bearing: PCVDeposit = initial_state["volatile_deposit_yield_bearing"]

    # State Updates
    stable_deposit_yield_bearing.yield_rate = stable_asset_yield_rate
    volatile_deposit_yield_bearing.yield_rate = volatile_asset_yield_rate


def setup_state_update_blocks(context: radcad.Context):
    # TODO Set up state update block initialization
    # state_update_blocks = context.state_update_blocks
    # params = context.parameters

    # state_update_blocks = [
    #     block for block in state_update_blocks \
    #     if block.get("include_if", False) and params[block["include_if"]]
    # ]
    return None
