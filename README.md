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

...

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
| [...](model/parts/...) | ... |

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model, e.g. number of epochs in a year, Gwei in 1 Ether |
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

The [Differential Model Specification](...) depicts the model's overall structure across System States, System Inputs, System Parameters, State Update Logic and System Metrics.

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

The [experiments/notebooks/](experiments/notebooks/) directory contains ...

#### Notebook 1. ...

...

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

## Change Log

See [CHANGELOG.md](CHANGELOG.md) for notable changes and versions.

## Acknowledgements

...

## Contributors ✨

...

## License

...
