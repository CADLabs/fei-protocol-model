# +
# generic state variable summary stats
# -
import numpy as np
import pandas as pd
import itertools
from scipy.stats import norm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

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
        df_ = (df.query('subset'+'_'+str(n_timesteps)+'==@subset')['q_'+str(n_timesteps)] >= threshold).astype(int)
        emp_probability = df_.sum()/len(df_)
        L.append(emp_probability)
        colnames.append('q_'+str(n_timesteps)+'_'+str(subset))
    return dict(zip(colnames,L))

def get_weight_evolution(df, subset):
    df_ = pd.DataFrame(
            df.query('subset==@subset')['capital_allocation_target_weights'].to_list(),
        )
    
    df_.index = df.query('subset==@subset')['timestamp']
    return df_

def get_weight_evolution_average(df, subset, use_cols):
    
    balances = pd.DataFrame(df.query('subset==@subset')["capital_allocation_target_weights"].to_list(),
             columns=use_cols)
    
    df_ = df.query('subset==@subset')[['timestep']].reset_index()
    
    df_ = pd.concat([df_, balances], axis=1).set_index('timestamp')
    
    df_ = df_.groupby('timestep').mean()
    
    df_.index = df.query('subset==@subset and run==1')['timestamp']
    
    return df_

def get_averages_by_subset(df, variables):
    L = []
    for i in df['subset'].value_counts().index:
        df_ = df.query('subset == @i')
        df_ = df_[['timestep', 'subset', 'run'] + variables].groupby('timestep').mean()
        df_.index = df.query('subset==@i and run==1')['timestamp']
        L.append(df_)
        
    return pd.concat(L, axis=0)
        
### KPI related

def compute_vol(x):
    return x.pct_change().std()

def compute_max(x):
    return x.max()

def compute_min(x):
    return x.min()

def compute_final_val(x):
    return x.iloc[-1]

def compute_mdd(x):
    window = 30

    rolling_max = x.rolling(window).max()
    dd = x/rolling_max - 1.0
    
    mdd = dd.rolling(window).min()
    return mdd.min()

def get_fn_dict():
    fn_list = [compute_vol, compute_max, compute_min, compute_final_val, compute_mdd]
    fn_names = ['volatility', 'max', 'min', 'final value', 'max dd']
    fn_dict = dict(zip(fn_names, fn_list))

    return fn_dict

def generate_emp_distribution_kpi(fn, df, variable, start=None, end=None):
    L = dict()
    for i in list(df['subset'].value_counts().index):
        V = dict()
        for j in list(df['run'].value_counts().index):
            x = df.query('run==@j and subset==@i')[variable].iloc[start:end]
            v = fn(x)
            V[j] = v
            
        L[i] = V
        
    return pd.DataFrame(L)

def compute_metric_set_for_variable(df, fn_dict, variable, start=None, end=None):
    L = dict()
    for fn_name, fn in fn_dict.items():
        metric_avg = generate_emp_distribution_kpi(fn, df, variable, start=start, end=end).mean(axis=0)
        L[fn_name] = metric_avg
        
    return pd.DataFrame(L)

def gen_norm_rv(n, mu, sigma):
    return norm.rvs(loc=mu, scale=sigma, size=1, random_state=n)[0]


def get_average_CAM_deposits(df, subset, use_cols):
    df_ = df.query('subset==@subset')[['timestep'] +use_cols].groupby('timestep').mean()
    df_.index = df.query('subset==@subset and run==1').index
    df_['timestamp'] = df_.index
    
    return df_

def get_final_deposit_avgs(df, use_cols, subset):
    final_ts_avgs = get_averages_by_subset(df, use_cols).query('subset==@subset').iloc[-1]
    final_ts_avgs = final_ts_avgs[2:]
    final_ts_avgs = pd.DataFrame(final_ts_avgs).reset_index()
    final_ts_avgs.columns = ['deposit', 'value']
    
    return final_ts_avgs

def get_state_variable_emp_dist(df, variable, timestep=-1):
    
    S = dict()
    
    for subset in df['subset'].unique():
        
        D = dict()

        for run in df['run'].unique():
            sv = df.query("subset==@subset and run==@run")[variable].iloc[timestep]

            D[run] = sv
                    
        S[subset] = D
        
    return pd.DataFrame(S).T

