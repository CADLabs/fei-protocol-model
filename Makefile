setup: install kernel plotly

install: install-packages
	pip install -r requirements.txt

install-packages:
	git submodule update --init --recursive
	python -m pip install -e ./packages/checkthechain

kernel:
	python3 -m ipykernel install --user --name python-cadlabs-fei --display-name "Python (CADLabs Fei Model)"

plotly:
	jupyter labextension install jupyterlab-plotly@4.14.3

start-lab:
	jupyter lab

format:
	black --line-length 100 model

test:
	# Run Pytest tests
	python3 -m pytest -m "not api_test" tests
	# Execute Jupyter Notebooks
	# execute-notebooks
	# Check formatting
	python -m black --check --diff --line-length 100 model
	# Check docstrings
	# pylint --disable=all --enable=missing-docstring model

build-docs: docs-pdoc docs-jupyter-book

docs-pdoc:
	pdoc --html model -o docs --force

docs-jupyter-book:
	jupyter-book clean docs
	jupyter-book build --config docs/_config.yml --toc docs/_toc.yml --path-output docs .
	cp -r ./docs/model ./docs/_build/html/docs/model

serve-docs:
	gunicorn -w 4 -b 127.0.0.1:5000 docs.server:app

execute-notebooks:
	rm experiments/notebooks/*.nbconvert.* || true
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=python-cadlabs --execute --to notebook experiments/notebooks/*.ipynb
	rm experiments/notebooks/*.nbconvert.* || true

update-notebooks:
	rm experiments/notebooks/*.nbconvert.* || true
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=python-cadlabs --execute --to notebook --inplace experiments/notebooks/*.ipynb
	rm experiments/notebooks/*.nbconvert.* || true

clear-notebook-outputs:
	jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace experiments/notebooks/*.ipynb

benchmark-test:
	python -m pytest benchmarks/benchmark_default_experiment.py --benchmark-compare-fail=min:5% --benchmark-compare=benchmark.json

benchmark-default:
	python -m pytest benchmarks/benchmark_default_experiment.py --benchmark-only --benchmark-json output.json

profile-memory:
	mprof run --include-children --multiprocess $(target)
	mprof plot
