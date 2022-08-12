# Model Assumptions

During the requirements specification project phase, a number of scoping assumptions were made:

**PCV Assumptions**
- Assume protocol PCV established so bonding curve bootstrapping not relevant
- PCV deposits will be generalised and categorised according to, for example: stable vs. volatile assets, deposit liquidity, yield rate, yield rate volatility, reward asset stability
- Yield opportunities will be generalised, where individual lending markets are not as relevant as their effect on PCV yield

**Open Market Assumptions**
- Peg stability and arbitrage (assume efficient / effective arbitrage, with 1 FEI == 1 USD) to be de-prioritised as they are mostly decoupled from PCV
- Only the effect of FEI-paired unstable asset liquidity pools on FEI supply and PCV will be considered, all PCV movements using other pairs will assume infinitely deep liquidity / not be affected by Fei

**Tribe Mechanism Assumptions**
- Tribe backstop and buybacks for over- and under-collateralisation will not be modelled
- Tribe incentives are being turned off and so are not relevant to modelling timeline
- Tribe Launch and Turbo are longer-term products and so will not be integrated into the model

Additionally, throughout development of the model, a number of mechanism specific assumptions were made which are listed below:

## [State Variables](model/state_variables.py)

Illustrative parameterisation and initial state sourced from data sources such as https://dune.com/llama/Fei-Protocol, https://app.fei.money/ as of 22 June 2022.

## [System Parameters](model/system_parameters.py)

Illustrative parameterisation and initial state sourced from data sources such as https://dune.com/llama/Fei-Protocol, https://app.fei.money/ as of 22 June 2022.

## [Accounting](model/parts/accounting.py)

* PCV assets are categorised as stable or volatile, idle or yield-bearing, and where relevant according to generic mechanisms: e.g. Liquidity Pool, Money Market, etc. rather than specific implementations such as Balancer, Aave, Compound

## [FEI Capital Allocation](model/parts/fei_capital_allocation.py)

* No exogenous flow of FEI into or out of the system due to demand for FEI, other than that required to rebalance Liquidity Pool imbalances
* Idle user-circulating FEI is given a weight of zero in the Capital Allocation Model i.e. we assume all FEI will be allocated to some yield bearing deposit over time. In reality, it could be favourable to hold FEI in certain market conditions or as an interim step between the PSM and allocation to other avenues

## [FEI Savings Deposit](model/parts/fei_savings_deposit.py)

* Although analysis was performed of budgeting of the FEI Savings Rate from protocol revenue, the model does not inflate the FEI supply for payment of yield
* The FEI Savings Deposit supply is not capped as was suggested in the FIP

## [Liquidity Pools](model/parts/liquidity_pools.py)

### Liquidity Provision

We assume that at simulation start, the protocol is the sole liquidity provider, after which the Capital Allocation Model can allocate user FEI for liquidity provision when that makes economic sense according to the user yield and risk weighted allocation.

### Liquidity Pool Source and Sink

* It is initially assumed that all FEI released into the circulating supply from a volatile asset liquidity pool as a result of arbitrage of pool imbalance is immediately redeemed, and any FEI needed to rebalance the pool is minted directly from the PSM.
* Additionally, no transaction volume apart from that required for rebalancing of the liquidity pool is performed and accounted for - as such, the protocol revenue from transaction fees will be lower than can be expected in reality.
* It is assumed that there is an infinite source available for the user capital needed for rebalancing, and that user capital states will as a result not need to be tracked.
* It is assumed that the generic Liquidity Pool is a Uniswap V2 constant product market maker

## [Money Markets](model/parts/money_markets.py)

* It is assumed that there is an infinite source available for the user capital needed for borrowing, and that user capital states will as a result not need to be tracked.

## [PCV Management](model/parts/pcv_management.py)

Currently, PCV movements don't account for trade slippage. Instead, trades are immediately executed assuming 100% efficiency. See [roadmap](ROADMAP.md) for more details about a possible extension.

## [PCV Yield](model/parts/pcv_yield.py)

Yield bearing deposit yield rates are not market dependent, but parameterised as a fixed rate. In reaility, yield rates tend to be market dependent where rates are lower in a market downturn.

## [Peg Stability Module](model/parts/peg_stability_module.py)

* PCV is redeemed directly from the PCV Deposit balance without any consideration for trade efficiency.
* It is assumed that the FEI token price is stable at all times and so the purpose of the PSM is purely for changes in PCV from minting or redemption.

## [Price Processes](model/parts/price_processes.py)

* It is assumed that the FEI token price is always equal to 1 USD
* It is assumed that the Stable Asset price is a Gaussian noise process
* It is assumed that the Volatile Asset price is a Brownian motion process

## [System Metrics](model/parts/system_metrics.py)

...

## [Uniswap](model/parts/uniswap.py)

The simplifying assumption is made that a Uniswap V2 pool is used for all protocol liquidity.
