"""
Simulation configuration such as the number of timesteps and Monte Carlo runs
"""

from model.constants import days_per_month


DELTA_TIME = 1  # days per timestep
SIMULATION_TIMESTEPS = 400
# SIMULATION_TIME_MONTHS = 12  # number of months
# TIMESTEPS = (
#     days_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
# )  # number of simulation timesteps
TIMESTEPS = SIMULATION_TIMESTEPS // DELTA_TIME
MONTE_CARLO_RUNS = 1  # number of runs
