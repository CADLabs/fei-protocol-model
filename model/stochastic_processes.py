import numpy as np
from stochastic import processes

import experiments.simulation_configuration as simulation
from experiments.utils import rng_generator


def create_volatile_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    **kwargs,
):
    """Configure environmental volatile price process

    > A Brownian meander is a Brownian motion from (0, 0) to (t, 0) which is conditioned to be non-negative on the interval [0, t].

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    
    mu = kwargs.get('mu')
    sigma = kwargs.get('sigma')
    initial_price = kwargs.get('initial_price')
    
    # runtime checking since this function is called regardless of setting
    initial_price = initial_price if initial_price is not None else 0
        
    process = processes.continuous.BrownianMotion(drift=mu, scale=sigma, t=(timesteps * dt), rng=rng)
    price_samples = process.sample(timesteps * dt + 1)
    price_samples = [
        initial_price + z for z in price_samples
    ]
    return price_samples


def create_stable_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    **kwargs,
):
    
    """Configure environmental stable price process

    Gaussian Noise Process
    
    See https://stochastic.readthedocs.io/en/latest/noise.html
    """
    
    mu=kwargs.get('mu')
    sigma=kwargs.get('sigma')
    
    # runtime checking since this function is called regardless of setting
    if mu is not None and sigma is not None:

        process = processes.noise.GaussianNoise(t=(timesteps * dt), rng=rng)
        price_samples = process.sample(timesteps * dt + 1)
        price_samples = [
            mu + sigma*z for z in price_samples
        ]
        return price_samples
    
    else:
        return [np.nan for x in range(timesteps * dt)]


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
        
    switcher = {
        "volatile_price_samples": [
            create_volatile_price_process(timesteps=timesteps, dt=dt,
                                        rng=rng_generator(),
                                        mu=kwargs.get('mu'),
                                        sigma=kwargs.get('sigma'),
                                        initial_price = kwargs.get('initial_price'))
            
            for _ in range(runs)
        ],
        "stable_price_samples": [
            create_stable_price_process(timesteps=timesteps, dt=dt,
                                        rng=rng_generator(),
                                        mu=kwargs.get('mu'),
                                        sigma=kwargs.get('sigma'))
            for _ in range(runs)
        ],
    }

    return switcher.get(process, "Invalid Process")
