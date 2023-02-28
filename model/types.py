"""# Types
Various Python types used in the model
"""

import numpy as np
import sys

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass
from enforce_typing import enforce_types
from typing import Union, List, Dict
from abc import ABCMeta, abstractmethod

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
StateVariableKey = str

# Assets
USD = Union[int, float]
FEI = Union[int, float]
UNI = Union[int, float]
VolatileAssetUnits = Union[int, float]
StableAssetUnits = Union[int, float]

# Weights
CAMWeights = List[FEI]
CAMDeltas = Dict[str, FEI]


@enforce_types
@dataclass(frozen=False)
class Deposit(metaclass=ABCMeta):
    """## Generic Deposit
    A generic Deposit class used for PCV and User Deposits.

    Private variables with prefix _ should only be set directly in model configuration (e.g. initial state)
    and be set using appropriate methods during runtime. This ensures the right assertions are made, and makes
    it easy to check where "unsafe" updates are made.
    """

    asset: str
    """Asset held in the deposit e.g. 'ETH'"""
    deposit_location: str
    """Location of Deposit (used for State Variable naming) e.g. 'liquidity_pool', 'money_market', 'idle', 'yield_bearing'"""
    _balance: Union[FEI, StableAssetUnits, VolatileAssetUnits] = 0.0
    # Asset value must be initialized using appropriate method with asset price argument
    _asset_value: USD = Uninitialized
    _yield_accrued: Union[FEI, StableAssetUnits, VolatileAssetUnits] = 0.0
    # Yield value must be initialized using appropriate method with asset price argument
    _yield_value: USD = Uninitialized
    _yield_rate: APR = 0.0

    @property
    def key(self) -> str:
        return "_".join([self.asset, self.deposit_location, self._deposit_type])

    @property
    @abstractmethod
    def _deposit_type(self) -> str:
        """Private variable, type of Deposit (used for State Variable naming) e.g. 'pcv_deposit' or 'user_deposit'"""
        pass

    def __add__(self, other):
        """
        Add two Deposits of the same type (subclass) and asset together. Returns a new Deposit instance.
        """

        assert (
            self._deposit_type == other._deposit_type
        ), "Can't add two unlike Deposit instances together"
        assert self.asset == other.asset, "Can't add two unlike Deposit instances together"

        from_asset_price = other.asset_value / other.balance if other.balance else 0
        to_asset_price = self.asset_value / self.balance if self.balance else 0

        assert (
            from_asset_price == to_asset_price
        ), "Can't add two Deposit instances with different implicit asset prices"
        assert (
            self.yield_rate == other.yield_rate
        ), "Can't add two Deposit instances with different yield rates"

        return self.__class__(
            asset=self.asset,
            deposit_location=self.deposit_location,
            _balance=self.balance + other.balance,
            _asset_value=self.asset_value + other.asset_value,
            _yield_accrued=self.yield_accrued + other.yield_accrued,
            _yield_value=self.yield_value + other.yield_value,
            _yield_rate=self.yield_rate,
        )

    def deposit(self, amount, asset_price: USD):
        """
        Deposit an amount, in asset units, into Deposit balance,
        and update the asset value.
        """
        assert amount >= 0, "Amount must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance += amount
        self._asset_value = self._balance * asset_price

        return self

    def withdraw(self, amount, asset_price: USD):
        """
        Withdraw an amount, in asset units, from the Deposit balance,
        and update the asset value.
        """
        assert amount >= 0, "Amount must be a positive value"
        assert amount <= self.balance, "Amount must be less than balance"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance -= amount
        self._asset_value = self._balance * asset_price

        return self

    def transfer(self, to, amount, from_asset_price=None, to_asset_price=None):
        """
        Transfer an amount from the balance of one Deposit to the balance of another.

        If either asset_price is not passed as an arugment, it is calculated from the respective Deposit balance and asset_value.
        """
        if not from_asset_price:
            from_asset_price = self.asset_value / self.balance if self.balance else to_asset_price
        if not to_asset_price:
            to_asset_price = to.asset_value / to.balance if to.balance else from_asset_price

        self.withdraw(amount, from_asset_price)
        to.deposit(
            amount * from_asset_price / to_asset_price if to_asset_price else amount,
            to_asset_price,
        )

        return self, to

    def set_balance(self, balance, asset_price: USD):
        """
        Directly set the balance for the Deposit,
        and update the asset value.
        """
        assert balance >= 0, "Balance must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._balance = balance
        self._asset_value = self._balance * asset_price

        return self

    def accrue_yield(self, period_in_days: int, asset_price: USD):
        """
        Accrue yield on balance to yield_accrued based on yield_rate with simple interest.

        Args:
            period_in_days (int):   Requires period_in_days to convert annualized yield_rate to period yield rate
            asset_price (float):    Requires asset_price to update the yield_value

        Returns:
            The yield accrued in the current timestep
        """
        assert asset_price >= 0, "Asset price must be a positive value"
        assert period_in_days >= 0, "Period in days must be a positive value"

        delta_yield_accrued = self._balance * (self._yield_rate * period_in_days / 365)
        self._yield_accrued += delta_yield_accrued
        self._yield_value = self._yield_accrued * asset_price

        return delta_yield_accrued

    def accrue_yield_compounded(self, period_in_days, asset_price: USD):
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

    def transfer_yield(self, to, amount, asset_price: USD):
        """
        Transfer an amount from the yield_accrued of one Deposit to the balance of another (can include own balance).
        """
        assert amount <= self._yield_accrued, "Transfer amount greater than yield accrued"
        assert amount >= 0, "Amount must be a positive value"
        assert asset_price >= 0, "Asset price must be a positive value"

        self._yield_accrued -= amount
        to.deposit(amount, asset_price)
        self._yield_value = self._yield_accrued * asset_price

        return self, to

    def update_asset_value(self, asset_price: USD):
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
        assert new_yield_rate >= 0, new_yield_rate
        self._yield_rate = new_yield_rate


@enforce_types
@dataclass(frozen=False)
class PCVDeposit(Deposit):
    """## PCV Deposit

    Inherits from Deposit class.
    """

    _deposit_type = "pcv_deposit"
    """Implements abstract attribute from Deposit class"""


@enforce_types
@dataclass(frozen=False)
class UserDeposit(Deposit):
    """## User Deposit

    Inherits from Deposit class.
    """

    _deposit_type = "user_deposit"
    """Implements abstract attribute from Deposit class"""
