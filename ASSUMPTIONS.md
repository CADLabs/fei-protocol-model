# Model Assumptions (WIP)

During the requirements specification project phase, a number of basic assumptions were made when setting the model scope and purpose:

**PCV**
- Assume protocol PCV established so bonding curve bootstrapping not relevant
- PCV deposits will be generalised and categorised according to, for example: stable vs. volatile assets, deposit liquidity, yield rate, yield rate volatility, reward asset stability
- Yield opportunities will be generalised, where individual lending markets are not as relevant as their effect on PCV yield

**Open market**
- Peg stability and arbitrage (assume efficient / effective arbitrage, with 1 FEI == 1 USD) to be de-prioritised as they are mostly decoupled from PCV
- Only the effect of FEI-paired unstable asset liquidity pools on FEI supply and PCV will be considered, all PCV movements using other pairs will assume infinitely deep liquidity / not be affected by Fei

**Tribe mechanisms**
- Deprioritize modelling of Tribe backstop and buybacks for over- and under-collateralisation
- Tribe incentives are being turned off and so are not relevant to modelling timeline
- Tribe Launch and Turbo are longer-term products of lower priority and so will not be integrated into the model

Additionally, a number of mechanism specific assumptions were made which are listed below:

## [State Variables](model/state_variables.py)

Illustrative parameterisation and initial state sourced from https://dune.com/llama/Fei-Protocol, https://app.fei.money/ as of 22 June 2022.

See [Fei Protocol Model Initial State / Base Case](https://docs.google.com/spreadsheets/d/1LgqKEGRWaooWR6uD5X-vsOx2HBunfcGKJ58mX5rp7Z8) for accounting.

## [System Parameters](model/system_parameters.py)

Illustrative parameterisation and initial state sourced from https://dune.com/llama/Fei-Protocol, https://app.fei.money/ as of 22 June 2022.

See [Fei Protocol Model Initial State / Base Case](https://docs.google.com/spreadsheets/d/1LgqKEGRWaooWR6uD5X-vsOx2HBunfcGKJ58mX5rp7Z8) for accounting.

## [Accounting](model/parts/accounting.py)

## [FEI Capital Allocation](model/parts/fei_capital_allocation.py)

* No minting / redemption due to demand
* Idle is given a weight of zero in Capital Allocation Model i.e. we assume all FEI will be allocated to some yield bearing deposit. In reality, it could be favourable to hold FEI in certain market conditions or as an interim step between minting and redemption.

## [FEI Savings Deposit](model/parts/fei_savings_deposit.py)

* FEI Savings Rate should be budgeted from protocol revenue and either inflate supply or deplete PCV for payment of yield
* Deposit supply is not capped

## [Liquidity Pools](model/parts/liquidity_pools.py)

### Liquidity Provision

We assume that at simulation start, the protocol is the sole liquidity provider, after which the Capital Allocation Model can allocate user FEI for liquidity provision when that makes economic sense.

### Liquidity Pool Source and Sink

It is initially assumed that all FEI released into the circulating supply from a volatile asset liquidity pool as a result of arbitrage of pool imbalance is immediately redeemed, and any FEI needed to rebalance the pool is minted directly from the PSM.

Additionally, no transaction volume apart from that required for rebalancing of the liquidity pool is performed and accounted for - as such, the protocol revenue from transaction fees will be lower than can be expected in reality.

It is assumed that there is an infinite source available for the user capital needed for rebalancing, and that user capital states will as a result not need to be tracked.

## [Money Markets](model/parts/money_markets.py)

It is assumed that there is an infinite source available for the user capital needed for borrowing, and that user capital states will as a result not need to be tracked.

## [PCV Management](model/parts/pcv_management.py)

* PCV assets are categorised as stable or volatile, idle or yield-bearing, and where relevant according to specific mechanisms: e.g. Liquidity Pool, Money Market, etc.
* Dollar-cost Averaging

## [PCV Yield](model/parts/pcv_yield.py)

* Yield bearing deposits not market dependent

## [Peg Stability Module](model/parts/peg_stability_module.py)

* PSM fees are not collected for protocol revenue

## [Price Processes](model/parts/price_processes.py)

## [System Metrics](model/parts/system_metrics.py)

## [Uniswap](model/parts/uniswap.py)