def get_deposit_proportion(df, variable, timestep=-1):
    
    S = dict()
    
    for subset in df['subset'].unique():
        
        D = dict()

        for run in df['run'].unique():
            final_deposit_size = df.query("subset==@subset and run==@run")[variable].iloc[timestep]
            final_fei_u = df.query("subset==@subset and run==@run")['total_user_circulating_fei'].iloc[timestep]

            D[run] = final_deposit_size / final_fei_u
                    
        S[subset] = D
        
    return pd.DataFrame(S).T

def get_empirical_probability_for_deposit(proportions_df, threshold, var_type='deposit'):
    emp_probs = (proportions_df > threshold).sum(axis=1)/proportions_df.shape[1]

    if var_type == 'deposit':
        
        for i in range(len(emp_probs)):
            print('This deposit has a', 100*emp_probs[i], '% probability of reaching an allocation of',
                  100*threshold, '%, for subset '+str(i))
            
    if var_type == 'state_var':
        
        for i in range(len(emp_probs)):
            print('This state variable has a', 100*emp_probs[i], '% probability of reaching a value of',
                  threshold, ', for subset '+str(i))

def get_variable_mean_difference(df, variable):
    
    S = dict()
    
    for (s1, s2) in itertools.product(df['subset'].unique(), df['subset'].unique()):
        
        if s1 < s2:
            
            D = dict()

            for run in df['run'].unique():
                mu_diff = (df.query('subset==@s1 and run==@run')[variable].mean()
                 - df.query('subset==@s2 and run==@run')[variable].mean())
                D[run] = mu_diff

            S[str(s1)+'_'+str(s2)] = D
        
    return pd.DataFrame(S).T

def get_variable_difference_emp_prob(md_df):
    df_ = md_df > 0
    df_ = df_.sum(axis=1)/md_df.shape[1]
    
    return df_

def print_emp_prob_message(vd_prob):
    
    for i in range(len(vd_prob)):
        subsets = vd_prob.index[i].split('_')
        print('The empirical probability that subset', subsets[0], 'is greater on average than subset',
               subsets[1], 'is', vd_prob.values[i])


def generate_synthetic_fsr_expenditure(df, syn_rate):
    synthetic_fsr_expenditure = df["fei_savings_user_deposit_balance"] * syn_rate / 365
    return synthetic_fsr_expenditure

def get_synthetic_protocol_profit(df, syn_rate):
    
    D = pd.DataFrame()
        
    for subset in df['subset'].unique():
        
        D2 = pd.DataFrame()
        
        for run in df['run'].unique():
            
            df_ = df.query("run==@run and subset==@subset")
            
            protocol_profit = (df_['protocol_revenue'] -
             generate_synthetic_fsr_expenditure(df_, syn_rate))
            
            protocol_profit.name = 'protocol_profit'
            
            subset_ = df_['subset']
            run_ = df_['run']
            timestamp_ = df_['timestamp']
            timestep_ = df_['timestep']

            sv = pd.concat([timestamp_, timestep_, subset_, run_, protocol_profit], axis=1)
            
            D2 = pd.concat([D2, sv], axis=0)
            
        D = pd.concat([D, D2], axis=0)
        
    return D

def get_first_negative_pr_timestep(df):
    
    D = dict()
    
    for subset in df['subset'].unique():
        
        S = dict()
        
        for run in df['run'].unique():
            
            df_ = df.query("run==@run and subset==@subset")
            
            first_negative_timestep = df_['protocol_profit'].lt(0).idxmax()
            
            S[run] = first_negative_timestep
            
        D[subset] = S
        
    return pd.DataFrame(D).T


def get_emp_prob_timestep(ts_df, ts):
    df_ = ts_df < pd.Timestamp(ts)
    emp_probs = df_.sum(axis=1)/df_.shape[1]

    for i in range(len(emp_probs)):
        print('Protocol profit has a', 100*emp_probs[i], '% probability of first attaining a budget deficit by time:',
                ts, ', for subset '+str(i))

