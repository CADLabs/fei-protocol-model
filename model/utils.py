"""
Misc. utility and helper functions
"""

import copy
import math
import logging
from dataclasses import field
from functools import partial


def _update_from_signal(
    state_variable,
    signal_key,
    params,
    substep,
    state_history,
    previous_state,
    policy_input,
):
    return state_variable, policy_input[signal_key]


def update_from_signal(state_variable, signal_key=None):
    """A generic State Update Function to update a State Variable directly from a Policy Signal
    Args:
        state_variable (str): State Variable key
        signal_key (str, optional): Policy Signal key. Defaults to None.
    Returns:
        Callable: A generic State Update Function
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_update_from_signal, state_variable, signal_key)


def local_variables(_locals):
    return {key: _locals[key] for key in [_key for _key in _locals.keys() if "__" not in _key]}


def default(obj):
    return field(default_factory=lambda: copy.copy(obj))


def approx_greater_equal_zero(value, rel_tol=0.0, abs_tol=1e-10):
    return value >= 0 or math.isclose(value, 0, rel_tol=rel_tol, abs_tol=abs_tol)


def approx_eq(v1, v2, rel_tol=0.0, abs_tol=1e-10):
    return math.isclose(v1, v2, rel_tol=rel_tol, abs_tol=abs_tol)


def assert_log(condition, message="", _raise=True):
    try:
        assert condition, message
    except AssertionError as e:
        logging.warning(f"{e}: {message}")
        if _raise:
            raise AssertionError(f"{e}: {message}")

    return condition
