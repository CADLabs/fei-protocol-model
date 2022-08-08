import os
import sys
import pytest


@pytest.mark.skip(reason="test should be run with mprof, see Makefile")
def test_notebook_memory(notebook="1_sanity_checks.ipynb"):
    """
    e.g. python test_notebook_memory.py "1_sanity_checks.ipynb"
    """
    directory = "experiments/notebooks/"
    result = os.popen(
        f"jupyter nbconvert --to script --execute --stdout {directory + notebook} | ipython"
    ).read()
    assert "1" in result


if __name__ == '__main__':
    notebook = sys.argv[1] 
    test_notebook_memory(notebook)
