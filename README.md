# [Fei Protocol Model](https://fei.money)

[![Python package](https://github.com/CADLabs/fei-protocol-model/actions/workflows/python.yml/badge.svg)](https://github.com/CADLabs/fei-protocol-model/actions/workflows/python.yml)

See the [CADLabs Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model) for an example [radCAD](https://github.com/CADLabs/radCAD) modelling & simulation project based on this template.

## Table of Contents

* [Introduction](#Introduction)
  * [Model Features](#Model-Features)
  * [Directory Structure](#Directory-Structure)
  * [Model Architecture](#Model-Architecture)
  * [Model Assumptions](#Model-Assumptions)
  * [Differential Model Specification](#Differential-Model-Specification)
* [Environment Setup](#Environment-Setup)
* [Simulation Experiments](#Simulation-Experiments)
* [Tests](#Tests)
* [Change Log](#Change-Log)
* [Acknowledgements](#Acknowledgements)
* [Contributors](#Contributors-)
* [License](#License)

---

## Introduction

...

### Model Features

Currently the model includes the following features:
* [PCV Deposit Class](model/types.py) with standard methods and assertions for safe operation and a familiar interface
* [PCV movements](model/parts/pcv_management.py) between PCV Deposit instances including a basic rebalancing strategy targeting a stable backing ratio
* [PCV Deposit yield accrual](model/parts/pcv_yield.py) and management
* [Liquidity Pool subsystem](model/parts/liquidity_pools.py) that sources and sinks FEI directly between the pool and PSM, ready to be integrated with more granular strategies such as capital allocation of user-circulating FEI
* [Money Market subsystem](model/parts/money_markets.py) with placeholder dynamics, ready to be integrated
* Ability to initialise and perform parameter sweeps of Initial State using radCAD System Parameters
* [Jupyter notebooks](#simulation-experiments) exploring each part of the model as well as generic data analysis and model validation
* Supports [state-space analysis](https://en.wikipedia.org/wiki/State-space_representation) of volatile asset price processes using both stochastic processes where that makes sense (e.g. certain risk analyses) or price trajectories, and [phase-space analysis](https://en.wikipedia.org/wiki/Phase_space) using parameter sweeps/grids (e.g. between volatile asset price levels and PCV management strategies)

### Next Steps

In the next phase of development the focus will be on the following:
* [ ] Implementation and integration of WIP FEI Savings Deposit model with complex relationships identified and appropriately included
* [ ] Formalisation of FEI demand
* [ ] Development of set of experiments to deliver on the ultimate goal of the model, as a useful tool for the Fei team and community in illuminating complexity in the system, and developing, testing, and deploying various PCV management strategies during the FIP process

Additionally:
* [ ] Develop user-circulating FEI processes and accounting
* [ ] Replace Money Market placeholder utilization dynamics and integrate into rest of system

### Directory Structure

* [data/](data/): Datasets and API data sources (such as Etherscan.io and Beaconcha.in) used in the model
* [docs/](docs/): Misc. documentation such as auto-generated docs from Python docstrings and Markdown docs
* [experiments/](experiments/): Analysis notebooks and experiment workflow (such as configuration and execution)
* [logs/](logs/): Experiment runtime log files
* [model/](model/): Model software architecture (structural and configuration modules)
* [tests/](tests/): Unit and integration tests for model and notebooks

### Model Architecture

The [model/](model/) directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

#### Structural Modules

The model is composed of several structural modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [accounting.py](model/parts/accounting.py) | Assorted accounting of FEI aggregate State Variables such as Protocol Owned FEI, User-circulating FEI, etc. |
| [system_metrics.py](model/parts/system_metrics.py) | [Placeholder] Assorted system metrics such as FEI Demand |
| [fei_savings_deposit.py](model/parts/fei_savings_deposit.py) | [Placeholder] Implementation of the FEI Savings Deposit |
| [liquidity_pools.py](model/parts/liquidity_pools.py) | Implementation of a generic Uniswap style FEI-Volatile Liquidity Pool |
| [money_markets.py](model/parts/money_markets.py) | Implementation of a generic Aave/Compound style Money Market |
| [pcv_management.py](model/parts/pcv_management.py) | Implementation of PCV management processes and strategies |
| [pcv_yield.py](model/parts/pcv_yield.py) | Implementation of PCV yield processes and strategies |
| [price_processes.py](model/parts/price_processes.py) | State update functions for drawing samples from misc. projected or stochastic asset price processes |
| [user_circulating_fei.py](model/parts/user_circulating_fei.py) | [Placeholder] Implementation of user-circulating FEI processes and accounting |

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model, e.g. number of epochs in a year, Gwei in 1 Ether |
| [initialization.py](model/initialization.py) | Code used to set up the Initial State of the model before each subset from the System Parameters |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model State Update Block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various Python types used in the model, such as the `PCVDeposit` Class and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

### Model Assumptions

...

[ASSUMPTIONS.md](ASSUMPTIONS.md)

### Differential Model Specification

The [Differential Model Specification (WIP)](https://lucid.app/lucidchart/3d7d90e2-582d-4054-9176-5019943965c5/edit) depicts the model's overall structure across System States, System Inputs, System Parameters, State Update Logic and System Metrics.

## Environment Setup

The following steps guide you through how to set up a custom development environment using Python 3 and Jupyter.

Please note the following prerequisites before getting started:
* Python: tested with versions 3.8, 3.9
* NodeJS might be needed if using Plotly with Jupyter Lab (Plotly works out the box when using the Anaconda/Conda package manager with Jupyter Lab or Jupyter Notebook)

First, set up a Python 3 [virtualenv](https://docs.python.org/3/library/venv.html) development environment (or use the equivalent Anaconda step):
```bash
# Create a virtual environment using Python 3 venv module
python3 -m venv venv
# Activate virtual environment
source venv/bin/activate
```

Make sure to activate the virtual environment before each of the following steps.

Secondly, install the Python 3 dependencies using [Pip](https://packaging.python.org/tutorials/installing-packages/), from the [requirements.txt](requirements.txt) file within your new virtual environment:
```bash
# Install Python 3 dependencies inside virtual environment
pip install -r requirements.txt
```

To create a new Jupyter Kernel specifically for this environment, execute the following command:
```bash
python3 -m ipykernel install --user --name python-cadlabs-fei --display-name "Python (CADLabs Fei Model)"
```

You'll then be able to select the kernel with display name `Python (CADLabs Fei Model)` to use for your notebook from within Jupyter.

To start Jupyter Notebook or Lab (see notes about issues with [using Plotly with Jupyter Lab](#Known-Issues)):
```bash
jupyter notebook
# Or:
jupyter lab
```

For more advanced Unix/macOS users, a [Makefile](Makefile) is also included for convenience that simply executes all the setup steps. For example, to setup your environment and start Jupyter Lab:
```bash
# Setup environment
make setup
# Start Jupyter Lab
make start-lab
```

### Known Issues

#### Plotly doesn't display in Jupyter Lab

To install and use Plotly with Jupyter Lab, you might need NodeJS installed to build Node dependencies, unless you're using the Anaconda/Conda package manager to manage your environment. Alternatively, use Jupyter Notebook which works out the box with Plotly.

See https://plotly.com/python/getting-started/

You might need to install the following "lab extension": 
```bash
jupyter labextension install jupyterlab-plotly@4.14.3
```

#### Windows Issues

If you receive the following error and you use Anaconda, try: `conda install -c anaconda pywin32`
> DLL load failed while importing win32api: The specified procedure could not be found.

## Simulation Experiments

The [experiments/](experiments/) directory contains modules for configuring and executing simulation experiments, as well as performing post-processing of the results.

The [experiments/notebooks/](experiments/notebooks/) directory contains Jupyter notebooks exploring each part of the model as well as generic data analysis and model validation.

#### Sanity Checks

See [experiments/notebooks/sanity_checks.ipynb](experiments/notebooks/sanity_checks.ipynb)

The purpose of this notebook is to provide a set of standard sanity checks to validate the model as it developed, across different volatile asset price trajectories.

#### Walkthrough

See [experiments/notebooks/walkthrough.ipynb](experiments/notebooks/walkthrough.ipynb)

The purpose of this notebook was to demonstrate the state of the model during a previous worksession.

#### Exploratory Data Analysis

See [experiments/notebooks/exploratory_data_analysis.ipynb](experiments/notebooks/exploratory_data_analysis.ipynb)

The purpose of this notebook is to perform Exploratory Data Analysis of real Fei data sets using `checkthechain`. This notebook currently has Storm's original analysis and is on-hold until further exploration is needed and the `ctc` issues are resolved.

#### Money Markets Notebook

See [experiments/notebooks/money_markets_notebook.ipynb](experiments/notebooks/money_markets_notebook.ipynb)

The purpose of this notebook is to illustrate the operation of the generic Money Market subsystem.

#### PCV Management Notebook

See [experiments/notebooks/pcv_management_notebook.ipynb](experiments/notebooks/pcv_management_notebook.ipynb)

The purpose of this notebook is to illustrate PCV management strategies.

#### PCV Yield Notebook

See [experiments/notebooks/pcv_yield_notebook.ipynb](experiments/notebooks/pcv_yield_notebook.ipynb)

The purpose of this notebook is to illustrate PCV yield accrual and management.

## Tests

We use Pytest to test the `model` module code, as well as the notebooks.

To execute the Pytest tests:
```bash
source venv/bin/activate
python3 -m pytest tests
```

To run the full GitHub Actions CI Workflow (see [.github/workflows](.github/workflows)):
```bash
source venv/bin/activate
make test
```

### Simulation Profiling

A notebook exists to perform simulation time profiling of individual State Update Blocks of the model, see [experiments/notebooks/simulation_profiling/simulation_timestep_substep_profiling.ipynb]. Simulation time profiling of PRs is also performed in the GitHub Action pipeline, and included in each PR by a bot. See the Makefile and GitHub Action file for more details.

Memory profiling can also be performed using `memory-profiler`.

## Change Log

See [CHANGELOG.md](CHANGELOG.md) for notable changes and versions.

## Acknowledgements

...

## Contributors ✨

...

## License

...
