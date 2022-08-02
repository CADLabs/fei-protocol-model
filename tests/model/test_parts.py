import pytest
import numpy as np

from experiments.default_experiment import experiment
from experiments.run import run


@pytest.fixture
def df():
    # Test all simulation result substeps
    experiment.engine.drop_substeps = False
    df, _exceptions = run(experiment)
    # Drop timestep 0 (initial state) and timestep 1 (partially initialized substeps)
    df = df.drop(df.query("timestep in [0, 1]").index)

    return df


def test_liquidity_pool_invariant(df):
    # Only expected to be consistent at end of each timestep
    df = df.query("substep == substep.max")
    fei_balance = (
        df.fei_liquidity_pool_pcv_deposit_balance
        + df.fei_liquidity_pool_user_deposit_balance
    )
    volatile_asset_balance = (
        df.volatile_liquidity_pool_pcv_deposit_balance
        + df.volatile_liquidity_pool_user_deposit_balance
    )

    assert (
        df.liquidity_pool_invariant == fei_balance * volatile_asset_balance
    ).all(), "Constant product invariant broken"


def test_liquidity_pool_tvl(df):
    fei_balance = (
        df.fei_liquidity_pool_pcv_deposit_balance
        + df.fei_liquidity_pool_user_deposit_balance
    )
    volatile_asset_balance = (
        df.volatile_liquidity_pool_pcv_deposit_balance
        + df.volatile_liquidity_pool_user_deposit_balance
    )

    df.liquidity_pool_tvl == (
        fei_balance * df.fei_price + volatile_asset_balance * df.volatile_asset_price
    ).all(), "Liquidity pool TVL inconsistent"


def test_pcv_accounting(df):
    assert (df.total_pcv > 0).all()
    assert (df.total_stable_asset_pcv > 0).all()
    assert (df.total_stable_asset_pcv_balance > 0).all()
    assert (df.total_volatile_asset_pcv > 0).all()
    assert (df.total_volatile_asset_pcv_balance > 0).all()

    assert (
        df.total_pcv == df.total_stable_asset_pcv + df.total_volatile_asset_pcv
    ).all(), "Total PCV constituents inconsistent"

    # # Only expected to be consistent at end of each timestep because PCV value depends on asset price
    df = df.query("substep == substep.max")
    assert (
        df.total_pcv
        == df.total_stable_asset_pcv_balance * df.stable_asset_price
        + df.total_volatile_asset_pcv_balance * df.volatile_asset_price
    ).all(), "Total PCV constituent balances inconsistent"


def test_money_market_utilization(df):
    # Only expected to be consistent at end of each timestep
    df = df.query("substep == substep.max")
    calculated_utilization_rate = df.fei_money_market_borrowed / (
        df.fei_money_market_pcv_deposit_balance
        + df.fei_money_market_user_deposit_balance
    )

    assert (
        np.isclose(df.fei_money_market_utilization, calculated_utilization_rate)
    ).all(), "Money market utilization rate inconsistent"
