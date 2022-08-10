# FEI Capital Allocation Model

###### tags: `Fei`

The FEI capital allocation model constitutes the set of dynamics by which user-circulating FEI moves and is allocated to protocol ecosystem avenues. Its dynamics are key in understanding drivers of FEI demand and how it is affected by monetary policy settings.

The FEI capital allocation model is independent of movements of Protocol-Owned FEI.

- $FEI_U = \sum_i(FEI\_Deposit_i)$
    - The user circulating FEI is the sum of all FEI held in FEI-denominated deposit balances

- FEI Denominated Deposits (Avenues for FEI in the Ecosystem):
    - FEI Liquidity Pool
    - FEI Money Market
    - FEI Savings Deposit
    - Idle User FEI

- Mechanisms responsible for idiosyncratically updating deposits:
    - FEI Liquidity Pool: CFMM Policy
    - FEI Money Market: Utilization Rate Policy
    - FEI Savings Deposit: FSD Policy
    - Idle User FEI: Exogenous Mint/Redemption Process

- In order to encode user interaction and user preferences in rebalancing deposits (reallocating FEI to a different avenue) one may cohesively encode system-wide user preferences through global risk-vector weighting of all FEI deposits. The FEI CAM uses exogenous and endogenous (state observation) signals to compute the risk vector - which informs how FEI should be rebalanced across FEI deposits.

- $W_{t, risk} = [w_{t,D_1}, w_{t,D_2}, w_{t,D_3}, w_{t,D_4}], \ s.t. \ W_{t, risk}^T{1} = 1$
    - $w_{t, D_i} = f(y_{t,D_i}, r_{t,D_i} \ | \ W_{(1,\dots,t-1), risk}, S_{D,{(1,\dots,t-1)}})$, function of deposit yield and risk, conditional on history of risk weight vector and history of part of system state relative to deposits $(S_D)$ (can just be prev timestep).
    - $y_{t,D_i} =$ function of deposit yield, endogenous
    - $r_{t,D_i} =$ function of deposit risk, endogenous or exogenous

- Calculate rebalancing across deposits as: $S_{D,{t+1}} \leftarrow rebalance(S_{D,{t}}, W_{t, risk})$. (INTERNAL NOTE: can be specified once implemented).  The portion of the state space ($S_D$) relative to CAM deposits is updated as a result of deposit movements informed by the CAM weights.

**Well-Posedness of weight computation problem**

In an endogenous setting, $w_{t, D_i}$, is specific to each mechanism because $y_{t,D_i}, r_{t,D_i}$ are mechanism-specific. Here, we want to ensure order-of-magnitude weight similarity across idiosyncratic calculation for yield and risk in all concerned mechanisms.

Weight calculation is adjusted by a 'mechanism specific' factors which allow the model  to recommend to moving into and out of deposits. It is desireable to avoid hyper-concentration of FEI in a single deposit type in 'business as usual' settings.

**NOTE:** The IDLE FEI deposit, is always attributed a weight of zero.

#### CAM Weight rebalance decomposition
Once the weight update between two timesteps is computed, we must be able to enact the rebalancing from all FEI deposits in terms of constituent movements between FEI deposits. In other words, we must disaggregate the total percentage change to a FEI deposit into constituent  flows from all other deposits.

The change in weights (what to rebalance overall) is defined as:

$\Delta W_{t+1,t} = W_{t+1, risk} - W_{t, risk} = [\Delta w^{D_1}_{(t+1,t)}, \Delta w^{D_2}_{(t+1,t)}, \Delta  w^{D_3}_{(t+1,t)}, \Delta w^{D_4}_{(t+1,t)}]$

Where:

$\Delta w^{D_i}_{(t+1,t)} = \sum_{j \neq i}\delta^{D_i,D_j}_{(t+1,t)}, \ \delta^{D_i,D_i}_{(t+1,t)} = 0$

In other words, the total difference in weight vector for deposit ($D_i$) the total to rebalance - is the sum of the individual movements between deposit $D_i$ and  all other deposits $D_j$ ('Self-movements' are zero by definition).

We can be exhaustive here:

- Liquidity Pool Deposit:
$\Delta w^{LP}_{(t+1,t)} = \delta^{LP,LP}_{(t+1,t)} + \delta^{LP,MM}_{(t+1,t)} + \delta^{LP,FSD}_{(t+1,t)} + \delta^{LP,IDLE}_{(t+1,t)}$

- Money Market Deposit:
$\Delta w^{MM}_{(t+1,t)} = \delta^{MM,LP}_{(t+1,t)} + \delta^{MM,MM}_{(t+1,t)} + \delta^{MM,FSD}_{(t+1,t)} + \delta^{MM,IDLE}_{(t+1,t)}$

