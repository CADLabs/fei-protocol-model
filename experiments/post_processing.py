import pandas as pd
import numpy as np
from radcad.core import generate_parameter_sweep

from model.system_parameters import parameters, Parameters, pcv_deposit_keys, user_deposit_keys
from model.types import PCVDeposit, UserDeposit


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param] for param in set_params} for subset in parameter_sweep]

        for subset_index in df['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value

    return df


def post_process(df: pd.DataFrame, drop_timestep_zero=True, parameters=parameters):
    # Assign parameters to DataFrame
    assign_parameters(df, parameters, [
        # Parameters to assign to DataFrame
        'dt',
        'target_stable_pcv_ratio',
        'target_rebalancing_condition',
        'rebalancing_period',
    ])

    # Set DataFrame index
    df = df.set_index("timestamp", drop=False)

    # Disaggregate PCV Deposit State Variables
    for key in pcv_deposit_keys:
        for variable in PCVDeposit(asset="", deposit_location="").__dict__.keys():
            df[key + ('_' if not variable.startswith('_') else '') + variable] = df.apply(lambda row: getattr(row[key], variable), axis=1)
    # Disaggregate User Deposit State Variables
    for key in user_deposit_keys:
        for variable in UserDeposit(asset="", deposit_location="").__dict__.keys():
            df[key + ('_' if not variable.startswith('_') else '') + variable] = df.apply(lambda row: getattr(row[key], variable), axis=1)
    # Remove Deposit instances from state
    df = df.drop(pcv_deposit_keys + user_deposit_keys, axis=1)

    # Calculate metrics
    df["pcv_yield_ratio"] = df["pcv_yield"] / df["total_user_circulating_fei"] * 365 / df["dt"]

    df["fei_minted"] = np.maximum(df.fei_minted_redeemed, 0)
    df["fei_redeemed"] = np.abs(np.minimum(df.fei_minted_redeemed, 0))
    df["cumulative_fei_minted"] = df["fei_minted"].cumsum()
    df["cumulative_fei_redeemed"] = df["fei_redeemed"].cumsum()

    # Convert decimals to percentages
    convert_to_percentage = [
        'collateralization_ratio',
        'stable_backing_ratio',
        'stable_pcv_ratio',
        'pcv_yield_rate',
        'pcv_yield_ratio'
    ]
    for variable in convert_to_percentage:
        df[variable + '_pct'] = df[variable] * 100

    # Drop the initial state for plotting
    if drop_timestep_zero:
        df = df.drop(df.query('timestep == 0').index)

    # Disaggregate Capital Allocation Target Weights
    capital_allocation_fei_deposit_variables = parameters["capital_allocation_fei_deposit_variables"][0]
    df[[key + '_weight' for key in capital_allocation_fei_deposit_variables]] = df.apply(
        lambda row: list(
            row.capital_allocation_target_weights) if row.capital_allocation_target_weights.size
            else [None for _ in capital_allocation_fei_deposit_variables],
            axis=1, result_type='expand'
    ).astype('float32')

    return df
