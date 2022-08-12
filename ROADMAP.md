# Model Extension Roadmap

## Account for PCV Movement Efficiency

Currently, PCV movements don't account for trade slippage. Instead, trades are immediately executed assuming 100% efficiency.

As an extension, trades could execute over a period of 1 to 2 weeks accounting for available liquidity or a threshold of slippage in the range of 1-2%.

## Develop a KPI for FEI Demand

One System Goal was to sustainably increase demand for FEI, evaluating FEI demand under different FEI Savings Rates and market conditions.

To properly model FEI Demand, a few updates to the model need to be made:
* Develop a KPI for FEI Demand as a function of State Variables that affect user preferences to mint or redeem FEI e.g. Collateralization Ratio, Stable Backing Ratio, Volatile Asset market conditions, etc. could all affect a user's decision to mint or redeem FEI
* Develop a process to model the FEI Demand driven or Capital Allocation Model yield and risk weighted exogenous flow of FEI from the PSM into user-circulating FEI

## Extend PCV Deposit Types

PCV Deposits are generalised as being stable vs. volatile, idle vs. yield-bearing, and according to specific mechanisms such as the generic Liquidity Pool or Money Market.

As an extension, a more diverse portfolio of PCV assets better representing the on-chain distribution of PCV could be introduced.

## Parameterise Model Directly from On-chain Data

The model's Initial State and System Parameters are currently parameterised by manual Exploratory Data Analysis using `checkthechain` and data sources such as Dune.

As an extension, the model can be initialised directly from on-chain data allowing the model to be used as a digital twin. Additionally, parameters can be tuned using system identification, backtesting, etc.

## Improve Capital Allocation Algorithm

The Capital Allocation Model algorithm currently uses a yield and risk weighted target allocation for movements of user-circulating FEI, meant to encode user preferences. There are currently limited constraints on movements of FEI apart from to maintain sound accounting of FEI.

As an extension, one could introduce mechanism specific user utility functions for FEI allocation, or improve the attributed risk for each deposit type.
