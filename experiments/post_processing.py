import pandas as pd
from radcad.core import generate_parameter_sweep

from model.system_parameters import parameters, Parameters


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
        'dt'
    ])

    # Drop the initial state for plotting
    if drop_timestep_zero:
        df = df.drop(df.query('timestep == 0').index)

    return df
