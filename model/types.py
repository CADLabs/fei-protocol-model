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
APR = float

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
    """
    A PCV Deposit class.

    Private variables with prefix _ should only be set directly in model configuration (e.g. initial state)
    and be set using appropriate methods during runtime. This ensures the right assertions are made, and makes
    it easy to check where "unsafe" updates are made.
    """

    asset: str
    """Asset held in the deposit e.g. 'ETH'"""
    deposit_type: str
    """Type of PCV Deposit e.g. 'liquidity_pool', 'money_market', 'idle', 'yield_bearing'"""
    _balance: Union[FEI, StableAssetUnits, VolatileAssetUnits] = Uninitialized
    _asset_value: USD = Uninitialized
    _yield_accrued: Union[FEI, StableAssetUnits, VolatileAssetUnits] = 0.0
    _yield_value: USD = 0.0
    _yield_rate: APR = Uninitialized

    def deposit(self, amount, asset_price):
        """
        Deposit an amount, in asset units, into PCV Deposit balance,
        and update the asset value.
        """
        assert amount >= 0, "Amount must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance += amount
        self._asset_value = self._balance * asset_price

        return self

    def withdraw(self, amount, asset_price):
        """
        Withdraw an amount, in asset units, from the PCV Deposit balance,
        and update the asset value.
        """
        assert amount >= 0, "Amount must be a positive value"
        assert amount <= self.balance, "Amount must be less than balance"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance -= amount
        self._asset_value = self._balance * asset_price

        return self

    def transfer(self, to, amount, asset_price):
        """
        Transfer an amount from the balance of one PCV Deposit to the balance of another.
        """
        self.withdraw(amount, asset_price)
        to.deposit(amount, asset_price)

        return self, to

    def set_balance(self, balance, asset_price):
        """
        Directly set the balance for the PCV Deposit,
        and update the asset value.
        """
        assert balance > 0, "Balance must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance = balance
        self._asset_value = self._balance * asset_price

        return self

    def accrue_yield(self, period_in_days, asset_price):
        """
        Accrue yield on balance to yield_accrued based on yield_rate with simple interest.

        Args:
            period_in_days (int):   Requires period_in_days to convert annualized yield_rate to period yield rate
            asset_price (float):    Requires asset_price to update the yield_value

        Returns:
            The PCVDeposit instance
        """
        assert asset_price >= 0, "Asset price must be a positive value"
        assert period_in_days >= 0, "Period in days must be a positive value"

        self._yield_accrued += self._balance * (self._yield_rate * period_in_days / 365)
        self._yield_value = self._yield_accrued * asset_price

        return self

    def accrue_yield_compounded(self, period_in_days, asset_price):
        """
        Accrue yield on balance to yield_accrued based on yield_rate with compound interest.

        Args:
            period_in_days (int):   Requires period_in_days to convert annualized yield_rate to period yield rate
            asset_price (float):    Requires asset_price to update the yield_value

        Returns:
            The PCVDeposit instance
        """
        assert asset_price >= 0, "Asset price must be a positive value"
        assert period_in_days >= 0, "Period in days must be a positive value"

        self.accrue_yield(period_in_days, asset_price)
        self.transfer_yield(self, self._yield_accrued, asset_price)

        assert self._yield_accrued == 0
        assert self._yield_value == 0

        return self

    def transfer_yield(self, to, amount, asset_price):
        """
        Transfer an amount from the yield_accrued of one PCV Deposit to the balance of another (can include own balance).
        """
        assert amount <= self._yield_accrued, "Transfer amount greater than yield accrued"
        assert amount >= 0, "Amount must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._yield_accrued -= amount
        to.deposit(amount, asset_price)
        self._yield_value = self._yield_accrued * asset_price

        return self, to

    def update_asset_value(self, asset_price):
        """
        Update the asset value based on the current asset price.
        """
        self._asset_value = self._balance * asset_price

        return self

    @property
    def balance(self):
        """Balance in asset units"""
        return self._balance

    @property
    def asset_value(self):
        """Value of balance in USD"""
        return self._asset_value

    @property
    def yield_accrued(self):
        """Yield accrued on balance (simple or compound interest) in asset units"""
        return self._yield_accrued

    @property
    def yield_value(self):
        """Value of yield accrued in USD"""
        return self._yield_value

    @property
    def yield_rate(self):
        """Annualized yield rate (as APR or simple interest rate without compounding)"""
        return self._yield_rate

    @yield_rate.setter
    def yield_rate(self, new_yield_rate):
        assert new_yield_rate >= 0
        self._yield_rate = new_yield_rate
