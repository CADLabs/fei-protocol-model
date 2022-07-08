# +
# generic state variable summary stats
# -

def get_summary_stats_for_simulation_average(df, subset, cols=None):
    
    df_ = df[cols].groupby(['subset','timestep']).mean().reset_index().query('subset==@subset')
    stats_df = df_.describe()
    stats_df.loc['skew'] = df_.skew()
    stats_df.loc['kurtosis'] = df_.kurtosis()
    # TODO: max drawdown & other relevant summary stats here

    return stats_df


def get_summary_stats_for_simulation_run(df, subset, run, cols=None):
    df_ = df[cols].query('subset==@subset and run==@run')

    stats_df = df_.describe()
    stats_df.loc['skew'] = df_.skew()
    stats_df.loc['kurtosis'] = df_.kurtosis()
    # TODO: max drawdown & other relevant summary stats here

    return stats_df


# +
# capital allocation metrics
# -

def normalize_fei_deposits(df, fei_cols):
    
    df_addtl_cols = ['subset', 'run', 'timestep']
    
    norm_df = df[fei_cols].div(df[fei_cols].sum(axis=1), axis=0)
    
    return pd.concat([df[df_addtl_cols], norm_df], axis=1)


def get_fei_deposit_colnames(col_prefixes, col_suffix):
    return [x+col_suffix for x in col_prefixes]


def get_allocations_at_timestep(fei_capital_allocations, fei_cols, run, subset, timestep=-1):
    df_ = fei_capital_allocations.query('run==@run and subset==@subset')[fei_cols].iloc[timestep]
    df_ = pd.DataFrame(df_).reset_index()
    df_.columns = ['index', 'values']
    
    return df_


def get_avg_allocations_at_timestep(fei_capital_allocations, fei_cols, subset, timestep=-1):
    df_ = fei_capital_allocations.query('subset==@subset')[fei_cols].iloc[timestep]
    df_ = pd.DataFrame(df_).reset_index()
    df_.columns = ['index', 'values']
    
    return df_


def get_average_capital_allocations(fei_capital_allocations):
    df_ = fei_balance_capital_allocations.groupby(['subset','timestep']).mean().reset_index()
    df_ = df_.drop(columns='run')
    return df_
