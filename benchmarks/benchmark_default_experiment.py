from experiments.run import run
from experiments.default_experiment import experiment
import radcad


def test_benchmark_default_experiment(benchmark):
    benchmark.pedantic(default_experiment, iterations=3, rounds=3)

def default_experiment():
    simulation: radcad.Simulation = experiment.simulations[0]
    simulation.runs = 5

    _df, _exceptions = run(executable=experiment)
