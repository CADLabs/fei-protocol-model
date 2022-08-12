"""# User-circulating FEI Capital Allocation Model (CAM) Module
The Capital Allocation Model describes the aggregate movements of user-circulating FEI within the Fei Protocol ecosystem,
between any Deposit or location where users could choose to allocate their FEI.

These locations include:
- FEI Savings Deposit
- Competing yield opportunities (currently a generic money market in the model)
- Liquidity pools (including liquidity provision and FEI released into the user-circulating FEI supply from volatile asset liquidity pool imbalances)
- Simply holding FEI

These capital movements are computed based on a yield and risk weighted target allocation for each location.
At each timestep of the simulation, the actual allocation is rebalanced towards the target allocation, with some degree of uncertainty and delay.

Additionally, in a next step to further formulate FEI demand, the model will describe the minting and redemption of FEI to feed into the capital allocation.

PCV and protocol-owned FEI movements are independent of the Capital Allocation Model and managed directly via governance-implemented protocol policies.
"""

from typing import Dict, List
from model.system_parameters import Parameters
import model.parts.liquidity_pools as liquidity_pools
from scipy.stats import dirichlet
import numpy as np
import pprint
import networkx as nx
import logging
import copy

pp = pprint.PrettyPrinter(indent=4)


def policy_fei_capital_allocation_exogenous_weight_update(
    params: Parameters, substep, state_history, previous_state
):
    """## User-circulating FEI Capital Allocation Exogenous Weight Computation Policy
    Exogenous, stochastic Dirichlet distribution driven Capital Allocation policy.
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
    # TODO Take `random_state`` from simulation seed
    perturbation = dirichlet.rvs(alpha, size=1, random_state=timestep)[0]
    rebalance_rate = np.sqrt(dt / rebalance_duration)
    target_weights = rebalance_rate * perturbation + np.array(current_weights)
    normalised_target_weights = target_weights / target_weights.sum()

    return {
        "capital_allocation_target_weights": normalised_target_weights,
    }


def policy_fei_capital_allocation_endogenous_weight_update(
    params: Parameters, substep, state_history, previous_state
):
    """## User-circulating FEI Capital Allocation Endogenous Weight Computation Policy
    Endogenous yield and risk weighted target Capital Allocation policy.
    """
    # Parameters
    fei_deposit_variables = params["capital_allocation_fei_deposit_variables"]
    moving_average_window = params["capital_allocation_yield_rate_moving_average_window"]

    # State Variables
    timestep = previous_state["timestep"]
    volatile_asset_risk_metric = previous_state["volatile_asset_risk_metric"]

    # Calculate moving average of yield vector
    yield_history_map: Dict[str, List] = {
        key: [state[-1][key].yield_rate for state in state_history[-moving_average_window:timestep]]
        for key in fei_deposit_variables
    }
    yield_history: List[List] = yield_history_map.values()
    yield_map = {
        key: max(sum(yield_history) / moving_average_window, 1e-18) or previous_state[key].yield_rate
        for key, yield_history in yield_history_map.items()
    }
    yield_vector = np.array(list(yield_map.values()))

    # Calculate yield volatility risk
    yield_std = np.array([np.std(x) for x in yield_history])
    yield_mean = np.array([np.mean(x) for x in yield_history])
    yield_risk = yield_std / (yield_mean + 1e-18)

    # Calculate volatile asset risk
    volatile_asset_risk = {key: 0 for key in fei_deposit_variables}
    volatile_asset_risk_override = {
        "fei_liquidity_pool_user_deposit": volatile_asset_risk_metric,
        "fei_money_market_user_deposit": volatile_asset_risk_metric,
    }
    volatile_asset_risk_intersection = (
        volatile_asset_risk.keys() & volatile_asset_risk_override.keys()
    )
    volatile_asset_risk.update(
        {
            update_key: volatile_asset_risk_override[update_key]
            for update_key in volatile_asset_risk_intersection
        }
    )
    volatile_asset_risk = np.array(list(volatile_asset_risk.values()))

    # Calculate risk vector
    risk_vector = 1 + volatile_asset_risk + yield_risk

    assert yield_vector.sum() > 0, "zero or negative yield vector sum"
    assert risk_vector.sum() > 0, "zero or negative risk vector sum"

    # Calculate target weights: weight = yield / (1 + risk)
    target_weights = yield_vector / risk_vector

    assert target_weights.sum() >= 0, "zero or negative weights sum"

    normalised_target_weights = target_weights / target_weights.sum()

    return {
        "capital_allocation_target_weights": normalised_target_weights,
    }


def array_sum_threshold_check(array, total, threshold):
    """## Array Sum Threshold Check
    A function to check that the sum of a Numpy `array` is less than some `total` value within some `threshold`
    """
    return np.abs(sum(array) - total) < threshold


def policy_fei_capital_allocation_rebalancing(
    params: Parameters, substep, state_history, previous_state
):
    """## User-circulating FEI Capital Allocation Rebalancing Policy
    A Policy that takes the target Capital Allocation weights calculated in `policy_fei_capital_allocation_endogenous_weight_update(...)`,
    calculates the current Capital Allocation weights, and performs the necessary rebalancing operations to try meet the target.
    """
    # Parameters
    dt = params["dt"]
    rebalance_duration = params["capital_allocation_rebalance_duration"]
    fei_deposit_variables = params["capital_allocation_fei_deposit_variables"]

    # State Variables
    target_weights: np.ndarray = previous_state["capital_allocation_target_weights"]
    fei_price = previous_state["fei_price"]

    # Calculate current weights
    fei_deposits = [copy.deepcopy(previous_state[key]) for key in fei_deposit_variables]
    current_deposit_balances = np.array([deposit.balance for deposit in fei_deposits])
    total_fei = sum(current_deposit_balances)
    current_weights = np.array([balance / total_fei for balance in current_deposit_balances])

    assert array_sum_threshold_check(current_deposit_balances, total_fei, 1e-3), "Summation error"
    assert array_sum_threshold_check(current_weights, 1, 1e-3), "Percentage calculation error"
    assert array_sum_threshold_check(current_weights, 1, 1e-3), "Percentage calculation error"

    # Calculate deltas for rebalancing
    rebalance_rate = np.sqrt(dt / rebalance_duration)

    (
        rebalance_matrix,
        total_fei_deposit_balance_change,
    ) = compute_capital_allocation_rebalance_matrix(
        target_weights, current_weights, total_fei, rebalance_rate
    )

    for (row, column), value in filter(lambda x: x != 0, np.ndenumerate(rebalance_matrix)):
        # Perform balance transfer
        from_index = column if value > 0 else row
        to_index = row if value > 0 else column

        transfer_amount = min(abs(value), fei_deposits[from_index].balance)

        fei_deposits[from_index].transfer(
            to=fei_deposits[to_index],
            amount=transfer_amount,
            from_asset_price=fei_price,
            to_asset_price=fei_price,
        )

    new_capital_allocation = [deposit.balance for deposit in fei_deposits]

    # Check constraints
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
        logging.debug(
            f"Capital allocation rebalancing: movement of {log_rebalance_remainder} FEI unallocated"
        )

    assert array_sum_threshold_check(new_capital_allocation, total_fei, 1e-3), "Summation error"

    return {
        "capital_allocation_rebalance_matrix": rebalance_matrix,
        "capital_allocation_rebalance_remainder": rebalance_remainder,
        # FEI User Deposit updates
        **{key: fei_deposits[index] for index, key in enumerate(fei_deposit_variables)},
        **(
            liquidity_pools.update_fei_liquidity(
                previous_state,
                dict(zip(fei_deposit_variables, fei_deposits))["fei_liquidity_pool_user_deposit"],
            )
            if "fei_liquidity_pool_user_deposit" in fei_deposit_variables
            else {}
        ),
    }


def compute_capital_allocation_rebalance_matrix(
    target_fei_allocation,
    current_fei_allocation,
    total_fei,
    rebalance_rate=1,
):
    """## Compute Capital Allocation Rebalance Matrix
    A function that computes the User Deposit rebalancing operations necessary to
    meet the target Capital Allocation.
    """
    # Calculate delta matrix - amounts to rebalance and to disaggregate
    allocation_pct_change = target_fei_allocation - current_fei_allocation
    total_fei_deposit_balance_change = rebalance_rate * allocation_pct_change * total_fei

    number_of_deposits = len(total_fei_deposit_balance_change)
    deposit_incidence_matrix = generate_constrained_incidence_matrix(number_of_deposits)

    total_balance_changes = np.append(total_fei_deposit_balance_change, np.array(0))
    # Solve Ax = b st 1Tx == 0 (conservation constraint)
    deltas = np.linalg.pinv(deposit_incidence_matrix) @ total_balance_changes

    assert np.allclose(
        np.dot(deposit_incidence_matrix, deltas),
        total_balance_changes,
        atol=1e-3,
    ), "Linear algebra solution is above imprecision tolerance"

    rebalance_matrix = populate_delta_triangular_matrix(deltas, number_of_deposits)

    return rebalance_matrix, total_fei_deposit_balance_change


def populate_delta_triangular_matrix(d, w_size):
    """## Populate Delta Triangular Matrix
    A function that populates a lower triangular matrix, sometimes referred to as a `triu` function.
    """
    D = np.zeros((w_size, w_size))

    k = 0
    for i in range(len(D)):
        for j in range(len(D)):
            if i < j:
                D[i][j] = d[k]
                k += 1

    return D


def generate_constrained_incidence_matrix(n_deposits):
    """## Generate Constrained Incidence Matrix
    A function that calculates the incidence matrix for the graph of User Deposits,
    in order to be able to calculate the transactions needed to rebalance towards the target Capital Allocation.
    """
    G = nx.complete_graph(n_deposits)
    A = (nx.incidence_matrix(G, oriented=True).toarray() * -1).astype(int)

    # NOTE Fixes NetworkX rendition of 2-deposit adjacency matrix generation
    if A.shape[1] == 1:
        A = np.hstack([A, np.zeros((2, 1))])

    constrained_incidence_matrix = np.vstack([A, np.ones((1, A.shape[1]))])
    return constrained_incidence_matrix
