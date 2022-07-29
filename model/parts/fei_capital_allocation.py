"""FEI Capital Allocation  Model
"""

from model.types import (
    UserDeposit,
)
from model.system_parameters import Parameters
from scipy.stats import dirichlet
import numpy as np
import pprint
import networkx as nx
import logging

pp = pprint.PrettyPrinter(indent=4)


def policy_exogenous_weight_update(params: Parameters, substep, state_history, previous_state):
    """User-circulating FEI Capital Allocation Exogenous Weight Computation Policy
    TODO Implementation / validation of edge case behaviour WIP
    """
    # Parameters
    dt = params["dt"]
    alpha = params["capital_allocation_exogenous_concentration"]
    rebalance_duration = params["capital_allocation_rebalance_duration"]
    fei_deposit_variables = params["capital_allocation_fei_deposit_variables"]

    # State Variables
    timestep = previous_state["timestep"]

    # Calculate current weights
    fei_deposits = [previous_state[key] for key in fei_deposit_variables]
    current_deposit_balances = [deposit.balance for deposit in fei_deposits]
    total_fei = sum(current_deposit_balances)
    current_weights = [balance / total_fei for balance in current_deposit_balances]

    # Calculate target weights: stochastic, exogenous weights
    # https://en.wikipedia.org/wiki/Dirichlet_distribution
    # TODO Take random_state from simulation seed
    perturbation = dirichlet.rvs(alpha, size=1, random_state=timestep)[0]
    rebalance_rate = np.sqrt(dt / rebalance_duration)
    target_weights = rebalance_rate * perturbation + np.array(current_weights)
    normalised_target_weights = target_weights / target_weights.sum()

    return {
        "capital_allocation_target_weights": normalised_target_weights,
    }


def policy_endogenous_weight_update(params: Parameters, substep, state_history, previous_state):
    """User-circulating FEI Capital Allocation Endogenous Weight Computation Policy"""
    # Parameters
    fei_deposit_variables = params["capital_allocation_fei_deposit_variables"]
    moving_average_window = params["capital_allocation_yield_rate_moving_average_window"]

    # State Variables
    timestep = previous_state["timestep"]

    # Calculate target weights: weight = yield / risk
    # Calculate moving average of yield vector
    yield_vector = np.array(
        [
            sum(
                [
                    state[-1][key].yield_rate
                    for state in state_history[-moving_average_window:timestep]
                ]
            )
            / moving_average_window
            or previous_state[key].yield_rate
            for key in fei_deposit_variables
        ]
    )
    # NOTE Currently assumes no difference in risk preference between deposits
    risk_vector = np.array([1 for _ in yield_vector])
    target_weights = yield_vector / risk_vector
    normalised_target_weights = target_weights / target_weights.sum()

    return {
        "capital_allocation_target_weights": normalised_target_weights,
    }


def array_sum_threshold_check(array, total, thresh):
    return np.abs(sum(array) - total) < thresh


