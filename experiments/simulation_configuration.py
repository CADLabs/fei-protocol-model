"""
Simulation configuration such as the number of timesteps and Monte Carlo runs
"""

# NOTE Model has not been tested for `DELTA_TIME` != 1
DELTA_TIME = 1  # days per timestep
SIMULATION_TIME_DAYS = 365  # number of days
TIMESTEPS = SIMULATION_TIME_DAYS // DELTA_TIME  # number of simulation timesteps
MONTE_CARLO_RUNS = 1  # number of runs
