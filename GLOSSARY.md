# Model Glossary

A set of technical terminology and common abbreviations used in the model. Wherever possible we avoid the use of jargon, except where those terms are widely used by Fei Protocol. For any other terminology not included here, please see relevant State Variable, System Parameter, Policy, and State Update Function docstrings.

## Assorted
| Term | Common Abbreviation | Description |
| --- | --- | --- |
| Volatile Asset | | Generic volatile PCV asset, equivalent to ETH |
| Stable Asset | | Generic stable PCV asset, equivalent to stablecoin |
| Capital Allocation Model | CAM | User-circulating FEI yield / risk weighted capital allocation model |
| CAM Deposit |  | User Deposit managed by CAM |
| User Deposit | | Location where a user can deposit FEI |
| PCV Deposit | | Location where the protocol can deposit FEI |
| Liquidity Pool | LP | Generic FEI-Volatile liquidity pool |
| Money Market | MM | Generic money market e.g. Aave, Compound |

## Metrics and KPIs

| Term | Common Abbreviation | Description |
| --- | --- | --- |
| Collateral Ratio | CR | `total_pcv / total_user_circulating_fei` |
| Yield Ratio | | `pcv_yield / total_user_circulating_fei` |
| Stable Backing Ratio | | `total_stable_asset_pcv / total_user_circulating_fei` |
| Stable PCV Ratio | | `total_stable_asset_pcv / total_pcv` |
| PCV at Risk	PCVar | | See [Value at Risk](https://www.investopedia.com/articles/04/092904.asp) |
| Utilisation rate | | Money market borrowing / utilisation rate == borrowed / supplied |

## System Parameters

| Term | Common Abbreviation | Description |
| --- | --- | --- |
| Capital Allocation Rebalance Duration	| Rebalance Duration / Velocity | Rebalance over X number of timesteps towards target user-circulating FEI Capital Allocation |