def policy_deposit_rebalance(params: Parameters, substep, state_history, previous_state):
    """User-circulating FEI Capital Allocation Rebalance Policy"""
    # Parameters
    dt = params["dt"]
    rebalance_duration = params["capital_allocation_rebalance_duration"]
    fei_deposit_variables = params["capital_allocation_fei_deposit_variables"]

    # State Variables
    target_weights: np.ndarray = previous_state["capital_allocation_target_weights"]
    fei_price = previous_state["fei_price"]

    fei_liquidity_pool_user_deposit: UserDeposit = previous_state["fei_liquidity_pool_user_deposit"]
    fei_money_market_user_deposit: UserDeposit = previous_state["fei_money_market_user_deposit"]
    fei_savings_user_deposit: UserDeposit = previous_state["fei_savings_user_deposit"]
    fei_idle_user_deposit: UserDeposit = previous_state["fei_idle_user_deposit"]

    # Calculate current weights
    fei_deposits = [previous_state[key] for key in fei_deposit_variables]
    current_deposit_balances = np.array([deposit.balance for deposit in fei_deposits])
    total_fei = sum(current_deposit_balances)
    current_weights = np.array([balance / total_fei for balance in current_deposit_balances])

    assert array_sum_threshold_check(current_deposit_balances, total_fei, 1e-3), "Summation error"
    assert array_sum_threshold_check(current_weights, 1, 1e-3), "Percentage calculation error"
    assert array_sum_threshold_check(current_weights, 1, 1e-3), "Percentage calculation error"

    # Calculate deltas for rebalancing
    rebalance_rate = np.sqrt(dt / rebalance_duration)

    rebalance_matrix, total_fei_deposit_balance_change = compute_rebalance_matrix(
        target_weights, current_weights, total_fei, rebalance_rate
    )

    # TODO Correctly handle transfers of volatile asset liquidity to / from liquidity pool,
    # specifically for exogenous process currently
    for (row, column), value in filter(lambda x: x != 0, np.ndenumerate(rebalance_matrix)):
        # Perform balance transfer
        from_index = column if value > 0 else row
        to_index = row if value > 0 else column

        transfer_amount = min(abs(value), fei_deposits[from_index].balance)
        assert transfer_amount <= abs(
            value
        ), f"Deposit {fei_deposits[from_index].key} balance {fei_deposits[from_index].balance} less than capital allocation rebalance value {abs(value)}"

        fei_deposits[from_index].transfer(
            to=fei_deposits[to_index],
            amount=transfer_amount,
            from_asset_price=fei_price,
            to_asset_price=fei_price,
        )

    new_capital_allocation = [deposit.balance for deposit in fei_deposits]

    # Check that deposit sizes after all rebalances match the total balance change set by weight changes
    # assert np.allclose(
    #     current_deposit_balances + total_fei_deposit_balance_change, new_capital_allocation
    # ), "Capital allocation rebalancing error"
    rebalance_remainder = (
        current_deposit_balances + total_fei_deposit_balance_change
    ) - new_capital_allocation
    rebalance_remainder_tolerance = 0.001  # % of deposit balance
    rebalance_remainder[np.isclose(rebalance_remainder, 0)] = 0
    rebalance_remainder_pct = rebalance_remainder / (current_deposit_balances + 1e-9)
    if np.any(rebalance_remainder_pct > rebalance_remainder_tolerance):
        log_rebalance_remainder = {
            deposit.key: rebalance_remainder[index] for index, deposit in enumerate(fei_deposits)
        }
        logging.warning(
            f"Capital allocation rebalancing error: movement of {log_rebalance_remainder} FEI unallocated"
        )
    assert array_sum_threshold_check(new_capital_allocation, total_fei, 1e-3), "Summation error"

    return {
        "capital_allocation_rebalance_matrix": rebalance_matrix,
        "capital_allocation_rebalance_remainder": rebalance_remainder,
        "fei_liquidity_pool_user_deposit": fei_liquidity_pool_user_deposit,
        "fei_money_market_user_deposit": fei_money_market_user_deposit,
        "fei_savings_user_deposit": fei_savings_user_deposit,
        "fei_idle_user_deposit": fei_idle_user_deposit,
    }


def compute_rebalance_matrix(
    target_fei_allocation,
    current_fei_allocation,
    total_fei,
    rebalance_rate=1,
):
    # Calculate delta matrix - amounts to rebalance and to disaggregate
    allocation_pct_change = target_fei_allocation - current_fei_allocation
    total_fei_deposit_balance_change = rebalance_rate * allocation_pct_change * total_fei

    number_of_deposits = len(total_fei_deposit_balance_change)
    deposit_incidence_matrix = generate_constrained_incidence_matrix(number_of_deposits)

    total_balance_changes = np.append(total_fei_deposit_balance_change, np.array(0))
    # Solve Ax = b st 1Tx == 0 (conservation constraint)
    deltas = np.linalg.pinv(deposit_incidence_matrix) @ total_balance_changes

    assert np.allclose(
        np.dot(deposit_incidence_matrix, deltas), total_balance_changes
    ), "No solution to linear algebra problem"

    rebalance_matrix = populate_delta_triu(deltas, number_of_deposits)

    return rebalance_matrix, total_fei_deposit_balance_change


def populate_delta_triu(d, w_size):
    D = np.zeros((w_size, w_size))

    k = 0
    for i in range(len(D)):
        for j in range(len(D)):
            if i < j:
                D[i][j] = d[k]
                k += 1

    return D


def generate_constrained_incidence_matrix(n_deposits):
    G = nx.complete_graph(n_deposits)
    A = (nx.incidence_matrix(G, oriented=True).toarray() * -1).astype(int)

    # NOTE: fixes networkx rendition of 2-deposit adjacency matrix generation
    if A.shape[1] == 1:
        A = np.hstack([A, np.zeros((2, 1))])

    constrained_incidence_matrix = np.vstack([A, np.ones((1, A.shape[1]))])
    return constrained_incidence_matrix
