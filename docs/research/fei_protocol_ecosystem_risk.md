# Fei Protocol Ecosystem Risk

Risk analysis is generally understood as occurring as a result of market data becoming observable. Provided our model effectively simulates such data, there is a stronger case for post-output analysis than in-model. NOTE: Observability is at the level of the model. State variables that are modelled to stand in for unobservable real-life aspects of the FEI ecosystem can have associated risk gauges, but will not have real-world data to be checked against.

Fei Protocol and Ecosystem Risk can be broadly examined under three aspects:
1. Generalized Tail Risk Analysis - for model-observable processes whose values over time can be analyzed as an empirical probability distribution.
2. Mechanism-Specific Risk Analysis - in which useful / nontrivial observed relationships as a result of mechanism-specific state variables are quantified as metrics.
3. Policy-Driven Risk Analysis - in which the isolated or combined effects of monetary policy levers are gauged and causally linked to key system KPIs.

Each of these aspects assumes a different importance based on the existence of independent stochastic drivers in the FEI Protocol model versus trajectories - ex: price processes.

## Examples

1. $VaR(\alpha)$ for the Volatile Asset in PCV and associated quantile-gauged tail risk for derivative processes such as Total Volatile PCV value with rebalancing and Value of Accrued PCV yield in volatile deposits. This is most useful when stochastic volatile asset prices drive the model.
2. Lending Market utilization rate delta under different FEI Savings rate settings. Insolvency of overall protocol debt under different FEI savings rate settings. More generally, any metric derived from differences in parameter sweeps.
3. Delta of PCV deposit capital efficiency from net in/outflows as a result of different PCV rebalancing stable backing target values. (Or different rebalancing policies alltogether)

Volatility of difference of PCV yield and fixed SR and consequent volatility of the yield bearing FEI minting cap.


## A) Generalized Tail Risk Analysis
In Quantitative Risk Management, one of the most common sets of metrics for evaluating 'risk' is to associate the concept of risk to volatility. In particular, once returns on an asset or a portfolio of assets are available, statistical analyses can be performed on their distribution. Here, we can consider the PCV to be a weighted portfolio of a volatile and a stable asset.

More generally, any observable process in the model which exhibits a stochastic behavior, either because explicitly modelled as a process, or as a result of system dynamics - can be an object of statistical analysis. Whether the state variable which captures the process can be used directly or must first be transformed is dependent on what the state variable encodes.

## B) Mechanism-Specific Risk Analysis
Here, we relax the association between risk and volatility, and are more interested in how state variables which encode the dynamics which arise as a result of specific mechanisms can point to potential points of instability in the overall ecosystem. In its most basic (but arguably effective) form this involves the creation of risk metrics as the difference between key state variables across different settings of parameters in a sweep. 

Without invoking state variable transformations, a simple ancillary is the correlation matrix constructed for all values of a state variable for each setting in a parameter sweep.

## C) Policy-Driven Risk Analysis
This is the analysis in which we look at the effects of applying specific monetary policy levers. Since policies ultimately inform mechanisms, this analysis assumes somewhat of a similar flavor as the prior one, in terms of constructing and evaluating system metrics. Complex, multi-mechanism derived metrics such as proxies for FEI demand can be construed as being part of this risk analysis block.

In practice, difference metrics here should be constructed from parameter sweeps on policy inputs rather than process or mechanism parameters.

## Risk Analyses Per Differential Specification PSUB

Here we go over where each of the three prongs of the risk analysis framework can come into play, at the level of state variables

### Price Processes

- A) Summary Statistics(*see appendix) of Volatile Asset price, Stable Asset price. More interesting for stable asset if a jump process for tail event occasional de-pegs is introduced.
- B) None
- C) None

### FEI-X Liquidity Pool & Rebalancing

- A) Summary statistics of the TVL, FEI Source/Sink, and IL processes
- B) Metrics for delta in FEI Source/Sink, TVL, and cumulative FEI redemptions under different price trajectories
- C) Metrics for delta in LP PCV Deposit size under different stable backing targets from PCV rebalancing

### FEI-X Money Market

- A) Summary statistics for lending rate, APR, and utilization processes
- B) Metrics for delta in lending and utilization rate under different price trajectories
- C) Metrics for delta in lending and utilization rate under different levels of FEI Savings Rate

Additionally: Metrics for Lending Market Insolvency, Liquidations at Risk, and Borrower usage (informs FEI demand). See [Gauntlet](https://governance.aave.com/t/gauntlet-market-risk-primer/2097).

### User-circulating FEI

- A) Summary statistics for user circulating fei, fei mint/redemption processes
- B) Metrics for delta in user circulating fei under different external processes (price trajectories, lending market rates)
- C) Metrics for delta in user circulating fei under different policies: FEI savings rate, PCV rebalancing stable backing ratio targets, etc (informs FEI demand)

