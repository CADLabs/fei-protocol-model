"""
Various Python types used in the model
"""

import numpy as np
import sys

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field
from enum import Enum
from typing import Union

# If Python version is greater than equal to 3.8, import from typing module
# Else also import from typing_extensions module
if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable, NamedTuple
else:
    from typing import List, NamedTuple
    from typing_extensions import TypedDict, Callable


# Generic types
Uninitialized = np.nan
Percentage = float
APY = float

# Simulation types
Timestep = int
Run = int

# Assets
USD = float
FEI = float
VolatileAssetUnits = float
StableAssetUnits = float


@dataclass(frozen=False)
class PCVDeposit:
    asset: str  # name of asset
    deposit_type: str  # name of avenue - one of: liquidity_pool, money_market, idle, yield_bearing
    balance: Union[
        FEI, StableAssetUnits, VolatileAssetUnits
    ] = Uninitialized  # balance in asset units
    asset_value: USD = Uninitialized  # value in USD
    yield_balance: Union[
        FEI, StableAssetUnits, VolatileAssetUnits
    ] = Uninitialized  # accrued balance of yield in asset units
    yield_value: USD = Uninitialized  # accrued value of yield in USD
    yield_rate: APY = Uninitialized  # accrued value of yield in USD


class PCVDepositState:
    fei_idle: PCVDeposit
    stable_asset_idle: PCVDeposit
    volatile_asset_idle: PCVDeposit