# PCV at RISK 

def calculate_VaR(df, state_variable, alpha, timesteps):
    results = pd.DataFrame()

    for simulation in df.simulation.unique():
        df_simulation = df.query("simulation == @simulation")
        for subset in df_simulation.subset.unique():
            df_subset = df_simulation.query("subset == @subset")
            for run in df_subset.run.unique():
                df_run = df_subset.query("run == @run")

                returns = df_run[state_variable].pct_change()
                final_value = df_run[state_variable].iloc[-1]
                q = returns.quantile(1 - alpha)
                value_at_risk = abs(final_value * q) * np.sqrt(timesteps)

                result = pd.DataFrame({'simulation': [simulation], 'subset': [subset], 'run': [run], 'VaR': [value_at_risk], 'q': [q]})
                results = pd.concat([results, result])

    return results.reset_index(drop=True)


def calculate_VaR_threshold_probability(df, threshold):
    results = pd.DataFrame()
    
    for subset in df.subset.unique():
        df_subset = df.query("subset == @subset")
        
        df_threshold = df_subset["q"] >= threshold
        probability = df_threshold.sum() / len(df_threshold)
        
        result = pd.DataFrame({'subset': [subset], 'threshold': [threshold], 'probability': [probability]})
        results = pd.concat([results, result])
    
    return results.reset_index(drop=True)

def get_data_to_plot(df, df_var, run, subset):
    pcv_ret = df.query('run == @run and subset == @subset')['total_pcv'].pct_change()
    var = df_var.query('run == @run and subset == @subset')['VaR'].iloc[0]
    q = df_var.query('run == @run and subset == @subset')['q'].iloc[0]
    
    return pcv_ret, var, q

def plot_VaR_hist(df_var, variable):
    df_ = pd.concat(
        [
            df_var.query('subset==0')[variable].reset_index(drop=True),
            df_var.query('subset==1')[variable].reset_index(drop=True),
        ], axis=1)

    df_.columns = [variable+'_0', variable+'_1']
    
    return df_.hist()

def compute_means(df, variable):
    
    n_runs = len(df['run'].value_counts())
    
    mu1, mu2 = [], []
    
    for run in range(1,n_runs+1):
        diff = (df.query('subset == 0 and run==@run')[variable] -
                df.query('subset == 1 and run==@run')[variable])
        
        s1 = df.query('subset == 0 and run==@run')[variable]
        s2 = df.query('subset == 1 and run==@run')[variable]
        
        mu1.append(s1.mean())#/s1.std())
        mu2.append(s2.mean())#/s2.std())
        
    return np.array(mu1), np.array(mu2)

def compute_sr(df, variable):
    
    
    n_runs = len(df['run'].value_counts())
    
    mu1, mu2 = [], []
    
    for run in range(1,n_runs+1):
        diff = (df.query('subset == 0 and run==@run')[variable] -
                df.query('subset == 1 and run==@run')[variable])
        
        r1 = df.query('subset == 0 and run==@run')[variable]#.pct_change()
        r2 = df.query('subset == 1 and run==@run')[variable]#.pct_change()
        
        mu1.append(r1.mean()/r1.std())
        mu2.append(r2.mean()/r2.std())
        
    return np.array(mu1), np.array(mu2)


def make_PCVaR_plot(df, df_var, max_rows):
    fig = make_subplots(rows=max_rows, cols=len(df['subset'].unique()),
                        x_title='PCV Daily Returns - Left: Policy 0, Right: Policy 1',
                        y_title='Number of Observations',
                       )

    for subset in df['subset'].unique():
        for run in range(1,max_rows+1):

            pcv_ret, var, q = get_data_to_plot(df, df_var, run, subset)

            fig.add_trace(
                px.histogram(pcv_ret, x="total_pcv", nbins=100).data[0],
                row=run, col=subset+1)

            fig.add_vline(x=q, row=run, col=subset+1)


    fig.update_layout(
        title="Histogram of PCV Returns for Runs and Policy Settings",
        autosize=False,
        #width=1200,
        height=1600,
    )

    fig.show()