- FEI Savings Deposit:
$\Delta w^{FSD}_{(t+1,t)} = \delta^{FSD,MM}_{(t+1,t)} + \delta^{FSD,LP}_{(t+1,t)} + \delta^{FSD,FSD}_{(t+1,t)} + \delta^{FSD,IDLE}_{(t+1,t)}$

- Idle Deposit:
$\Delta w^{IDLE}_{(t+1,t)} = \delta^{IDLE,MM}_{(t+1,t)} + \delta^{IDLE,FSD}_{(t+1,t)} + \delta^{IDLE,LP}_{(t+1,t)} + \delta^{IDLE,IDLE}_{(t+1,t)}$

Subject to the constraints:
- ${(\delta^W)}^T 1 = \Delta W_{t+1,t}$ and $1^T \Delta W_{(t+1,t)} = 1$

![](https://hackmd.io/_uploads/SyzMdyw35.png)
Causal Loop Diagram for CAM Delta Interaction

**How to compute the $\delta$s?** 
There are two paradigms for computing $\delta$s, **weight disaggregation** and idiosyncratic $\delta$ computation and aggregation into weights. In the current implementation, we deal with the former.

The weight disaggregation problem can be reduced to solving a [system of linear equations](https://en.wikipedia.org/wiki/System_of_linear_equations#Matrix_solution) ($Ax = B$) in which the unknowns, $x$, are the $\delta$s, the coefficient matrix, $A$, is the [incidence matrix](https://mathworld.wolfram.com/IncidenceMatrix.html) of the flow network of deposits (refer to diagram above), and the coefficient vector, $B$, is the CAM weights for the timestep.

Using our notation, $Ax =B$ becomes $A \delta^W_{(t+1,t)} = \Delta W_{t+1,t}$, subject to $1^T\delta^W_{(t+1,t)} = 0$, because there is no minting/redemption of FEI at this stage, just balance transfer between deposits. Solving this every timestep yields the amounts to be transferred between deposits.

In this approach, we are generally able to guarantee an accounting-consistent and feasible set of transfers between deposits, however we do not have control over the indivdual dynamics of transfers between any pair of deposits, as the transfer amounts are obtained as a result of a global calculation.

A potential extension here involves the computation of the yield/risk in relative terms for each deposit pair, such that the entire weighted risk/yield for the deposit satisfies the constraints of being a weight.

### Implemenetation 

The FEI CAM  is not separate from the  FEI Ecosystem Model. It is a specifically purposed model item which allows to cohesively orchestrate movements of user FEI within the ecosystem and have consistent accounting.

The FEI CAM has two main sections (see diffspec for details):
- The FEI Cam PSUBs. Two PSUBs within the model which respectively deal with:
    - CAM  Weight Updates -  calculated in a polocy which takes as input the set of CAM yield rates, historical allocation weights, and concerned FEI  denomiated deposits
    - CAM Rebalancing  - based on the difference in current vs re-calculated weights, generate a set of FEI Deposit 'orders' corresponding to the execution of transfer functions, encompassed as a "deposit rebalance matrix", which is executed in the policy.

## Extension - Backtest Framework for CAM

The FEI Capital Allocation Model can  be used as a backtest tool and as a predictive tool within a digital-twin context of the FEI Ecosystem Model.

- As a backtest tool:
    - Replacing the evolution of the FEI-denominated Deposits subject to CAM rebalancing with the historical time series for the balances of these deposits (or proxies for these), we can perform goodness-of-fit analysis by comparing historical (implied) CAM weights vs simulation-derived CAM weights. Standard time series metrics such as MAE, MAD and RMSE can be used to quantify the observed fit

- As a predictive tool:
    - We can run secondary, experimental type of analysis in which time series forecasting methods (traditional or machine learning  based) are used to predict CAM weights based on historical implied weights, replacing the in-simulation computation with forecast values. (INTERNAL  NOTE: At this stage, the main value prop of the CAM is indeed to derive weights and rebalance via deposit yield & risk calculation, but this remains an option).

**Deposit Balance Observability and CAM**
The CAM can provide unique insights in terms of projecting the deposit balance distribution of FEI in the ecosystem.

EDA can currently be used to calculate observable (implied) weights corresponding to the allocation of FEI in the ecosystem. This is done by calculating the proportion of FEI across on-chain deposits for each abstract Deposit type - Liquidity Pools, Money Markets, and Idle FEI. Aggregating these amounts over individual implementations of each of these deposits and dividing by total FEI supply will yield the weighting of FEI in the ecosystem - which the CAM attempts to simulate.

There is currently no on-chain observability for the FEI savings deposit, however this is a key feature of the FEI Ecosystem Model. As such, by toggling simulation state to enable or disable the FSD as a constituent of the CAM allows to switch between a backtest scenario, and a what-if scenario in terms of seeing how the inclusion of the FSD affects the distribution of deposit balances over the simulation.
