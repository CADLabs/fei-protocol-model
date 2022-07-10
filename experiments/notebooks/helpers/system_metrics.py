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


def calculate_VaR_run(df, n_run, alpha, n_timesteps, t_start, t_end):
    pcv_ret = df.query('run==@n_run')['total_pcv'].pct_change()
    pcv_final_val = df.query('run==@n_run')['total_pcv'].iloc[-1]
    q = pcv_ret.quantile(1-alpha)
    # see https://www0.gsb.columbia.edu/faculty/pglasserman/B6014/var-d.pdf
    # for n-day var simplifying assumption which allows for generalization
    VaR_n = abs(pcv_final_val * q)*np.sqrt(n_timesteps)
    
    return VaR_n, q


def calculate_VaR_subset(df, n_subset, alpha, n_timesteps, t_start, t_end):
    VAR = []
    
    df_ = df.query("subset==@n_subset")
    for run in df_['run'].value_counts().index:
        var, q = calculate_VaR_run(df_, run, alpha, n_timesteps, t_start, t_end)
        
        VAR.append((n_subset, var, q))
    
    return pd.DataFrame(VAR, columns=[x+'_'+str(n_timesteps) for x in ['subset', 'VaR', 'q']])


def calculate_VaR(df, alpha, n_timesteps, t_start, t_end):
    L = []
    
    for subset in df['subset'].value_counts().index:
        VaR_subset = calculate_VaR_subset(df, subset, alpha, n_timesteps, t_start, t_end)
        L.append(VaR_subset)
        
    return pd.concat(L, axis=0).reset_index(drop=True)


def calculate_VaR_n(df, alpha, timestep_range, t_start, t_end):
    U, L = [], []
    
    for t in range(timestep_range):
        L.append(calculate_VaR(df, 0.95, t+1, t_start, t_end))
        U.append(t+1)
        
    return dict(zip(U, L))


def calculate_VaR_summary_stats(df, n_timesteps):
    L = []
    colnames = []
    for subset in df['subset'+'_'+str(n_timesteps)].value_counts().index:
        L.append(df.query('subset'+'_'+str(n_timesteps)+'==@subset').describe())
        colnames += [colname+'_'+str(subset) for colname in df.columns]
    
    VAR_info = pd.concat(L, axis=1)
    VAR_info.columns = colnames
    VAR_info = VAR_info.drop(index=['count'])
    return VAR_info


def calculate_VaR_threshold_probability(df, n_timesteps, threshold):
    L = []
    colnames = []
    for subset in df['subset'+'_'+str(n_timesteps)].value_counts().index:
        df_ = (df.query('subset'+'_'+str(n_timesteps)+'==@subset')['q_'+str(n_timesteps)] <= threshold).astype(int)
        emp_probability = df_.sum()/len(df_)
        L.append(emp_probability)
        colnames.append('q_'+str(n_timesteps)+'_'+str(subset))
    return dict(zip(colnames,L))
        
