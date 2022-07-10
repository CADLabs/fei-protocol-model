import numpy as np
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
    initial_price = kwargs.get("initial_price", 0) or 0

    process = processes.continuous.GeometricBrownianMotion(
        drift=mu, volatility=sigma, t=(timesteps * dt), rng=rng
    )
    price_samples = process.sample(timesteps * dt + 1)
    price_samples = [initial_price * z for z in price_samples]

    # Example of Geometric Brownian Motion Process using Numpy:
    # x = np.exp((mu - sigma ** 2 / 2) * dt + sigma * np.random.normal(0, np.sqrt(dt), size=(timesteps + 1)).T)
    # x = initial_price * x.cumprod(axis=0)

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
    initial_price = kwargs.get("initial_price", 0) or 0

    process = processes.continuous.BrownianMotion(
        drift=mu, scale=sigma, t=(timesteps * dt), rng=rng
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