### FEI Savings Deposit

- A) Summary statistics for user FEI savings deposit size, deposit cap, lockup, and idle FEI processes
- B) Metrics for delta in idle and yield bearing FEI under different external processes (price trajectories, lending market rates)
- C) Metrics for delta in idle and yield bearing FEI under different policies: FEI savings rate (informs FEI demand)

Additionally: FEI savings rate opportunity cost and circulation related metrics (Danilo's WIP TBC here)

### PCV Yield
- A) Summary statistics PCV yield amounts and yield value processes
- B) Metrics for relating PCV yield amounts and deposit amounts under different external processes (price trajectories, lending market rates) for all PCV deposit types
- C) Metrics for relating PCV yield amounts and deposit amounts under different policies: specifically FEI rebalancing under different stable backing targets and various approaches for integrating yield accrual

### PCV Management
- A) Summary statistics for PCV amount and value processes, in individual deposits and in aggregation
- B) Metrics for relating PCV yield amounts and deposit amounts under different external processes (price trajectories, lending market rates) for all PCV deposit types
- C) Metrics for relating PCV amounts under different policies: specifically FEI rebalancing under different stable backing targets, FEI savings rate policy, PCV yield policy, FEI money market deployment policy

Additionally: Metrics and tail risk analysis for mechanism-level contribution to protocol debt, collateral ratio solvency.

### FEI Demand Metric Construction and Comparison

FEI Demand Metric(s) will likely involve inputs from multiple signals or indeed multiple metrics, especially those constructed to inform aggregate behavior in reaction to supply - ex: utilization rate from MM block + locked up FEI deposit from user-circulating block + FEI released in market from LP rebalancing block.

It may be of interest to compute metrics for FEI demand with downstream effects and interactions between FEI ecosystem parts toggled on and off (once implemented) in order to understand to what extent metrics for FEI demand are affected by the underlying mechanisms being in place (1st order) vs their downstream interaction (2nd order).

# Appendix:

**Value at Risk (VaR):** It estimates how much a set of investments might lose (with a given probability), given normal market conditions, in a set time period such as a day. For a given portfolio, time horizon, and probability p, the p VaR can be defined informally as the maximum possible loss during that time after excluding all worse outcomes whose combined probability is at most p. p-VaR is defined such that the probability of a loss greater than VaR is (at most) (1-p) while the probability of a loss less than VaR is (at least) p. A loss which exceeds the VaR threshold is termed a "VaR breach". [Source.](https://en.wikipedia.org/wiki/Value_at_risk)

For example, if the PCV portfolio has a one-day 95% VaR of $1 million, that means that there is a 5% probability that the portfolio will fall in value by more than $1 million over a one-day period if there is no trading. [Source.](https://en.wikipedia.org/wiki/Value_at_risk)

**Expected Shortfall:** The "expected shortfall at q% level" is the expected return on the portfolio in the worst q% of cases. ES estimates the risk of an investment in a conservative way, focusing on the less profitable outcomes. It is calculated for a given quantile-level q, and is defined to be the mean loss of portfolio value given that a loss is occurring at or below the q-quantile. [Source.](https://en.wikipedia.org/wiki/Expected_shortfall)

##### PCV Summary Statistics

We can also compute simple summary statistics from the distribution of returns on the PCV Portfolio:
- historical volatility
- max drawdown
- sharpe ratio
- sortino ratio

The evolution of these metrics based on a rolling window over the duration of the simulation can act as a stand-in for a dynamic risk score.

##### State Variable Correlations

In general, it may be useful to compute a correlation matrix for all state variables which play a role in determining future system state: ex - informing FEI demand. Correlations can be computed once as a result of simulation outputs or on a rolling basis, as to be able to inspect the evolution of correlations themselves.

Whilst analysis of correlations is not a formal parameter hypothesis testing procedure, one may informally gauge the simulated strength of relationships, and even compare to real world data, in order to validate assumptions.

**Examples:**
- Direct Minting/Redemption via PSMs
- Stable and Volatile asset pool TVLs
- Stable and Volatile asset pool imbalances
- Money Market Utilization rate
- User Circulating FEI
- Collateral Ratio

Can have their correlations computed against ETH price and amongst each other. Strength/Weakness in correlated pairs may help examine magnitude of downstream effects.

#### FEI Price / Arbitrage Extensions

Relaxing the perfect arbitrage assumption (FEI at $1), additional arbitrage-related risk analyses become possible.

Although departing from traditional portfolio analysis we can also look at things like the distribution of deviations from the peg of FEI price, once FEI price is modelled as a stochastic process whose stationarety around $1 is maintained as a result of arbitrage actions.

Possible extensions include custom definitions of X-at-risk where X can stand in for a desired quantity, such as peg deviation.
