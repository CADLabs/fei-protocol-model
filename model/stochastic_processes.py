import numpy as np
import pandas as pd
from stochastic import processes

import experiments.simulation_configuration as simulation
from experiments.utils import rng_generator


def geometric_brownian_motion_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    **kwargs,
):
    """Configure Geometric Brownian Motion process
    > A geometric Brownian motion S_t is the analytic solution to the stochastic differential equation with Wiener process...

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    mu = kwargs.get("mu")
    sigma = kwargs.get("sigma")
    initial_price = kwargs.get("initial_price", 1) or 1

    process = processes.continuous.GeometricBrownianMotion(
        drift=mu, volatility=sigma, t=(timesteps * dt + 1), rng=rng
    )
    price_samples = process.sample(timesteps * dt + 1, initial=initial_price)

    return price_samples


def brownian_motion_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    **kwargs,
):
    """Configure Brownian Motion process
    > A standard Brownian motion (discretely sampled) has independent and
    identically distributed Gaussian increments with variance equal to
    increment length. Non-standard Brownian motion includes a linear drift
    parameter and scale factor.

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    mu = kwargs.get("mu")
    sigma = kwargs.get("sigma")
    initial_price = kwargs.get("initial_price", 1) or 1

    process = processes.continuous.BrownianMotion(
        drift=mu, scale=sigma, t=(timesteps * dt + 1), rng=rng
    )
    price_samples = process.sample(timesteps * dt + 1)
    price_samples = [initial_price + z for z in price_samples]

    return price_samples


def gaussian_noise_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    **kwargs,
):
    """Configure Gaussian Noise Process

    Gaussian Noise Process

    See https://stochastic.readthedocs.io/en/latest/noise.html
    """

    mu = kwargs.get("mu")
    sigma = kwargs.get("sigma")

    process = processes.noise.GaussianNoise(t=(timesteps * dt), rng=rng)
    price_samples = process.sample(timesteps * dt + 1)
    price_samples = [mu + sigma * z for z in price_samples]

    return price_samples


def create_stochastic_process_realizations(
    process,
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    runs=1,
    **kwargs,
):
    """Create stochastic process realizations

    Using the stochastic processes defined in `processes` module, create random number generator (RNG) seeds,
    and use RNG to pre-generate samples for number of simulation timesteps.
    """
    if process == "geometric_brownian_motion_process":
        return [
            geometric_brownian_motion_process(
                timesteps=timesteps,
                dt=dt,
                rng=rng_generator(),
                mu=kwargs.get("mu"),
                sigma=kwargs.get("sigma"),
                initial_price=kwargs.get("initial_price"),
            )
            for _ in range(runs)
        ]
    elif process == "brownian_motion_process":
        return [
            brownian_motion_process(
                timesteps=timesteps,
                dt=dt,
                rng=rng_generator(),
                mu=kwargs.get("mu"),
                sigma=kwargs.get("sigma"),
                initial_price=kwargs.get("initial_price"),
            )
            for _ in range(runs)
        ]
    elif process == "gaussian_noise_process":
        return [
            gaussian_noise_process(
                timesteps=timesteps,
                dt=dt,
                rng=rng_generator(),
                mu=kwargs.get("mu"),
                sigma=kwargs.get("sigma"),
            )
            for _ in range(runs)
        ]
    else:
        raise Exception("Invalid Process")


def generate_volatile_asset_price_scenarios() -> pd.DataFrame:
    # Price trend scenarios

    base_price_trend = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=0,
        sigma=0.02,
        initial_price=2000,
        runs=1,
    )[0]

    bearish_price_trend = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=-0.5,
        sigma=0.02,
        initial_price=2000,
        runs=1,
    )[0]

    bullish_price_trend = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=0.5,
        sigma=0.02,
        initial_price=2000,
        runs=1,
    )[0]

    # Price volatility scenarios

    base_price_volatility = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=0,
        sigma=0.02,
        initial_price=2000,
        runs=1,
    )[0]

    low_price_volatility = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=0,
        sigma=0.02 * 0.5,
        initial_price=2000,
        runs=1,
    )[0]

    high_price_volatility = create_stochastic_process_realizations(
        "geometric_brownian_motion_process",
        timesteps=simulation.TIMESTEPS,
        dt=simulation.DELTA_TIME,
        mu=0,
        sigma=0.02 * 2,
        initial_price=2000,
        runs=1,
    )[0]

    return pd.DataFrame(
        {
            # Price trend scenarios
            "base_price_trend": base_price_trend,
            "bearish_price_trend": bearish_price_trend,
            "bullish_price_trend": bullish_price_trend,
            # Price volatility scenarios
            "base_price_volatility": base_price_volatility,
            "low_price_volatility": low_price_volatility,
            "high_price_volatility": high_price_volatility,
        }
    )
